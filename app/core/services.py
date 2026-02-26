from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.schema import Offer

def generate_offer_no(db: Session) -> str:
    """
    Generates a new offer number in the format Q-YYYY-000001.
    Resets the counter every year.
    """
    current_year = datetime.now().year
    prefix = f"Q-{current_year}-"
    
    # Find the latest offer number for the current year
    last_offer = db.query(Offer).filter(
        Offer.offer_no.like(f"{prefix}%")
    ).order_by(Offer.offer_no.desc()).first()
    
    if last_offer and last_offer.offer_no:
        try:
            last_seq = int(last_offer.offer_no.split("-")[-1])
            new_seq = last_seq + 1
        except ValueError:
            new_seq = 1
    else:
        new_seq = 1
        
    return f"{prefix}{new_seq:06d}"

def calculate_offer_totals(offer: Offer):
    """
    Calculates the totals for an offer based on its items.
    Updates the offer object in place (does not commit).
    """
    sub_total = 0.0
    discount_total = 0.0
    vat_total = 0.0
    
    for item in offer.items:
        # Calculate item total
        gross_amount = item.quantity * item.unit_price
        item_discount = gross_amount * (item.discount_percent / 100.0)
        net_amount = gross_amount - item_discount
        
        # Calculate VAT
        if offer.include_vat:
            # If unit price includes VAT, we need to extract it
            # Net Amount is inclusive of VAT
            # VAT = Net Amount - (Net Amount / (1 + VAT Rate/100))
            item_vat = net_amount - (net_amount / (1 + item.vat_rate / 100.0))
            item_sub_total = net_amount - item_vat
        else:
            # VAT is added on top
            item_vat = net_amount * (item.vat_rate / 100.0)
            item_sub_total = net_amount
            
        item.total_price = net_amount if offer.include_vat else (net_amount + item_vat)
        
        sub_total += item_sub_total
        discount_total += item_discount
        vat_total += item_vat
        
    offer.sub_total = sub_total
    offer.discount_total = discount_total
    offer.vat_total = vat_total
    offer.grand_total = sub_total + vat_total # Logic depends on how we want to show it
    
    # To be consistent with display:
    # Subtotal (Net)
    # + VAT
    # = Grand Total
    # Discount is already deducted from Subtotal in this logic? 
    # Usually: 
    # Gross Total: sum(qty * price)
    # Discount Total: sum(discount)
    # Net Subtotal: Gross - Discount
    # VAT Total: sum(VAT on Net Subtotal)
    # Grand Total: Net Subtotal + VAT Total
    
    # Let's refine based on "include_vat"
    
    raw_sub_total = 0.0 # Sum of (qty * unit_price) before discount
    total_discount = 0.0
    total_vat = 0.0
    
    for item in offer.items:
        line_gross = item.quantity * item.unit_price
        line_discount = line_gross * (item.discount_percent / 100.0)
        line_net = line_gross - line_discount
        
        if offer.include_vat:
            # line_net includes VAT
            base_amount = line_net / (1 + item.vat_rate / 100.0)
            line_vat = line_net - base_amount
        else:
            # line_net excludes VAT
            base_amount = line_net
            line_vat = base_amount * (item.vat_rate / 100.0)
            
        raw_sub_total += base_amount # Sum of base amounts
        total_discount += (line_gross - line_net) # This is tricky if VAT included
        # Better: just sum base amounts
        
        total_vat += line_vat
        
    # Re-calculating to be precise
    # We will store:
    # sub_total: Sum of base amounts (excluding VAT)
    # discount_total: This is hard to represent if unit price includes VAT. 
    # Let's simplify: 
    # If include_vat: unit_price is VAT inclusive. 
    # If exclude_vat: unit_price is VAT exclusive.
    
    current_sub_total = 0.0
    current_vat_total = 0.0
    current_discount_total = 0.0
    
    for item in offer.items:
        qty = item.quantity
        price = item.unit_price
        disc_rate = item.discount_percent
        vat_rate = item.vat_rate
        
        gross = qty * price
        discount_amount = gross * (disc_rate / 100.0)
        net_after_discount = gross - discount_amount
        
        if offer.include_vat:
            # net_after_discount includes VAT
            # Tax Base = Net / (1 + VAT%)
            tax_base = net_after_discount / (1 + vat_rate / 100.0)
            vat_amount = net_after_discount - tax_base
            
            # Item Total Price (for display) usually includes VAT if that's the mode
            item.total_price = net_after_discount
        else:
            # net_after_discount excludes VAT
            tax_base = net_after_discount
            vat_amount = tax_base * (vat_rate / 100.0)
            
            item.total_price = tax_base + vat_amount
            
        current_sub_total += tax_base
        current_vat_total += vat_amount
        
        # Discount total is approximate if VAT included, but usually we just want to know how much was shaved off the list price
        # If list price included VAT, the discount also "includes" VAT reduction.
        # Let's just sum the raw discount amount calculated from unit price
        current_discount_total += discount_amount

    offer.sub_total = current_sub_total
    offer.vat_total = current_vat_total
    offer.grand_total = current_sub_total + current_vat_total
    offer.discount_total = current_discount_total
