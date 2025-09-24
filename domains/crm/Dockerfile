FROM node:18-alpine

***REMOVED*** Set working directory
WORKDIR /app

***REMOVED*** Copy package files
COPY package*.json ./

***REMOVED*** Install dependencies
RUN npm ci --only=production

***REMOVED*** Copy source code
COPY . .

***REMOVED*** Build the application
RUN npm run build

***REMOVED*** Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

***REMOVED*** Change ownership
RUN chown -R nodejs:nodejs /app
USER nodejs

***REMOVED*** Expose port
EXPOSE 8081

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8081/health || exit 1

***REMOVED*** Start the application
CMD ["npm", "start"]
