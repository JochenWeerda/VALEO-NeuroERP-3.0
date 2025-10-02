***REMOVED*** Multi-stage build for VALEO NeuroERP 3.0 HR Domain
FROM node:20-alpine AS builder

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy package files
COPY package*.json ./
COPY tsconfig.json ./

***REMOVED*** Install dependencies
RUN npm ci --only=production && npm cache clean --force

***REMOVED*** Copy source code
COPY src/ ./src/

***REMOVED*** Build the application
RUN npm run build

***REMOVED*** Production stage
FROM node:20-alpine AS production

***REMOVED*** Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

***REMOVED*** Create app user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy built application
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./

***REMOVED*** Switch to non-root user
USER nodejs

***REMOVED*** Expose port
EXPOSE 3030

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3030/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

***REMOVED*** Start the application
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/app/server.js"]

