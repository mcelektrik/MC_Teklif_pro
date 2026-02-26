$ErrorActionPreference="Stop"
if(Test-Path ".\.venv_new\Scripts\Activate.ps1"){ . .\.venv_new\Scripts\Activate.ps1 }
python -m compileall -q app
python -m app.importers.customers_import .\customers_template.xlsx
python app\importers\products_import.py .\products_template.xlsx
Write-Host "RUN_OK"
