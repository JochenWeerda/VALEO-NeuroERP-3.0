FROM python:3.11-slim

WORKDIR /app

COPY services/finance/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/finance/app ./app
COPY services/finance/main.py ./main.py

EXPOSE 8003

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8003/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]

