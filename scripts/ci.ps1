param(
  [switch]$Fresh
)

$ErrorActionPreference="Stop"

# Ensure cwd = repo root
Set-Location (Split-Path -Parent $PSScriptRoot)

# Activate venv if present
if(Test-Path ".\.venv_new\Scripts\Activate.ps1"){ . .\.venv_new\Scripts\Activate.ps1 }

# BAK guard
$bakOutside = Get-ChildItem -Recurse -File -Filter "*.BAK_*" |
  Where-Object { $_.FullName -notlike "*\_bak\*" }
if($bakOutside.Count -ne 0){
  Write-Host "ERROR: BAK files found outside _bak. Clean before CI."
  $bakOutside | Select-Object -ExpandProperty FullName | ForEach-Object { " - $_" }
  exit 2
}

# Logs
$outDir = ".\_out\logs"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$stamp = Get-Date -Format yyyyMMdd_HHmmss
$log = Join-Path $outDir ("CI_{0}.log" -f $stamp)

# Run
Write-Host "== CI START =="
Write-Host ("ROOT = {0}" -f (Get-Location))
Write-Host ("LOG  = {0}" -f $log)

$cmd = @("powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",".\scripts\run.ps1")
if($Fresh){ $cmd += "-Fresh" }

# tee output to log, preserve exit code
& $cmd[0] $cmd[1] $cmd[2] $cmd[3] $cmd[4] $cmd[5] $cmd[6] 2>&1 | Tee-Object -FilePath $log
$exit = $LASTEXITCODE
if($exit -ne 0){
  Write-Host ("CI_FAIL exit={0}" -f $exit)
  exit $exit
}

Write-Host "CI_PASS"
exit 0
