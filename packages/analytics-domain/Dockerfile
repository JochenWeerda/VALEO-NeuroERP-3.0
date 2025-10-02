***REMOVED*** Multi-stage build for analytics domain
FROM node:18-alpine AS base

***REMOVED*** Install dependencies for native modules
RUN apk add --no-cache python3 make g++

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy package files
COPY package.json package-lock.json* ./

***REMOVED*** Install dependencies
RUN npm ci --only=production && npm cache clean --force

***REMOVED*** Production stage
FROM node:18-alpine AS production

***REMOVED*** Install runtime dependencies
RUN apk add --no-cache dumb-init curl

***REMOVED*** Create app user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S analytics -u 1001

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy dependencies from base stage
COPY --from=base --chown=analytics:nodejs /app/node_modules ./node_modules

***REMOVED*** Copy application code
COPY --chown=analytics:nodejs . .

***REMOVED*** Build TypeScript
RUN npm run build

***REMOVED*** Remove development dependencies
RUN npm prune --production

***REMOVED*** Create reports directory with proper permissions
RUN mkdir -p /app/reports && chown -R analytics:nodejs /app/reports

***REMOVED*** Switch to non-root user
USER analytics

***REMOVED*** Expose port
EXPOSE 3005

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3005/health || exit 1

***REMOVED*** Start application
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]