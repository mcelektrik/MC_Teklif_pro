# Build Script for MC_Teklif_Pro
$ErrorActionPreference = "Stop"

Write-Host "Building MC_Teklif_Pro..." -ForegroundColor Cyan

# Ensure we are in the project root
$ProjectRoot = (Get-Item -Path ".\").FullName
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build"
$StagingDir = Join-Path $ProjectRoot "staging"

# Clean previous builds
if (Test-Path $DistDir) { Remove-Item -Path $DistDir -Recurse -Force }
if (Test-Path $BuildDir) { Remove-Item -Path $BuildDir -Recurse -Force }
if (Test-Path $StagingDir) { Remove-Item -Path $StagingDir -Recurse -Force }

New-Item -ItemType Directory -Path $StagingDir | Out-Null

# 1. Run PyInstaller
Write-Host "Running PyInstaller..."
# We need to include templates and assets
# app/pdf/templates -> app/pdf/templates
# app/pdf/assets -> app/pdf/assets
# We use --add-data. On Windows it uses ; as separator.

$DataArgs = @(
    "--add-data", "app/pdf/templates;app/pdf/templates",
    "--add-data", "app/pdf/assets;app/pdf/assets"
)

# Use python -m PyInstaller to ensure we use the venv one
python -m PyInstaller --noconfirm --onefile --windowed --name "MC_Teklif_Pro" `
    --clean @DataArgs `
    app/main.py

if (-not (Test-Path "dist\MC_Teklif_Pro.exe")) {
    Write-Error "PyInstaller failed to create executable."
}

# Copy executable to staging
Copy-Item "dist\MC_Teklif_Pro.exe" $StagingDir

# 2. Handle Playwright Browsers
Write-Host "Locating Playwright browsers..."
# Default location on Windows
$PlaywrightPath = "$env:LOCALAPPDATA\ms-playwright"

if (-not (Test-Path $PlaywrightPath)) {
    Write-Warning "Playwright browsers not found at default location: $PlaywrightPath"
    Write-Warning "Attempting to install..."
    playwright install chromium
}

if (Test-Path $PlaywrightPath) {
    Write-Host "Copying Playwright browsers to staging..."
    # We only need chromium for this app
    $ChromiumPath = Get-ChildItem -Path $PlaywrightPath -Filter "chromium-*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($ChromiumPath) {
        $DestPath = Join-Path $StagingDir "ms-playwright"
        New-Item -ItemType Directory -Path $DestPath | Out-Null
        # Copy the chromium folder
        Copy-Item -Path $ChromiumPath.FullName -Destination $DestPath -Recurse
        Write-Host "Copied $($ChromiumPath.Name)"
    } else {
        Write-Error "Could not find chromium in $PlaywrightPath"
    }
} else {
    Write-Error "Playwright browsers not found."
}

# 3. Run Inno Setup
Write-Host "Running Inno Setup..."
$InnoCompiler = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if (-not (Test-Path $InnoCompiler)) {
    Write-Warning "Inno Setup Compiler not found at $InnoCompiler"
    Write-Warning "Please install Inno Setup 6 or update the path in build.ps1"
    Write-Warning "Skipping installer generation."
} else {
    $IssFile = Join-Path $ProjectRoot "installer\MC_Teklif_Pro.iss"
    # We need to pass the StagingDir to Inno Setup. 
    # Inno Setup supports /D definitions.
    
    & $InnoCompiler "/DStagingDir=$StagingDir" $IssFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installer created successfully in dist_installer!" -ForegroundColor Green
    } else {
        Write-Error "Inno Setup failed."
    }
}

Write-Host "Build Complete."
