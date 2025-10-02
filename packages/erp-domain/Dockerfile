***REMOVED*** VALEO NeuroERP 3.0 - ERP Domain Service Dockerfile
FROM node:18-alpine AS base

***REMOVED*** Install dependencies for native modules
RUN apk add --no-cache python3 make g++

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy package files
COPY package*.json ./

***REMOVED*** Install dependencies
RUN npm ci --only=production && npm cache clean --force

***REMOVED*** Production stage
FROM node:18-alpine AS production

***REMOVED*** Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

***REMOVED*** Create app user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S valero -u 1001

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy dependencies from base stage
COPY --from=base --chown=valero:nodejs /app/node_modules ./node_modules

***REMOVED*** Copy source code
COPY --chown=valero:nodejs . .

***REMOVED*** Build TypeScript
RUN npm run build

***REMOVED*** Remove development dependencies
RUN npm prune --production

***REMOVED*** Switch to non-root user
USER valero

***REMOVED*** Expose port
EXPOSE 3002

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js

***REMOVED*** Start the application
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]