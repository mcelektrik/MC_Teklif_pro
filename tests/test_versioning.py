import os
import shutil
from pathlib import Path
from datetime import datetime
from app.core.schema import Offer, Customer
from app.pdf.render import generate_pdf
from app.core.settings import DOCUMENTS_DIR

def test_pdf_versioning(db_session):
    # Setup
    customer = Customer(name="Test Customer")
    offer = Offer(
        offer_no="Q-2024-TEST", 
        customer=customer,
        created_at=datetime.now()
    )
    db_session.add(customer)
    db_session.add(offer)
    db_session.flush()
    
    settings = {
        "company_name": "Test Co",
        "company_address": "Test Addr",
        "company_phone": "123",
        "company_tax_no": "111",
        "company_iban": "TR123"
    }
    
    # Create first PDF
    path1 = generate_pdf(offer, settings)
    assert path1.exists()
    assert str(path1).endswith(".pdf")
    
    # Create second PDF (should be v2)
    path2 = generate_pdf(offer, settings)
    assert path2.exists()
    assert "_v2.pdf" in str(path2)
    
    # Cleanup
    if path1.exists(): os.remove(path1)
    if path2.exists(): os.remove(path2)
    # Clean directory if empty
    try:
        os.rmdir(path1.parent)
    except:
        pass
