import pytest
import os
import shutil
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.schema import Base, Offer, Customer
from app.core.settings import DB_PATH
import app.core.settings

# Use an in-memory SQLite database for tests
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def patch_documents_dir(tmp_path):
    # Patch DOCUMENTS_DIR to point to a temp dir
    original_dir = app.core.settings.DOCUMENTS_DIR
    app.core.settings.DOCUMENTS_DIR = tmp_path / "Documents"
    app.core.settings.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Restore
    app.core.settings.DOCUMENTS_DIR = original_dir
