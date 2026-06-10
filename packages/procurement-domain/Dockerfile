FROM node:20-alpine

RUN corepack enable && corepack prepare pnpm@9.12.0 --activate

WORKDIR /workspace

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.base.json ./
COPY packages/procurement-domain/package.json packages/procurement-domain/package.json

RUN pnpm install --frozen-lockfile \
    --filter @valero-neuroerp/procurement-domain...

COPY packages/procurement-domain packages/procurement-domain

RUN pnpm --filter @valero-neuroerp/procurement-domain build && \
    chown -R node:node /workspace

WORKDIR /workspace/packages/procurement-domain
USER node

EXPOSE 3002

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:3002/health >/dev/null || exit 1

CMD ["node", "dist/index.js"]
