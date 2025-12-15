# Production Deployment Script for Laba-2 Flask Application
# Usage: .\deploy.ps1 [build|start|stop|restart|logs|backup|status|deploy]

param(
    [Parameter(Position=0)]
    [ValidateSet('build', 'start', 'stop', 'restart', 'logs', 'status', 'backup', 'deploy', 'help')]
    [string]$Command = 'help'
)

$ProjectName = "laba-2-main"
$BackupDir = ".\backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Helper functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if .env file exists
function Test-EnvFile {
    if (-not (Test-Path .env)) {
        Write-Warning-Custom ".env file not found!"
        if (Test-Path .env.production) {
            Write-Info "Copying .env.production to .env..."
            Copy-Item .env.production .env
            Write-Warning-Custom "Please edit .env and set FLASK_SECRET to a secure random value!"
            exit 1
        } else {
            Write-Error-Custom "No .env.production template found!"
            exit 1
        }
    }
    
    # Check if FLASK_SECRET is set to default value
    $envContent = Get-Content .env -Raw
    if ($envContent -match "CHANGE_ME_TO_SECURE_RANDOM_STRING") {
        Write-Error-Custom "FLASK_SECRET is not set to a secure value in .env!"
        Write-Info "Generate a secure key with PowerShell:"
        Write-Host '$bytes = New-Object byte[] 32; [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes); [System.BitConverter]::ToString($bytes) -replace "-",""' -ForegroundColor Cyan
        exit 1
    }
}

# Build Docker image
function Invoke-Build {
    Write-Info "Building Docker image..."
    docker-compose build
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Build completed successfully!"
    } else {
        Write-Error-Custom "Build failed!"
        exit 1
    }
}

# Start application
function Start-Application {
    Write-Info "Starting application..."
    Test-EnvFile
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Application started!"
        Write-Info "Waiting for health check..."
        Start-Sleep -Seconds 5
        Test-Health
    } else {
        Write-Error-Custom "Failed to start application!"
        exit 1
    }
}

# Stop application
function Stop-Application {
    Write-Info "Stopping application..."
    docker-compose stop
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Application stopped!"
    } else {
        Write-Error-Custom "Failed to stop application!"
        exit 1
    }
}

# Restart application
function Restart-Application {
    Write-Info "Restarting application..."
    Test-EnvFile
    docker-compose restart
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Application restarted!"
        Start-Sleep -Seconds 5
        Test-Health
    } else {
        Write-Error-Custom "Failed to restart application!"
        exit 1
    }
}

# View logs
function Show-Logs {
    Write-Info "Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f web
}

# Check application health
function Test-Health {
    Write-Info "Checking application health..."
    $HealthUrl = "http://localhost:5000/health"
    
    try {
        $response = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Info "✓ Health check passed!"
            Write-Info "Application is running at: http://localhost:5000"
        } else {
            Write-Error-Custom "✗ Health check failed! (HTTP $($response.StatusCode))"
            Write-Warning-Custom "Check logs with: .\deploy.ps1 logs"
            exit 1
        }
    } catch {
        Write-Error-Custom "✗ Health check failed! Cannot connect to application."
        Write-Warning-Custom "Check logs with: .\deploy.ps1 logs"
        exit 1
    }
}

# Show application status
function Show-Status {
    Write-Info "Application status:"
    docker-compose ps
    Write-Host ""
    Test-Health
}

# Create database backup
function New-Backup {
    Write-Info "Creating database backup..."
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }
    
    $ContainerId = docker-compose ps -q web
    
    if ([string]::IsNullOrWhiteSpace($ContainerId)) {
        Write-Error-Custom "Container is not running!"
        exit 1
    }
    
    $BackupFile = "$BackupDir\backup_$Timestamp.db"
    docker cp "$($ContainerId):/data/my_database.db" $BackupFile
    
    if (Test-Path $BackupFile) {
        $size = (Get-Item $BackupFile).Length / 1KB
        Write-Info "✓ Backup created: $BackupFile"
        Write-Info "Backup size: $([math]::Round($size, 2)) KB"
    } else {
        Write-Error-Custom "✗ Backup failed!"
        exit 1
    }
}

# Deploy (full deployment process)
function Invoke-Deploy {
    Write-Info "Starting full deployment process..."
    
    Test-EnvFile
    
    Write-Info "Step 1: Creating backup..."
    $containers = docker-compose ps
    if ($containers -match "Up") {
        try {
            New-Backup
        } catch {
            Write-Warning-Custom "Backup failed, continuing anyway..."
        }
    } else {
        Write-Warning-Custom "Application not running, skipping backup..."
    }
    
    Write-Info "Step 2: Building new image..."
    Invoke-Build
    
    Write-Info "Step 3: Stopping old containers..."
    docker-compose down
    
    Write-Info "Step 4: Starting new containers..."
    docker-compose up -d
    
    Write-Info "Step 5: Waiting for application to start..."
    Start-Sleep -Seconds 10
    
    Write-Info "Step 6: Running health check..."
    Test-Health
    
    Write-Info "✓ Deployment completed successfully!"
    Write-Info "View logs with: .\deploy.ps1 logs"
}

# Show usage
function Show-Usage {
    Write-Host "Usage: .\deploy.ps1 [command]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Cyan
    Write-Host "  build     - Build Docker image"
    Write-Host "  start     - Start application"
    Write-Host "  stop      - Stop application"
    Write-Host "  restart   - Restart application"
    Write-Host "  logs      - View application logs"
    Write-Host "  status    - Show application status"
    Write-Host "  backup    - Create database backup"
    Write-Host "  deploy    - Full deployment (backup, build, restart)"
    Write-Host "  help      - Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\deploy.ps1 deploy    # Full deployment process"
    Write-Host "  .\deploy.ps1 logs      # View logs"
    Write-Host "  .\deploy.ps1 backup    # Create database backup"
}

# Main script logic
switch ($Command) {
    'build' {
        Invoke-Build
    }
    'start' {
        Start-Application
    }
    'stop' {
        Stop-Application
    }
    'restart' {
        Restart-Application
    }
    'logs' {
        Show-Logs
    }
    'status' {
        Show-Status
    }
    'backup' {
        New-Backup
    }
    'deploy' {
        Invoke-Deploy
    }
    'help' {
        Show-Usage
    }
    default {
        Write-Error-Custom "Unknown command: $Command"
        Show-Usage
        exit 1
    }
}
