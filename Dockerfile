***REMOVED*** VALEO-NeuroERP-3.0 Container Implementation
***REMOVED*** Week 5 - Containerization & Orchestration Setup
***REMOVED*** Clean Architecture Container Configuration

FROM node:18-alpine AS base

***REMOVED*** Security best practices
RUN apk add --no-cache \
    dumb-init \
    && addgroup -g 1001 -S valeo \
    && adduser -S neuroerp -u 1001

USER neuroerp
WORKDIR /app

***REMOVED*** Copy package files first for dependency caching
COPY --chown=neuroerp package*.json ./
COPY --chown=neuroerp yarn.lock* ./

***REMOVED*** Install dependencies
ENV NODE_ENV=production
RUN npm ci --only=production && npm cache clean --force

***REMOVED*** Copy Clean Architecture domain source code
COPY --chown=neuroerp --from=base domains/ ./domains/

***REMOVED*** Copy business logic services
COPY --chown=neuroerp --from=base app/core/ ./app/core/
COPY --chown=neuroerp --from=base app/api/ ./app/api/
COPY --chown=neuroerp --from=base app/services/ ./app/services/

***REMOVED*** Copy configuration
COPY --chown=neuroerp config/ ./config/
COPY --chown=neuroerp .env* ./

***REMOVED*** Build Clean Architecture Services
RUN npm run build:domains
RUN npm run build:api

***REMOVED*** Production stage
FROM node:18-alpine AS production

RUN apk add --no-cache dumb-init && \
    addgroup -g 1001 -S valeo && \
    adduser -S neuroerp -u 1001

USER neuroerp
WORKDIR /app

***REMOVED*** Copy production dependencies and built application
COPY --chown=neuroerp --from=base /app/node_modules ./node_modules
COPY --chown=neuroerp --from=base /app/package*.json ./
COPY --chown=neuroerp --from=base /app/dist ./dist
COPY --chown=neuroerp --from=base /app/config ./config

***REMOVED*** Health checks for Kubernetes
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node healthcheck.js

EXPOSE 3000

***REMOVED*** Start with dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/server.js"]

