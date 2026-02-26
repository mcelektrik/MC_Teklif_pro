$ErrorActionPreference="Stop"
if(Test-Path ".\.venv_new\Scripts\Activate.ps1"){ . .\.venv_new\Scripts\Activate.ps1 }
python -c "from app.core.db import SessionLocal; from app.core.schema import Customer, Product; s=SessionLocal(); print('customers=', s.query(Customer).count()); print('products=', s.query(Product).count()); s.close()"
