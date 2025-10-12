FROM python:3.11-slim

WORKDIR /app

***REMOVED*** Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

***REMOVED*** Copy application code
COPY app/ ./app/
COPY services/crm/main.py ./main.py

***REMOVED*** Expose port
EXPOSE 8001

***REMOVED*** Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8001/health')"

***REMOVED*** Run service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

