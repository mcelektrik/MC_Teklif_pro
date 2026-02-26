param(
  [string]$CustomersXlsx = ".\customers_template.xlsx",
  [string]$ProductsXlsx  = ".\products_template.xlsx"
)

$ErrorActionPreference="Stop"
$py=".\.venv_new\Scripts\python.exe"; if(!(Test-Path $py)){$py="python"}

Write-Host "== SMOKE =="

& $py -m compileall -q app
Write-Host "OK: compileall"

& $py -m app.importers.customers_import $CustomersXlsx
& $py app\importers\products_import.py $ProductsXlsx

Write-Host "SMOKE_OK"
