# VALEO-NeuroERP-3.0 Container Implementation
# Week 5 - Containerization & Orchestration Setup
# Clean Architecture Container Configuration

FROM node:18-alpine AS base

# Security best practices
RUN apk add --no-cache \
    dumb-init \
    && addgroup -g 1001 -S valeo \
    && adduser -S neuroerp -u 1001

USER neuroerp
WORKDIR /app

# Copy package files first for dependency caching
COPY --chown=neuroerp package*.json ./
COPY --chown=neuroerp yarn.lock* ./

# Install dependencies
ENV NODE_ENV=production
RUN npm ci --only=production && npm cache clean --force

# Copy Clean Architecture domain source code
COPY --chown=neuroerp --from=base domains/ ./domains/

# Copy business logic services
COPY --chown=neuroerp --from=base app/core/ ./app/core/
COPY --chown=neuroerp --from=base app/api/ ./app/api/
COPY --chown=neuroerp --from=base app/services/ ./app/services/

# Copy configuration
COPY --chown=neuroerp config/ ./config/
COPY --chown=neuroerp .env* ./

# Build Clean Architecture Services
RUN npm run build:domains
RUN npm run build:api

# Production stage
FROM node:18-alpine AS production

RUN apk add --no-cache dumb-init && \
    addgroup -g 1001 -S valeo && \
    adduser -S neuroerp -u 1001

USER neuroerp
WORKDIR /app

# Copy production dependencies and built application
COPY --chown=neuroerp --from=base /app/node_modules ./node_modules
COPY --chown=neuroerp --from=base /app/package*.json ./
COPY --chown=neuroerp --from=base /app/dist ./dist
COPY --chown=neuroerp --from=base /app/config ./config

# Health checks for Kubernetes
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node healthcheck.js

EXPOSE 3000

# Start with dumb-init for proper signal handling
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/server.js"]

