import os
import sys
from pathlib import Path

APP_NAME = "MC_Teklif_Pro"

# Determine AppData path
if sys.platform == "win32":
    APPDATA = os.getenv("APPDATA")
    USERPROFILE = os.getenv("USERPROFILE")
else:
    APPDATA = os.path.expanduser("~/.config")
    USERPROFILE = os.path.expanduser("~")

APP_DIR = Path(APPDATA) / APP_NAME
DB_PATH = APP_DIR / "mc_teklif.db"
BACKUP_DIR = APP_DIR / "backups"
LOG_DIR = APP_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

# PDF Output Directory
DOCUMENTS_DIR = Path(USERPROFILE) / "Documents" / "MC_Teklif"

# Ensure directories exist
def ensure_directories():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

# Application Settings Keys
class AppSettings:
    COMPANY_NAME = "company_name"
    COMPANY_ADDRESS = "company_address"
    COMPANY_TAX_NO = "company_tax_no"
    COMPANY_PHONE = "company_phone"
    COMPANY_IBAN = "company_iban"
    LOGO_PATH = "logo_path"
    SIGNATURE_PATH = "signature_path"
    DEFAULT_VAT_RATE = "default_vat_rate"
