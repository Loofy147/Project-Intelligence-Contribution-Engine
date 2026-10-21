import test from 'node:test';
import assert from 'node:assert/strict';
import { createWorkbenchServer } from '../src/server.mjs';

const PROJECT_KEY = 'p'.repeat(64);
const OMNI_KEY = 'omniroute-test-secret';
const POLICY = {
  routeByTask: { general: 'auto', coding: 'auto/coding', reasoning: 'auto/smart', research: 'auto/smart', fast: 'auto/fast', cheap: 'auto/cheap', offline: 'auto/offline' },
  default: { maxOutputTokens: 100, maxBodyBytes: 2048, timeoutMs: 2000, maxRequestsPerMinute: 3, allowedTaskClasses: ['general', 'coding', 'reasoning', 'research', 'fast', 'cheap', 'offline'] },
  projects: { demo: { maxOutputTokens: 80, maxRequestsPerMinute: 3, allowedTaskClasses: ['general', 'coding', 'cheap'] } }
};

async function withServer(t, options = {}) {
  const seen = [];
  const server = await createWorkbenchServer({
    env: {
      WORKBENCH_API_KEYS_JSON: JSON.stringify({ demo: PROJECT_KEY }),
      OMNIROUTE_API_KEY: OMNI_KEY,
      OMNIROUTE_BASE_URL: 'http://omniroute.test:20128',
      MAX_BODY_BYTES: '2048',
      ...options.env
    },
    policies: options.policies || POLICY,
    upstreamFetch: options.upstreamFetch || (async (url, init) => {
      seen.push({ url, init });
      return new Response(JSON.stringify({ id: 'fake-response', data: [] }), { status: 200, headers: { 'content-type': 'application/json' } });
    }),
    logger: { info() {}, warn() {} },
    now: options.now || Date.now
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + server.address().port;
  t.after(() => new Promise(resolve => server.close(resolve)));
  return { base, seen };
}

const auth = { authorization: 'Bearer ' + PROJECT_KEY };
const body = { messages: [{ role: 'user', content: 'hello' }] };

test('health endpoint needs no provider credential', async t => {
  const { base } = await withServer(t);
  const res = await fetch(base + '/healthz');
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { status: 'ok', service: 'omniroute-workbench' });
});

test('rejects missing or invalid project key', async t => {
  const { base } = await withServer(t);
  assert.equal((await fetch(base + '/v1/models')).status, 401);
});

test('routes coding requests and clamps output tokens', async t => {
  const { base, seen } = await withServer(t);
  const res = await fetch(base + '/v1/chat/completions', {
    method: 'POST', headers: { ...auth, 'content-type': 'application/json', 'x-task-class': 'coding' },
    body: JSON.stringify({ ...body, model: 'untrusted/model', max_tokens: 900 })
  });
  assert.equal(res.status, 200);
  assert.equal(seen[0].url, 'http://omniroute.test:20128/v1/chat/completions');
  assert.equal(seen[0].init.headers.authorization, 'Bearer ' + OMNI_KEY);
  const forwarded = JSON.parse(seen[0].init.body);
  assert.equal(forwarded.model, 'auto/coding');
  assert.equal(forwarded.max_tokens, 80);
});

test('rejects malformed token limits and duplicate token fields', async t => {
  const { base, seen } = await withServer(t);
  for (const payload of [{ ...body, max_tokens: '900' }, { ...body, max_tokens: 4, max_completion_tokens: 5 }]) {
    const response = await fetch(base + '/v1/chat/completions', { method: 'POST', headers: { ...auth, 'content-type': 'application/json' }, body: JSON.stringify(payload) });
    assert.equal(response.status, 400);
  }
  assert.equal(seen.length, 0);
});

test('blocks task classes not enabled for project', async t => {
  const { base, seen } = await withServer(t);
  const res = await fetch(base + '/v1/chat/completions', { method: 'POST', headers: { ...auth, 'content-type': 'application/json', 'x-task-class': 'research' }, body: JSON.stringify(body) });
  assert.equal(res.status, 403);
  assert.equal(seen.length, 0);
});

test('does not proxy unsupported management routes', async t => {
  const { base, seen } = await withServer(t);
  const res = await fetch(base + '/admin/config', { headers: auth });
  assert.equal(res.status, 404);
  assert.equal(seen.length, 0);
});

test('enforces per-project request rate', async t => {
  const { base } = await withServer(t);
  for (let i = 0; i < 3; i++) assert.equal((await fetch(base + '/v1/models', { headers: auth })).status, 200);
  const limited = await fetch(base + '/v1/models', { headers: auth });
  assert.equal(limited.status, 429);
  assert.ok(Number(limited.headers.get('retry-after')) >= 1);
});

test('rejects oversized request bodies', async t => {
  const { base, seen } = await withServer(t);
  const res = await fetch(base + '/v1/chat/completions', {
    method: 'POST', headers: { ...auth, 'content-type': 'application/json' },
    body: JSON.stringify({ messages: [{ role: 'user', content: 'x'.repeat(3000) }] })
  });
  assert.equal(res.status, 413);
  assert.equal(seen.length, 0);
});

test('sanitizes upstream failures and logs no response body', async t => {
  const logs = [];
  const server = await createWorkbenchServer({
    env: { WORKBENCH_API_KEYS_JSON: JSON.stringify({ demo: PROJECT_KEY }), OMNIROUTE_API_KEY: OMNI_KEY, OMNIROUTE_BASE_URL: 'http://omniroute.test' },
    policies: POLICY,
    upstreamFetch: async () => { throw new Error('private host / secret token / stack trace'); },
    logger: { info(s) { logs.push(s); }, warn(s) { logs.push(s); } }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = 'http://127.0.0.1:' + server.address().port;
  t.after(() => new Promise(resolve => server.close(resolve)));
  const res = await fetch(base + '/v1/models', { headers: auth });
  assert.equal(res.status, 502);
  assert.deepEqual(await res.json(), { error: { type: 'gateway_error', message: 'Upstream gateway unavailable.' } });
  assert.ok(logs.every(line => !line.includes('private host')));
});
