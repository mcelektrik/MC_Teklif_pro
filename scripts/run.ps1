param(
  [switch]$Fresh
)

$ErrorActionPreference="Stop"

# Activate venv if present
if(Test-Path ".\.venv_new\Scripts\Activate.ps1"){ . .\.venv_new\Scripts\Activate.ps1 }

# Safety: block tracked/stray BAK artifacts outside _bak
$bakOutside = Get-ChildItem -Recurse -File -Filter "*.BAK_*" |
  Where-Object { $_.FullName -notlike "*\_bak\*" }
if($bakOutside.Count -ne 0){
  Write-Host "ERROR: BAK files found outside _bak. Move them into _bak or delete before running."
  $bakOutside | Select-Object -ExpandProperty FullName | ForEach-Object { " - $_" }
  exit 2
}

# Delegate to smoke
if($Fresh){
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke.ps1 -Fresh
} else {
  powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke.ps1
}

Write-Host "RUN_OK"
