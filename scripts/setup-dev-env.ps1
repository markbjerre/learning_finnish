# Development Environment Setup Script (PowerShell)
# Sets up all projects for local development on Windows

param(
    [switch]$Docker,
    [switch]$Help
)

# Colors
$InfoColor = "Cyan"
$SuccessColor = "Green"
$ErrorColor = "Red"
$WarningColor = "Yellow"

function Write-Header {
    param([string]$Text)
    Write-Host "`n=== $Text ===" -ForegroundColor $InfoColor
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor $SuccessColor
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor $ErrorColor
}

function Write-Warning-Custom {
    param([string]$Text)
    Write-Host "⚠ $Text" -ForegroundColor $WarningColor
}

function Write-Info {
    param([string]$Text)
    Write-Host "ℹ $Text" -ForegroundColor $InfoColor
}

function Show-Help {
    @"
Development Environment Setup Script (Windows PowerShell)

USAGE:
    powershell -ExecutionPolicy Bypass -File scripts/setup-dev-env.ps1 [OPTIONS]

OPTIONS:
    -Docker    Use Docker Compose for development
    -Help      Show this help message

EXAMPLES:
    powershell -ExecutionPolicy Bypass -File scripts/setup-dev-env.ps1              # Local setup
    powershell -ExecutionPolicy Bypass -File scripts/setup-dev-env.ps1 -Docker     # Docker setup

WHAT THIS SCRIPT DOES:
    1. Checks system dependencies (Node.js, Python, Docker)
    2. Installs project dependencies
    3. Sets up environment variables
    4. Initializes databases (if needed)
    5. Starts development servers

REQUIREMENTS:
    - Node.js 20+ (for frontends)
    - Python 3.11+ (for backends)
    - Docker Desktop (optional, if using -Docker)
    - Git

"@ | Write-Host
}

function Check-Dependencies {
    Write-Header "Checking System Dependencies"
    
    $missing = $false
    
    # Check Node.js
    try {
        $nodeVersion = node -v
        Write-Success "Node.js $nodeVersion found"
    } catch {
        Write-Error-Custom "Node.js not found. Install from https://nodejs.org"
        $missing = $true
    }
    
    # Check npm
    try {
        $npmVersion = npm -v
        Write-Success "npm $npmVersion found"
    } catch {
        Write-Error-Custom "npm not found"
        $missing = $true
    }
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1 | Select-String -Pattern "[\d.]+"
        Write-Success "Python $pythonVersion found"
    } catch {
        Write-Error-Custom "Python not found. Install from https://python.org"
        $missing = $true
    }
    
    # Check Git
    try {
        $gitVersion = git --version
        Write-Success "$gitVersion found"
    } catch {
        Write-Error-Custom "Git not found"
        $missing = $true
    }
    
    # Check Docker if needed
    if ($Docker) {
        try {
            $dockerVersion = docker --version
            Write-Success "$dockerVersion found"
        } catch {
            Write-Error-Custom "Docker not found. Install from https://docker.com"
            $missing = $true
        }
        
        try {
            $composeVersion = docker-compose --version
            Write-Success "$composeVersion found"
        } catch {
            Write-Error-Custom "Docker Compose not found"
            $missing = $true
        }
    }
    
    if ($missing) {
        Write-Error-Custom "Please install missing dependencies and try again"
        exit 1
    }
}

function Setup-Frontend {
    param(
        [string]$Name,
        [string]$Path
    )
    
    Write-Header "Setting up $Name Frontend"
    
    if (-not (Test-Path $Path)) {
        Write-Error-Custom "Directory not found: $Path"
        return
    }
    
    Push-Location $Path
    
    if (-not (Test-Path "node_modules")) {
        Write-Info "Installing dependencies..."
        npm install --legacy-peer-deps
        Write-Success "$Name dependencies installed"
    } else {
        Write-Info "$Name dependencies already installed"
    }
    
    Pop-Location
}

function Setup-Backend {
    param(
        [string]$Name,
        [string]$Path
    )
    
    Write-Header "Setting up $Name Backend"
    
    if (-not (Test-Path $Path)) {
        Write-Error-Custom "Directory not found: $Path"
        return
    }
    
    Push-Location $Path
    
    # Create venv if needed
    if (-not (Test-Path "venv")) {
        Write-Info "Creating Python virtual environment..."
        python -m venv venv
        Write-Success "Virtual environment created"
    }
    
    # Activate and install
    if (Test-Path "requirements.txt") {
        Write-Info "Installing Python dependencies..."
        & "venv\Scripts\activate.ps1"
        pip install -r requirements.txt
        deactivate
        Write-Success "$Name dependencies installed"
    }
    
    Pop-Location
}

function Setup-EnvFiles {
    Write-Header "Setting up Environment Variables"
    
    # Learning Finnish backend
    $finnishEnv = "learning_finnish\backend\.env"
    if (-not (Test-Path $finnishEnv)) {
        Write-Info "Creating learning_finnish backend .env"
        @"
FLASK_ENV=development
FLASK_DEBUG=1
"@ | Out-File -FilePath $finnishEnv -Encoding UTF8
        Write-Success "learning_finnish\.env created"
    }
    
    # Finance Dashboard
    $financeEnv = "Finance dashboard\.env"
    if (-not (Test-Path $financeEnv)) {
        Write-Warning-Custom "Finance dashboard .env not found"
        Write-Info "Create 'Finance dashboard\.env' with API keys"
    }
}

function Setup-Docker {
    Write-Header "Starting Docker Development Environment"
    
    if (-not (Test-Path "docker-compose.dev.yml")) {
        Write-Error-Custom "docker-compose.dev.yml not found"
        exit 1
    }
    
    Write-Info "Building and starting containers..."
    docker-compose -f docker-compose.dev.yml up -d
    
    Write-Success "Docker containers started"
    Write-Info "Check status with: docker-compose -f docker-compose.dev.yml ps"
}

function Setup-Local {
    Write-Header "Local Development Setup Complete"
    
    Write-Info "To start development servers, run:"
    Write-Host ""
    Write-Host "  Learning Finnish Frontend:"
    Write-Host "    cd learning_finnish && npm run dev"
    Write-Host "    (available at http://localhost:5173)"
    Write-Host ""
    Write-Host "  Learning Finnish Backend:"
    Write-Host "    cd learning_finnish\backend && venv\Scripts\activate && flask run"
    Write-Host "    (available at http://localhost:8000)"
    Write-Host ""
    Write-Host "  Finance Dashboard:"
    Write-Host "    cd 'Finance dashboard' && venv\Scripts\activate && flask run"
    Write-Host "    (available at http://localhost:5002)"
    Write-Host ""
    Write-Host "  Wedding:"
    Write-Host "    cd Wedding\markella-boho-celebration && npm run dev"
    Write-Host "    (available at http://localhost:5173)"
    Write-Host ""
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-Header "Development Environment Setup (Windows)"

Check-Dependencies

if ($Docker) {
    Write-Info "Using Docker Compose for development"
    Setup-Docker
} else {
    Write-Info "Setting up local development environment"
    
    # Setup frontends
    Setup-Frontend "Learning Finnish" "learning_finnish"
    Setup-Frontend "Wedding" "Wedding\markella-boho-celebration"
    
    # Setup backends
    Setup-Backend "Learning Finnish" "learning_finnish\backend"
    Setup-Backend "Finance Dashboard" "Finance dashboard"
    Setup-Backend "Housing Market" "Danish Housing Market Search"
    Setup-Backend "Website Front Page" "Website Front Page"
    
    # Setup environment files
    Setup-EnvFiles
    
    # Show instructions
    Setup-Local
}

Write-Header "Setup Complete!"
Write-Success "Development environment is ready"
Write-Info "Next: Run development servers and access http://localhost:5173"
