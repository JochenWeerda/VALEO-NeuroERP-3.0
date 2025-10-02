# VALEO NeuroERP 3.0 - ERP Domain Service Dockerfile
FROM node:18-alpine AS base

# Install dependencies for native modules
RUN apk add --no-cache python3 make g++

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Production stage
FROM node:18-alpine AS production

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create app user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S valero -u 1001

# Set working directory
WORKDIR /app

# Copy dependencies from base stage
COPY --from=base --chown=valero:nodejs /app/node_modules ./node_modules

# Copy source code
COPY --chown=valero:nodejs . .

# Build TypeScript
RUN npm run build

# Remove development dependencies
RUN npm prune --production

# Switch to non-root user
USER valero

# Expose port
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js

# Start the application
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "start"]