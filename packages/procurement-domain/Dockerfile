# VALEO NeuroERP 3.0 - Procurement Domain Dockerfile
FROM node:18-alpine AS base

# Install system dependencies for AI/ML processing
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-numpy \
    py3-scipy \
    py3-pandas \
    py3-scikit-learn \
    tesseract-ocr \
    tesseract-ocr-data-deu \
    tesseract-ocr-data-eng \
    poppler-utils \
    imagemagick \
    redis \
    postgresql-client \
    curl \
    && rm -rf /var/cache/apk/*

# Set Python path
ENV PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH

# Create app directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/
COPY models/ ./models/

# Build TypeScript
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S procurement -u 1001

# Change ownership
RUN chown -R procurement:nodejs /app
USER procurement

# Expose port
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3002/health || exit 1

# Start application
CMD ["npm", "start"]