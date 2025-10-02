***REMOVED*** VALEO NeuroERP 3.0 - Finance Domain Dockerfile
***REMOVED*** Multi-stage build for optimal production image

***REMOVED*** ===== BUILD STAGE =====
FROM node:18-alpine AS builder

***REMOVED*** Install system dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/cache/apk/*

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy package files
COPY package*.json ./
COPY domains/finance/package*.json ./domains/finance/

***REMOVED*** Install dependencies
RUN npm ci --only=production && npm cache clean --force

***REMOVED*** Copy source code
COPY domains/finance/ ./domains/finance/
COPY packages/ ./packages/
COPY migrations/sql/finance/ ./migrations/sql/finance/

***REMOVED*** Build TypeScript
RUN npm run build --workspace=domains/finance

***REMOVED*** ===== PRODUCTION STAGE =====
FROM node:18-alpine AS production

***REMOVED*** Install system dependencies for production
RUN apk add --no-cache \
    postgresql-client \
    curl \
    dumb-init \
    && rm -rf /var/cache/apk/*

***REMOVED*** Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S finance -u 1001

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy built application from builder stage
COPY --from=builder --chown=finance:nodejs /app/dist ./dist
COPY --from=builder --chown=finance:nodejs /app/domains/finance/dist ./domains/finance/dist
COPY --from=builder --chown=finance:nodejs /app/packages/utilities/dist ./packages/utilities/dist
COPY --from=builder --chown=finance:nodejs /app/node_modules ./node_modules

***REMOVED*** Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R finance:nodejs /app/data /app/logs

***REMOVED*** Switch to non-root user
USER finance

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3001/health || exit 1

***REMOVED*** Environment variables
ENV NODE_ENV=production
ENV PORT=3001

***REMOVED*** Expose port
EXPOSE 3001

***REMOVED*** Use dumb-init for proper signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

***REMOVED*** Start the application
CMD ["node", "domains/finance/dist/bootstrap.js"]