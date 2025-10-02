# VALEO-NeuroERP Deployment Script
Write-Host "Starting VALEO-NeuroERP deployment..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version
if (-not $?) {
    Write-Host "Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}
Write-Host "Using $pythonVersion" -ForegroundColor Green

# Create and activate virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
if (-not $?) {
    Write-Host "Failed to create virtual environment." -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate
if (-not $?) {
    Write-Host "Failed to activate virtual environment." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if (-not $?) {
    Write-Host "Failed to install dependencies." -ForegroundColor Red
    exit 1
}

# Run database migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
alembic upgrade head
if (-not $?) {
    Write-Host "Failed to run database migrations." -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow

# Start Redis
Write-Host "Starting Redis..." -ForegroundColor Yellow
Start-Process redis-server -NoNewWindow
if (-not $?) {
    Write-Host "Failed to start Redis." -ForegroundColor Red
    exit 1
}

# Start MongoDB
Write-Host "Starting MongoDB..." -ForegroundColor Yellow
Start-Process mongod -NoNewWindow
if (-not $?) {
    Write-Host "Failed to start MongoDB." -ForegroundColor Red
    exit 1
}

# Start Prometheus
Write-Host "Starting Prometheus..." -ForegroundColor Yellow
Start-Process prometheus -NoNewWindow
if (-not $?) {
    Write-Host "Failed to start Prometheus." -ForegroundColor Red
    exit 1
}

# Start Grafana
Write-Host "Starting Grafana..." -ForegroundColor Yellow
Start-Process grafana-server -NoNewWindow
if (-not $?) {
    Write-Host "Failed to start Grafana." -ForegroundColor Red
    exit 1
}

# Start FastAPI server
Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
Start-Process uvicorn "backend.main:app --host 0.0.0.0 --port 8000" -NoNewWindow
if (-not $?) {
    Write-Host "Failed to start FastAPI server." -ForegroundColor Red
    exit 1
}

# Start Celery worker
Write-Host "Starting Celery worker..." -ForegroundColor Yellow
Start-Process celery "worker -A backend.celery:app --loglevel=info" -NoNewWindow
if (-not $?) {
    Write-Host "Failed to start Celery worker." -ForegroundColor Red
    exit 1
}

Write-Host "VALEO-NeuroERP deployment completed successfully!" -ForegroundColor Green
Write-Host "Services running:" -ForegroundColor Green
Write-Host "- FastAPI server: http://localhost:8000" -ForegroundColor Cyan
Write-Host "- API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "- Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "- Grafana: http://localhost:3000" -ForegroundColor Cyan 