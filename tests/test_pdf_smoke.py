import os
import pytest
from datetime import datetime
from app.core.schema import Offer, Customer, OfferItem
from app.pdf.render import generate_pdf

def test_pdf_smoke(db_session):
    # Create a minimal valid offer
    customer = Customer(name="Smoke Test Customer")
    offer = Offer(
        offer_no="Q-SMOKE-001",
        customer=customer,
        created_at=datetime.now(),
        sub_total=100.0,
        vat_total=20.0,
        grand_total=120.0
    )
    item = OfferItem(
        description="Test Item",
        quantity=1,
        unit="Adet",
        unit_price=100.0,
        total_price=120.0
    )
    offer.items.append(item)
    
    db_session.add(customer)
    db_session.add(offer)
    db_session.flush()
    
    settings = {
        "company_name": "Smoke Co"
    }
    
    # Generate PDF
    try:
        path = generate_pdf(offer, settings)
        assert path.exists()
        assert path.stat().st_size > 0
        
        # Cleanup
        os.remove(path)
        try:
            os.rmdir(path.parent)
        except:
            pass
    except Exception as e:
        pytest.fail(f"PDF generation failed: {e}")
