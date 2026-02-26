# Setup Script for MC_Teklif_Pro
Write-Host "Setting up MC_Teklif_Pro Development Environment..." -ForegroundColor Cyan

# Check if venv exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Define python path
$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Python executable not found at $Python"
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..."
& $Python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..."
# Use --force-reinstall to avoid issues with editable installs in some envs
# But --no-deps to avoid re-downloading everything
try {
    & $Python -m pip install -e .
} catch {
    Write-Warning "Failed to install editable package. Attempting to continue..."
}

# Install Playwright browsers
Write-Host "Installing Playwright browsers..."
# Set path to local directory to avoid permission issues in sandbox/restricted envs
$env:PLAYWRIGHT_BROWSERS_PATH = (Join-Path (Get-Location) "browsers")
& $Python -m playwright install chromium

# Compile python files to check for syntax errors
Write-Host "Compiling Python files..."
& $Python -m py_compile app/main.py

# Run tests (if any exist yet)
if (Test-Path "tests") {
    Write-Host "Running tests..."
    & $Python -m pytest
}

Write-Host "DEV_OK" -ForegroundColor Green
