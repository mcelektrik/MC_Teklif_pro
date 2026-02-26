param(
  [switch]$Fresh,
  [switch]$Deterministic
)

$ErrorActionPreference="Stop"
if($Fresh -and $Deterministic){ throw "Fresh and Deterministic cannot be used together." }

# Ensure cwd = repo root
Set-Location (Split-Path -Parent $PSScriptRoot)

# Delegate to smoke.ps1
$cmd = @("powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",".\scripts\smoke.ps1")
if($Deterministic){ $cmd += "-Deterministic" }
elseif($Fresh){ $cmd += "-Fresh" }

& $cmd[0] $cmd[1] $cmd[2] $cmd[3] $cmd[4] $cmd[5] $cmd[6]
exit $LASTEXITCODE
