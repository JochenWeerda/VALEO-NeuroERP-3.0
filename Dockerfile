***REMOVED*** Multi-stage build for VALEO-NeuroERP Backend
***REMOVED*** Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

***REMOVED*** Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy requirements
COPY requirements.txt .

***REMOVED*** Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

***REMOVED*** Stage 2: Runtime
FROM python:3.11-slim

***REMOVED*** Create non-root user
RUN groupadd -r appuser -g 1000 && \
    useradd -r -u 1000 -g appuser appuser

WORKDIR /app

***REMOVED*** Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

***REMOVED*** Copy application code
COPY --chown=appuser:appuser . .

***REMOVED*** Create directories with correct permissions
RUN mkdir -p /app/data /app/logs /tmp && \
    chown -R appuser:appuser /app/data /app/logs /tmp

***REMOVED*** Set PATH for user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

***REMOVED*** Switch to non-root user
USER 1000:1000

***REMOVED*** Expose port
EXPOSE 8000

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')"

***REMOVED*** Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
