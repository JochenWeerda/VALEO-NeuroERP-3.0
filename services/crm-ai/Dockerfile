FROM python:3.11-slim

WORKDIR /app

***REMOVED*** Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

***REMOVED*** Download spaCy model
RUN python -m spacy download en_core_web_sm

***REMOVED*** Copy application code
COPY . .

***REMOVED*** Expose port
EXPOSE 6200

***REMOVED*** Run the application
CMD ["python", "main.py"]