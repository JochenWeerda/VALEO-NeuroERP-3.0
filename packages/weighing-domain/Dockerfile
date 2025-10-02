***REMOVED*** Use Node.js 20 Alpine as base image
FROM node:20-alpine

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Install system dependencies for PostgreSQL client
RUN apk add --no-cache postgresql-client

***REMOVED*** Copy package files
COPY package*.json ./
COPY drizzle.config.ts ./

***REMOVED*** Install dependencies
RUN npm ci --only=production && npm cache clean --force

***REMOVED*** Copy source code
COPY src/ ./src/
COPY migrations/ ./migrations/

***REMOVED*** Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S weighing -u 1001

***REMOVED*** Change ownership of app directory
RUN chown -R weighing:nodejs /app
USER weighing

***REMOVED*** Expose port
EXPOSE 3005

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3005/health', (res) => { \
    process.exit(res.statusCode === 200 ? 0 : 1) \
  }).on('error', () => process.exit(1))"

***REMOVED*** Start the application
CMD ["npm", "start"]