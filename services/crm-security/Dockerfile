FROM python:3.11-slim

WORKDIR /app

***REMOVED*** Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

***REMOVED*** Copy application code
COPY . .

***REMOVED*** Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

***REMOVED*** Expose port
EXPOSE 5700

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5700/health || exit 1

***REMOVED*** Run the application
CMD ["python", "main.py"]