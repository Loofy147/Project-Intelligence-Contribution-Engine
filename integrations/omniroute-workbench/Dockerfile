FROM node:22-alpine
ENV NODE_ENV=production HOST=0.0.0.0 PORT=20129
WORKDIR /app
COPY package.json ./
COPY src ./src
COPY config ./config
USER node
EXPOSE 20129
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 CMD node -e "fetch('http://127.0.0.1:20129/healthz').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "src/server.mjs"]
