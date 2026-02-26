param(
  [switch]$Fresh
)

$ErrorActionPreference="Stop"

$sw = [System.Diagnostics.Stopwatch]::StartNew()

# Ensure cwd = repo root
Set-Location (Split-Path -Parent $PSScriptRoot)

# Activate venv if present
if(Test-Path ".\.venv_new\Scripts\Activate.ps1"){ . .\.venv_new\Scripts\Activate.ps1 }

# Repo metadata
$branch = (git rev-parse --abbrev-ref HEAD 2>$null).Trim()
$commit = (git rev-parse --short HEAD 2>$null).Trim()

# BAK guard
$bakOutside = Get-ChildItem -Recurse -File -Filter "*.BAK_*" |
  Where-Object { $_.FullName -notlike "*\_bak\*" }
if($bakOutside.Count -ne 0){
  Write-Host "ERROR: BAK files found outside _bak. Clean before CI."
  $bakOutside | Select-Object -ExpandProperty FullName | ForEach-Object { " - $_" }
  exit 2
}

# Logs + summary dirs
$logDir = ".\_out\logs"
$sumDir = ".\_out\ci_summary"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
New-Item -ItemType Directory -Force -Path $sumDir | Out-Null

$stamp = Get-Date -Format yyyyMMdd_HHmmss
$logAbs = Join-Path (Resolve-Path $logDir).Path ("CI_{0}.log" -f $stamp)
$sumAbs = Join-Path (Resolve-Path $sumDir).Path ("CI_SUMMARY_{0}.json" -f $stamp)

# Python metadata (best effort)
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
$pyVer = ""
try { $pyVer = (python -V 2>&1).ToString().Trim() } catch { $pyVer = "" }

Write-Host "== CI START =="
Write-Host ("ROOT   = {0}" -f (Get-Location))
Write-Host ("BRANCH = {0}" -f $branch)
Write-Host ("COMMIT = {0}" -f $commit)
Write-Host ("FRESH  = {0}" -f ([bool]$Fresh))
Write-Host ("PY     = {0}" -f $py)
Write-Host ("PYVER  = {0}" -f $pyVer)
Write-Host ("LOG    = {0}" -f $logAbs)
Write-Host ("SUMMARY= {0}" -f $sumAbs)

# Run runner and tee all output
$cmd = @("powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",".\scripts\run.ps1")
if($Fresh){ $cmd += "-Fresh" }

$out = & $cmd[0] $cmd[1] $cmd[2] $cmd[3] $cmd[4] $cmd[5] $cmd[6] 2>&1
$out | Tee-Object -FilePath $logAbs | Out-Host
$exit = $LASTEXITCODE

# Extract key proofs from output (best effort)
$customers = $null
$products  = $null
$offerLine = $null

foreach($ln in $out){
  if($ln -match '^\s*customers=\s*(\d+)\s*$'){ $customers = [int]$Matches[1] }
  if($ln -match '^\s*products=\s*(\d+)\s*$'){  $products  = [int]$Matches[1] }
  if(($ln -is [string]) -and $ln.TrimStart().StartsWith("{'offer_id':")){
    $offerLine = $ln.Trim()
  }
}

$sw.Stop()

# Build summary object
$summary = [ordered]@{
  stamp_istanbul = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
  branch         = $branch
  commit         = $commit
  fresh          = [bool]$Fresh
  exit_code      = $exit
  duration_ms    = [int]$sw.ElapsedMilliseconds
  log_path       = $logAbs
  summary_path   = $sumAbs
  python         = $py
  python_version = $pyVer
  db_counts      = [ordered]@{
    customers = $customers
    products  = $products
  }
  smoke_offer_line = $offerLine
}

# Write summary JSON (always)
($summary | ConvertTo-Json -Depth 6) | Set-Content -Encoding UTF8 $sumAbs

# Update LATEST summary (always)
$latest = Join-Path (Resolve-Path $sumDir).Path "CI_SUMMARY_LATEST.json"
Copy-Item $sumAbs $latest -Force

if($exit -ne 0){
  Write-Error ("CI_FAIL exit={0}" -f $exit)
  exit $exit
}

Write-Host "CI_PASS"
exit 0


