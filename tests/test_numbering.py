from app.core.services import generate_offer_no
from app.core.schema import Offer
from datetime import datetime

def test_generate_offer_no_initial(db_session):
    # Test initial number generation
    offer_no = generate_offer_no(db_session)
    current_year = datetime.now().year
    assert offer_no == f"Q-{current_year}-000001"

def test_generate_offer_no_increment(db_session):
    # Create an existing offer
    current_year = datetime.now().year
    offer = Offer(offer_no=f"Q-{current_year}-000001")
    db_session.add(offer)
    db_session.commit()
    
    # Generate next number
    next_no = generate_offer_no(db_session)
    assert next_no == f"Q-{current_year}-000002"

def test_generate_offer_no_new_year(db_session):
    # Create an offer from last year
    last_year = datetime.now().year - 1
    offer = Offer(offer_no=f"Q-{last_year}-000005")
    db_session.add(offer)
    db_session.commit()
    
    # Generate new number for current year (should reset)
    current_year = datetime.now().year
    next_no = generate_offer_no(db_session)
    assert next_no == f"Q-{current_year}-000001"
