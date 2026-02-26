from app.core.schema import Offer, OfferItem
from app.core.services import calculate_offer_totals

def test_calc_totals_vat_included():
    offer = Offer(include_vat=True)
    # Item: 100 TL (inc VAT), 1 qty, 20% VAT
    item = OfferItem(
        quantity=1,
        unit_price=120.0, # 100 + 20 VAT
        vat_rate=20.0,
        discount_percent=0.0
    )
    offer.items = [item]
    
    calculate_offer_totals(offer)
    
    # Expected:
    # Net: 100.0
    # VAT: 20.0
    # Total: 120.0
    assert abs(offer.sub_total - 100.0) < 0.01
    assert abs(offer.vat_total - 20.0) < 0.01
    assert abs(offer.grand_total - 120.0) < 0.01

def test_calc_totals_vat_excluded():
    offer = Offer(include_vat=False)
    # Item: 100 TL (ex VAT), 1 qty, 20% VAT
    item = OfferItem(
        quantity=1,
        unit_price=100.0,
        vat_rate=20.0,
        discount_percent=0.0
    )
    offer.items = [item]
    
    calculate_offer_totals(offer)
    
    # Expected:
    # Net: 100.0
    # VAT: 20.0
    # Total: 120.0
    assert abs(offer.sub_total - 100.0) < 0.01
    assert abs(offer.vat_total - 20.0) < 0.01
    assert abs(offer.grand_total - 120.0) < 0.01

def test_calc_totals_discount():
    offer = Offer(include_vat=False)
    # Item: 100 TL, 10% discount
    item = OfferItem(
        quantity=1,
        unit_price=100.0,
        vat_rate=20.0,
        discount_percent=10.0
    )
    offer.items = [item]
    
    calculate_offer_totals(offer)
    
    # Gross: 100
    # Discount: 10
    # Net: 90
    # VAT: 18 (20% of 90)
    # Total: 108
    
    assert abs(offer.discount_total - 10.0) < 0.01
    assert abs(offer.sub_total - 90.0) < 0.01
    assert abs(offer.vat_total - 18.0) < 0.01
    assert abs(offer.grand_total - 108.0) < 0.01
