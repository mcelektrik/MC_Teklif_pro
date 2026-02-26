import shutil
import glob
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import DB_PATH, BACKUP_DIR
from app.core.schema import Base

# SQLite URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def backup_db():
    """
    Backs up the database to the backup directory.
    Keeps only the last 7 backups.
    """
    if not os.path.exists(DB_PATH):
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"mc_teklif_{timestamp}.db"
    
    try:
        shutil.copy2(DB_PATH, backup_file)
        
        # Cleanup old backups (keep last 7)
        backups = sorted(glob.glob(str(BACKUP_DIR / "mc_teklif_*.db")))
        if len(backups) > 7:
            for old_backup in backups[:-7]:
                os.remove(old_backup)
    except Exception as e:
        print(f"Backup failed: {e}")
def ensure_directories():
    pass
