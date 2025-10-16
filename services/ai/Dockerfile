FROM python:3.11-slim

WORKDIR /app

***REMOVED*** System dependencies for AI/ML
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

***REMOVED*** Application code
COPY app/ ./app/
COPY main.py ./

***REMOVED*** Create data directory for ChromaDB
RUN mkdir -p /app/data/chroma

***REMOVED*** Environment
ENV PYTHONUNBUFFERED=1

***REMOVED*** Expose ports (REST API + MCP Server)
EXPOSE 5000 5001

***REMOVED*** Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

