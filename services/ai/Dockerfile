FROM python:3.11-slim

WORKDIR /app

# System dependencies for AI/ML
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app/ ./app/
COPY main.py ./

# Create data directory for ChromaDB
RUN mkdir -p /app/data/chroma

# Environment
ENV PYTHONUNBUFFERED=1

# Expose ports (REST API + MCP Server)
EXPOSE 5000 5001

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

