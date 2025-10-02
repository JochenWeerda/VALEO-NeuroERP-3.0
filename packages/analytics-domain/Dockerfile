# Multi-stage build for analytics domain
FROM node:18-alpine AS base

# Install dependencies for native modules
RUN apk add --no-cache python3 make g++

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Production stage
FROM node:18-alpine AS production

# Install runtime dependencies
RUN apk add --no-cache dumb-init curl

# Create app user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S analytics -u 1001

# Set working directory
WORKDIR /app

# Copy dependencies from base stage
COPY --from=base --chown=analytics:nodejs /app/node_modules ./node_modules

# Copy application code
COPY --chown=analytics:nodejs . .

# Build TypeScript
RUN npm run build

# Remove development dependencies
RUN npm prune --production

# Create reports directory with proper permissions
RUN mkdir -p /app/reports && chown -R analytics:nodejs /app/reports

# Switch to non-root user
USER analytics

# Expose port
EXPOSE 3005

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3005/health || exit 1

# Start application
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]