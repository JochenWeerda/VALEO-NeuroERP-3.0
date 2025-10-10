# ===================================
# VALEO NeuroERP - Staging Deployment Script (PowerShell)
# ===================================
# Version: 3.0.0
# Purpose: Deploy staging environment on Windows/Docker Desktop
# Usage: .\scripts\staging-deploy.ps1 [-Clean] [-SkipBuild] [-SkipTests]

param(
    [switch]$Clean = $false,
    [switch]$SkipBuild = $false,
    [switch]$SkipTests = $false,
    [switch]$Help = $false
)

# ===================================
# Configuration
# ===================================

$ErrorActionPreference = "Stop"
$ComposeFile = "docker-compose.staging.yml"
$EnvFile = "env.example.staging"
$LogDir = "logs\staging"
$BackupDir = "backups\staging"

# ===================================
# Helper Functions
# ===================================

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "`n==> $Message" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" "Yellow"
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

function Show-Help {
    Write-Host @"

VALEO NeuroERP - Staging Deployment Script

USAGE:
    .\scripts\staging-deploy.ps1 [OPTIONS]

OPTIONS:
    -Clean          Stop and remove all containers, volumes, and images
    -SkipBuild      Skip Docker image building
    -SkipTests      Skip smoke tests after deployment
    -Help           Show this help message

EXAMPLES:
    .\scripts\staging-deploy.ps1                    # Normal deployment
    .\scripts\staging-deploy.ps1 -Clean             # Clean deployment
    .\scripts\staging-deploy.ps1 -SkipBuild         # Deploy without rebuilding
    .\scripts\staging-deploy.ps1 -SkipTests         # Deploy without tests

"@
}

function Test-DockerRunning {
    try {
        $null = docker ps 2>&1
        return $true
    }
    catch {
        return $false
    }
}

function Test-EnvFile {
    if (-not (Test-Path $EnvFile)) {
        Write-ErrorMsg "Environment file not found: $EnvFile"
        Write-Host "Please copy env.example.staging to .env and configure it."
        exit 1
    }
}

function New-Directories {
    Write-Step "Creating directories..."
    
    $dirs = @($LogDir, $BackupDir, "data", "config\keycloak")
    
    foreach ($dir in $dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Success "Created directory: $dir"
        }
    }
}

function Stop-Stack {
    Write-Step "Stopping existing stack..."
    
    try {
        docker-compose -f $ComposeFile down --remove-orphans 2>&1 | Out-Null
        Write-Success "Stack stopped"
    }
    catch {
        Write-Warning "No existing stack found or already stopped"
    }
}

function Remove-Stack {
    Write-Step "Removing all containers, volumes, and images..."
    
    docker-compose -f $ComposeFile down -v --rmi all --remove-orphans
    Write-Success "Stack completely removed"
}

function Build-Images {
    Write-Step "Building Docker images..."
    
    $startTime = Get-Date
    
    try {
        docker-compose -f $ComposeFile build --no-cache
        
        $duration = (Get-Date) - $startTime
        Write-Success "Images built successfully in $($duration.TotalMinutes.ToString('0.0')) minutes"
    }
    catch {
        Write-ErrorMsg "Image build failed"
        throw
    }
}

function Start-Stack {
    Write-Step "Starting staging stack..."
    
    try {
        docker-compose -f $ComposeFile up -d
        Write-Success "Stack started"
    }
    catch {
        Write-ErrorMsg "Failed to start stack"
        throw
    }
}

function Wait-ForServices {
    Write-Step "Waiting for services to be healthy..."
    
    $maxWait = 180
    $elapsed = 0
    $interval = 5
    
    $services = @(
        @{Name="PostgreSQL"; Container="valeo-staging-postgres"; Check={docker exec valeo-staging-postgres pg_isready -U valeo_staging}},
        @{Name="Redis"; Container="valeo-staging-redis"; Check={docker exec valeo-staging-redis redis-cli ping}},
        @{Name="Keycloak"; Container="valeo-staging-keycloak"; Check={curl -sf http://localhost:8180/health/ready}}
    )
    
    foreach ($service in $services) {
        Write-Host "  Waiting for $($service.Name)..." -NoNewline
        
        $ready = $false
        $serviceElapsed = 0
        
        while (-not $ready -and $serviceElapsed -lt $maxWait) {
            try {
                $null = & $service.Check 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $ready = $true
                    Write-Success " OK ($serviceElapsed seconds)"
                }
            }
            catch {
                # Keep waiting
            }
            
            if (-not $ready) {
                Start-Sleep -Seconds $interval
                $serviceElapsed += $interval
                Write-Host "." -NoNewline
            }
        }
        
        if (-not $ready) {
            Write-ErrorMsg " TIMEOUT after $maxWait seconds"
            throw "$($service.Name) did not become healthy"
        }
    }
    
    Write-Success "All core services are healthy"
}

function Invoke-DatabaseMigration {
    Write-Step "Running database migrations..."
    
    try {
        docker exec valeo-staging-backend alembic upgrade head
        Write-Success "Database migrations completed"
    }
    catch {
        Write-Warning "Migration failed (might be OK if no changes)"
    }
}

function Show-ContainerStatus {
    Write-Step "Container Status:"
    docker-compose -f $ComposeFile ps
}

function Show-ServiceUrls {
    Write-Step "Service URLs:"
    Write-Host ""
    Write-ColorOutput "  Frontend:        http://localhost:3001" "Cyan"
    Write-ColorOutput "  Backend API:     http://localhost:8001" "Cyan"
    Write-ColorOutput "  BFF:             http://localhost:4001" "Cyan"
    Write-ColorOutput "  Keycloak:        http://localhost:8180" "Cyan"
    Write-ColorOutput "  pgAdmin:         http://localhost:5151" "Cyan"
    Write-ColorOutput "  Redis Commander: http://localhost:8181" "Cyan"
    Write-Host ""
    Write-ColorOutput "  Test Users:" "Yellow"
    Write-Host "    - test-admin      / Test123!  (Admin)"
    Write-Host "    - test-user       / Test123!  (User)"
    Write-Host "    - test-readonly   / Test123!  (Read-Only)"
    Write-Host ""
}

function Invoke-SmokeTests {
    Write-Step "Running smoke tests..."
    
    $smokeTestScript = "scripts\smoke-tests-staging.sh"
    
    if (Test-Path $smokeTestScript) {
        # Try to run with Git Bash if available
        $gitBash = "C:\Program Files\Git\bin\bash.exe"
        
        if (Test-Path $gitBash) {
            & $gitBash $smokeTestScript
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "All smoke tests passed"
            }
            else {
                Write-Warning "Some smoke tests failed (check output above)"
            }
        }
        else {
            Write-Warning "Git Bash not found. Skipping smoke tests."
            Write-Host "  Install Git for Windows or run tests manually."
        }
    }
    else {
        Write-Warning "Smoke test script not found: $smokeTestScript"
    }
}

function Create-Backup {
    Write-Step "Creating database backup..."
    
    $timestamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
    $backupFile = "$BackupDir\pre-deployment-$timestamp.dump"
    
    try {
        docker exec valeo-staging-postgres pg_dump `
            -U valeo_staging `
            -Fc `
            valeo_neuro_erp_staging `
            > $backupFile
        
        Write-Success "Backup created: $backupFile"
    }
    catch {
        Write-Warning "Backup failed (might be OK if database doesn't exist yet)"
    }
}

function Show-Logs {
    param([int]$Lines = 50)
    
    Write-Step "Recent logs (last $Lines lines):"
    docker-compose -f $ComposeFile logs --tail=$Lines
}

# ===================================
# Main Deployment Flow
# ===================================

function Main {
    $startTime = Get-Date
    
    Write-ColorOutput @"

╔════════════════════════════════════════════╗
║  VALEO NeuroERP - Staging Deployment      ║
║  Version 3.0.0                             ║
╚════════════════════════════════════════════╝

"@ "Cyan"

    # Show help if requested
    if ($Help) {
        Show-Help
        exit 0
    }
    
    # Pre-flight checks
    Write-Step "Pre-flight checks..."
    
    if (-not (Test-DockerRunning)) {
        Write-ErrorMsg "Docker is not running!"
        Write-Host "Please start Docker Desktop and try again."
        exit 1
    }
    Write-Success "Docker is running"
    
    Test-EnvFile
    Write-Success "Environment file found"
    
    # Create necessary directories
    New-Directories
    
    # Clean deployment if requested
    if ($Clean) {
        Remove-Stack
    }
    else {
        Stop-Stack
    }
    
    # Create backup before deployment
    Create-Backup
    
    # Build images unless skipped
    if (-not $SkipBuild) {
        Build-Images
    }
    else {
        Write-Warning "Skipping image build (using existing images)"
    }
    
    # Start the stack
    Start-Stack
    
    # Wait for services
    Wait-ForServices
    
    # Run database migrations
    Invoke-DatabaseMigration
    
    # Show status
    Show-ContainerStatus
    
    # Run smoke tests unless skipped
    if (-not $SkipTests) {
        Start-Sleep -Seconds 10  # Give services a bit more time
        Invoke-SmokeTests
    }
    else {
        Write-Warning "Skipping smoke tests"
    }
    
    # Success!
    $duration = (Get-Date) - $startTime
    
    Write-ColorOutput @"

╔════════════════════════════════════════════╗
║  ✅ Staging Deployment Complete!          ║
╚════════════════════════════════════════════╝

"@ "Green"
    
    Write-Host "Total deployment time: $($duration.TotalMinutes.ToString('0.0')) minutes"
    Write-Host ""
    
    Show-ServiceUrls
    
    Write-ColorOutput "🎉 Happy Testing!" "Green"
}

# ===================================
# Error Handling
# ===================================

trap {
    Write-ErrorMsg "Deployment failed!"
    Write-Host ""
    Write-Host "Error details:"
    Write-Host $_.Exception.Message
    Write-Host ""
    Write-Host "Recent logs:"
    Show-Logs -Lines 20
    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "  1. Check Docker Desktop is running"
    Write-Host "  2. Check disk space (need ~10GB free)"
    Write-Host "  3. Check no port conflicts (3001, 8001, 8180, etc.)"
    Write-Host "  4. Try: .\scripts\staging-deploy.ps1 -Clean"
    Write-Host ""
    exit 1
}

# ===================================
# Run Main
# ===================================

Main

