***REMOVED*** Build stage
FROM node:18-alpine AS builder

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy package files
COPY package*.json ./
COPY tsconfig.json ./

***REMOVED*** Install dependencies
RUN npm ci --only=production

***REMOVED*** Copy source code
COPY src/ ./src/

***REMOVED*** Build the application
RUN npm run build

***REMOVED*** Production stage
FROM node:18-alpine AS production

***REMOVED*** Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

***REMOVED*** Create app user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S sales -u 1001

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy package files
COPY package*.json ./

***REMOVED*** Install production dependencies only
RUN npm ci --only=production && npm cache clean --force

***REMOVED*** Copy built application
COPY --from=builder /app/dist ./dist

***REMOVED*** Change ownership
RUN chown -R sales:nodejs /app
USER sales

***REMOVED*** Expose port
EXPOSE 3001

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3001/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

***REMOVED*** Start the application
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]