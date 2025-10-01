***REMOVED*** Build stage
FROM node:20-alpine AS builder

WORKDIR /app

***REMOVED*** Copy package files
COPY package*.json ./
COPY tsconfig.json ./

***REMOVED*** Install dependencies
RUN npm ci

***REMOVED*** Copy source
COPY src/ ./src/

***REMOVED*** Build
RUN npm run build

***REMOVED*** Production stage
FROM node:20-alpine

WORKDIR /app

***REMOVED*** Copy package files
COPY package*.json ./

***REMOVED*** Install production dependencies only
RUN npm ci --only=production

***REMOVED*** Copy built files from builder
COPY --from=builder /app/dist ./dist

***REMOVED*** Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

***REMOVED*** Expose port
EXPOSE 3007

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3007/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

***REMOVED*** Start server
CMD ["node", "dist/app/server.js"]
