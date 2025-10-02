***REMOVED*** VALEO NeuroERP 3.0 - Procurement Domain Dockerfile
FROM node:18-alpine AS base

***REMOVED*** Install system dependencies for AI/ML processing
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

***REMOVED*** Set Python path
ENV PYTHONPATH=/usr/lib/python3/dist-packages:$PYTHONPATH

***REMOVED*** Create app directory
WORKDIR /app

***REMOVED*** Copy package files
COPY package*.json ./
COPY tsconfig.json ./

***REMOVED*** Install dependencies
RUN npm ci --only=production && npm cache clean --force

***REMOVED*** Copy source code
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/
COPY models/ ./models/

***REMOVED*** Build TypeScript
RUN npm run build

***REMOVED*** Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S procurement -u 1001

***REMOVED*** Change ownership
RUN chown -R procurement:nodejs /app
USER procurement

***REMOVED*** Expose port
EXPOSE 3002

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3002/health || exit 1

***REMOVED*** Start application
CMD ["npm", "start"]