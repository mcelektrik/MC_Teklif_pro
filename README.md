# MC_Teklif_pro

## Setup (Windows PowerShell)

python -m venv .venv_new
.\.venv_new\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt

## Importers (idempotent + sha256 proof)

Customers:
python -m app.importers.customers_import .\customers_template.xlsx

Products:
python app\importers\products_import.py .\products_template.xlsx

## Output / Artifacts
- Runtime outputs and error reports are stored under .\_out\
- Backups are stored under .\_bak\
- These are gitignored by design.
