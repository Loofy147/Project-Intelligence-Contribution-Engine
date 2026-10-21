import { createServer } from 'node:http';
import { randomUUID, timingSafeEqual } from 'node:crypto';
import { readFile } from 'node:fs/promises';

const ROUTES = new Set(['auto', 'auto/coding', 'auto/smart', 'auto/fast', 'auto/cheap', 'auto/offline']);
const TASKS = new Set(['general', 'coding', 'reasoning', 'research', 'fast', 'cheap', 'offline']);
const HOP_HEADERS = new Set(['connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade', 'content-length', 'content-encoding', 'set-cookie']);

function sendJson(res, status, value, headers = {}) {
  if (res.headersSent) return;
  res.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...headers });
  res.end(JSON.stringify(value));
}

function loadKeys(raw) {
  let values;
  try { values = JSON.parse(raw || ''); } catch { throw new Error('WORKBENCH_API_KEYS_JSON must be valid JSON.'); }
  if (!values || typeof values !== 'object' || Array.isArray(values) || Object.keys(values).length === 0) {
    throw new Error('WORKBENCH_API_KEYS_JSON must map project IDs to API keys.');
  }
  const keys = new Map();
  const unique = new Set();
  for (const [project, key] of Object.entries(values)) {
    if (!/^[a-z0-9][a-z0-9._-]{0,63}$/i.test(project)) throw new Error('Invalid project ID in WORKBENCH_API_KEYS_JSON.');
    if (typeof key !== 'string' || key.length < 32 || /replace|placeholder|change-me/i.test(key)) {
      throw new Error('Each project API key must be a unique secret of at least 32 characters.');
    }
    if (unique.has(key)) throw new Error('Every project must have a distinct API key.');
    unique.add(key);
    keys.set(project, key);
  }
  return keys;
}

function safeEqual(a, b) {
  const left = Buffer.from(a);
  const right = Buffer.from(b);
  return left.length === right.length && timingSafeEqual(left, right);
}

function projectFor(req, keys) {
  const match = /^Bearer\s+(.+)$/i.exec(req.headers.authorization || '');
  if (!match) return null;
  let found = null;
  for (const [project, key] of keys) if (safeEqual(match[1], key)) found = project;
  return found;
}

async function readJson(req, maxBytes) {
  const chunks = [];
  let length = 0;
  for await (const chunk of req) {
    length += chunk.length;
    if (length > maxBytes) {
      const error = new Error('Request body too large.');
      error.status = 413;
      throw error;
    }
    chunks.push(chunk);
  }
  try {
    const parsed = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) throw new Error();
    return parsed;
  } catch {
    const error = new Error('Request body must be a valid JSON object.');
    error.status = 400;
    throw error;
  }
}

function readPolicies(raw) {
  let p;
  try { p = JSON.parse(raw); } catch { throw new Error('Policy file is not valid JSON.'); }
  if (!p?.default || !p?.projects || !p?.routeByTask) throw new Error('Policy file is missing required sections.');
  for (const [task, route] of Object.entries(p.routeByTask)) {
    if (!TASKS.has(task) || !ROUTES.has(route)) throw new Error('Policy contains an unsupported task route.');
  }
  for (const config of Object.values(p.projects)) {
    if (config.allowedTaskClasses && config.allowedTaskClasses.some(task => !TASKS.has(task))) throw new Error('Policy contains an unsupported task class.');
  }
  return p;
}

export async function createWorkbenchServer({ env = process.env, policies: suppliedPolicies, upstreamFetch = fetch, logger = console, now = Date.now } = {}) {
  const keys = loadKeys(env.WORKBENCH_API_KEYS_JSON);
  if (typeof env.OMNIROUTE_API_KEY !== 'string' || !env.OMNIROUTE_API_KEY.trim()) {
    throw new Error('OMNIROUTE_API_KEY is required. Create a dedicated API key in OmniRoute.');
  }
  const upstreamBase = new URL(env.OMNIROUTE_BASE_URL || 'http://127.0.0.1:20128');
  if (!['http:', 'https:'].includes(upstreamBase.protocol) || upstreamBase.username || upstreamBase.password || upstreamBase.search || upstreamBase.hash) {
    throw new Error('OMNIROUTE_BASE_URL must be an HTTP(S) origin without credentials, query, or fragment.');
  }
  const base = upstreamBase.toString().replace(/\/+$/, '');
  const bodyLimit = Number(env.MAX_BODY_BYTES || 0) || 1048576;
  const policies = suppliedPolicies || readPolicies(await readFile(env.POLICY_FILE || new URL('../config/policies.json', import.meta.url), 'utf8'));
  const timeoutMs = Number(env.UPSTREAM_TIMEOUT_MS || policies.default.timeoutMs || 120000);
  const rate = new Map();

  return createServer(async (req, res) => {
    const started = now();
    const id = randomUUID();
    res.setHeader('x-request-id', id);
    const routeUrl = new URL(req.url || '/', 'http://workbench.local');
    if (req.method === 'GET' && routeUrl.pathname === '/healthz') {
      return sendJson(res, 200, { status: 'ok', service: 'omniroute-workbench' });
    }
    const models = req.method === 'GET' && routeUrl.pathname === '/v1/models';
    const completions = req.method === 'POST' && routeUrl.pathname === '/v1/chat/completions';
    if (!models && !completions) return sendJson(res, 404, { error: { type: 'not_found', message: 'Route not found.' } });

    const project = projectFor(req, keys);
    if (!project) return sendJson(res, 401, { error: { type: 'authentication_error', message: 'Valid project bearer token required.' } }, { 'www-authenticate': 'Bearer' });

    const policy = { ...policies.default, ...(policies.projects[project] || {}) };
    const maxPerMinute = Number(policy.maxRequestsPerMinute || 30);
    const windowStart = Math.floor(now() / 60000) * 60000;
    const rateKey = project + ':' + windowStart;
    const count = rate.get(rateKey) || 0;
    if (count >= maxPerMinute) {
      return sendJson(res, 429, { error: { type: 'rate_limit_error', message: 'Project request limit exceeded. Retry next minute.' } }, { 'retry-after': String(Math.max(1, Math.ceil((windowStart + 60000 - now()) / 1000))) });
    }
    rate.set(rateKey, count + 1);
    for (const key of rate.keys()) if (!key.endsWith(':' + windowStart)) rate.delete(key);

    let requestBody;
    let task = 'general';
    try {
      if (completions) {
        if (!String(req.headers['content-type'] || '').toLowerCase().includes('application/json')) {
          return sendJson(res, 415, { error: { type: 'invalid_request_error', message: 'Content-Type must be application/json.' } });
        }
        requestBody = await readJson(req, Math.min(bodyLimit, Number(policy.maxBodyBytes || policies.default.maxBodyBytes || 1048576)));
        if (!Array.isArray(requestBody.messages) || requestBody.messages.length === 0) {
          return sendJson(res, 400, { error: { type: 'invalid_request_error', message: 'messages must be a non-empty array.' } });
        }
        task = String(req.headers['x-task-class'] || 'general').toLowerCase();
        const allowed = policy.allowedTaskClasses || Object.keys(policies.routeByTask);
        if (!TASKS.has(task) || !allowed.includes(task) || !policies.routeByTask[task]) {
          return sendJson(res, 403, { error: { type: 'policy_error', message: 'Task class is not permitted for this project.' } });
        }
        requestBody.model = policies.routeByTask[task];
        const tokenFields = ['max_tokens', 'max_completion_tokens'].filter(field => Object.hasOwn(requestBody, field));
        if (tokenFields.length > 1) return sendJson(res, 400, { error: { type: 'invalid_request_error', message: 'Use only one output-token limit field.' } });
        const tokenCap = Number(policy.maxOutputTokens || policies.default.maxOutputTokens || 4096);
        if (tokenFields.length === 1) {
          const field = tokenFields[0];
          if (!Number.isSafeInteger(requestBody[field]) || requestBody[field] < 1) {
            return sendJson(res, 400, { error: { type: 'invalid_request_error', message: field + ' must be a positive integer.' } });
          }
          requestBody[field] = Math.min(requestBody[field], tokenCap);
        } else {
          requestBody.max_tokens = tokenCap;
        }
      }

      const response = await upstreamFetch(base + (models ? '/v1/models' : '/v1/chat/completions'), {
        method: req.method,
        headers: {
          authorization: 'Bearer ' + env.OMNIROUTE_API_KEY,
          accept: req.headers.accept || 'application/json',
          ...(completions ? { 'content-type': 'application/json' } : {}),
          'x-request-id': id
        },
        ...(completions ? { body: JSON.stringify(requestBody) } : {}),
        signal: AbortSignal.timeout(timeoutMs)
      });
      const outHeaders = { 'cache-control': 'no-store', 'x-workbench-project': project };
      const type = response.headers.get('content-type');
      if (type) outHeaders['content-type'] = type;
      res.writeHead(response.status, outHeaders);
      res.end(Buffer.from(await response.arrayBuffer()));
      logger.info?.(JSON.stringify({ event: 'proxy_request', requestId: id, project, task, method: req.method, status: response.status, durationMs: now() - started }));
    } catch (error) {
      const status = Number(error?.status) || (error?.name === 'TimeoutError' || error?.name === 'AbortError' ? 504 : 502);
      logger.warn?.(JSON.stringify({ event: 'proxy_error', requestId: id, project, task, status, durationMs: now() - started }));
      return sendJson(res, status, { error: { type: 'gateway_error', message: status === 413 || status === 400 ? error.message : status === 504 ? 'Upstream request timed out.' : 'Upstream gateway unavailable.' } });
    }
  });
}

if (process.argv[1] && import.meta.url === new URL('file://' + process.argv[1]).href) {
  try {
    const server = await createWorkbenchServer();
    const host = process.env.HOST || '127.0.0.1';
    const port = Number(process.env.PORT || 20129);
    server.listen(port, host, () => console.info('OmniRoute Workbench listening on http://' + host + ':' + port));
  } catch (error) {
    console.error('Startup refused: ' + error.message);
    process.exitCode = 1;
  }
}
