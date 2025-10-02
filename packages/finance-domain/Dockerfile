# VALEO NeuroERP 3.0 - Finance Domain Dockerfile
# Multi-stage build for optimal production image

# ===== BUILD STAGE =====
FROM node:18-alpine AS builder

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY domains/finance/package*.json ./domains/finance/

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY domains/finance/ ./domains/finance/
COPY packages/ ./packages/
COPY migrations/sql/finance/ ./migrations/sql/finance/

# Build TypeScript
RUN npm run build --workspace=domains/finance

# ===== PRODUCTION STAGE =====
FROM node:18-alpine AS production

# Install system dependencies for production
RUN apk add --no-cache \
    postgresql-client \
    curl \
    dumb-init \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S finance -u 1001

# Set working directory
WORKDIR /app

# Copy built application from builder stage
COPY --from=builder --chown=finance:nodejs /app/dist ./dist
COPY --from=builder --chown=finance:nodejs /app/domains/finance/dist ./domains/finance/dist
COPY --from=builder --chown=finance:nodejs /app/packages/utilities/dist ./packages/utilities/dist
COPY --from=builder --chown=finance:nodejs /app/node_modules ./node_modules

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R finance:nodejs /app/data /app/logs

# Switch to non-root user
USER finance

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3001/health || exit 1

# Environment variables
ENV NODE_ENV=production
ENV PORT=3001

# Expose port
EXPOSE 3001

# Use dumb-init for proper signal handling
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

# Start the application
CMD ["node", "domains/finance/dist/bootstrap.js"]