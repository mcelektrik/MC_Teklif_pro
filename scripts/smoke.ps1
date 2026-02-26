param(
  [string]$CustomersXlsx = ".\customers_template.xlsx",
  [string]$ProductsXlsx  = ".\products_template.xlsx",
  [switch]$Fresh,
  [switch]$Deterministic
)

$ErrorActionPreference="Stop"
$py=".\.venv_new\Scripts\python.exe"; if(!(Test-Path $py)){$py="python"}

Write-Host "== SMOKE =="

& $py -m compileall -q app
Write-Host "OK: compileall"

& $py -m app.importers.customers_import $CustomersXlsx
& $py app\importers\products_import.py $ProductsXlsx


Write-Host "== SMOKE_OFFER =="
if ($Deterministic) {
  & $py .\scripts\smoke_offer.py --deterministic
} elseif ($Fresh) {
  & $py .\scripts\smoke_offer.py --fresh
} else {
  & $py .\scripts\smoke_offer.py
}
Write-Host "OK: smoke_offer"

Write-Host "== DB_COUNTS =="
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\db_counts.ps1
Write-Host "OK: db_counts"
Write-Host "SMOKE_OK"

