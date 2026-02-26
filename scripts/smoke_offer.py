from __future__ import annotations

from datetime import datetime
import argparse
from app.core.db import SessionLocal
from app.core.schema import Customer, Product, Offer, OfferItem

def calc_totals(offer: Offer):
    sub_total = 0.0
    discount_total = 0.0
    vat_total = 0.0
    grand_total = 0.0

    include_vat = bool(getattr(offer, "include_vat", True))

    for it in offer.items:
        qty = float(it.quantity or 0.0)
        unit_price = float(it.unit_price or 0.0)
        vat_rate = float(it.vat_rate or 0.0)
        disc = float(it.discount_percent or 0.0)

        if qty <= 0:
            continue

        gross_line = qty * unit_price
        disc_amt = gross_line * (disc / 100.0) if disc > 0 else 0.0
        gross_after_disc = gross_line - disc_amt

        if include_vat:
            # unit_price is VAT-included
            denom = (1.0 + vat_rate / 100.0) if vat_rate is not None else 1.0
            net = gross_after_disc / denom if denom else gross_after_disc
            vat = gross_after_disc - net
            sub_total += net
            vat_total += vat
            discount_total += disc_amt
            grand_total += gross_after_disc
            it.total_price = gross_after_disc
        else:
            # unit_price is VAT-excluded
            net = gross_after_disc
            vat = net * (vat_rate / 100.0) if vat_rate else 0.0
            sub_total += net
            vat_total += vat
            discount_total += disc_amt
            grand_total += (net + vat)
            it.total_price = net + vat

    offer.sub_total = round(sub_total, 2)
    offer.discount_total = round(discount_total, 2)
    offer.vat_total = round(vat_total, 2)
    offer.grand_total = round(grand_total, 2)

def main():
    db = SessionLocal()
    try:
        c = db.query(Customer).order_by(Customer.id.asc()).first()
        p = db.query(Product).order_by(Product.id.asc()).first()

        if not c:
            raise SystemExit("NO_CUSTOMER: customers table empty (import customers first)")
        if not p:
            raise SystemExit("NO_PRODUCT: products table empty (import products first)")

        # args
        parser = argparse.ArgumentParser()
        parser.add_argument("--fresh", action="store_true", help="Create a unique SMOKE offer_no (timestamped).")
        parser.add_argument("--deterministic", action="store_true", help="Use fixed offer_no and fixed data for deterministic CI runs.")
        args, _ = parser.parse_known_args()

        # offer_no
        # offer_no
        if args.deterministic:
            offer_no = "SMOKE-DETERMINISTIC"
        else:
            fmt = "%Y%m%d-%H%M%S" if args.fresh else "%Y%m%d"
            offer_no = "SMOKE-" + datetime.now().strftime(fmt)
        o = db.query(Offer).filter(Offer.offer_no == offer_no).one_or_none()

        created = False
        if not o:
            o = Offer(
                customer_id=c.id,
                offer_no=offer_no,
                currency=getattr(p, "currency", "TRY") or "TRY",
                include_vat=True,
                status="DRAFT",
                note="SMOKE OFFER (auto-generated)"
            )
            db.add(o)
            db.flush()
            created = True

        # idempotent item: one line with description=product name
        desc = f"{p.stock_code} - {p.name}"
        it = (
            db.query(OfferItem)
            .filter(OfferItem.offer_id == o.id, OfferItem.description == desc)
            .one_or_none()
        )

        inserted_item = False
        if not it:
            it = OfferItem(
                offer_id=o.id,
                description=desc,
                quantity=2.0,
                unit=getattr(p, "unit", None) or "Adet",
                unit_price=float(getattr(p, "sale_price", 0.0) or 0.0),
                vat_rate=float(getattr(p, "vat_rate", 20.0) or 20.0),
                discount_percent=0.0,
            )
            db.add(it)
            db.flush()
            inserted_item = True

        # refresh relationship list
        db.refresh(o)
        calc_totals(o)
        db.commit()

        # proof output
        print({
            "offer_id": o.id,
            "offer_no": o.offer_no,
            "customer_id": o.customer_id,
            "currency": o.currency,
            "include_vat": o.include_vat,
            "status": o.status,
            "items_count": len(o.items),
            "created_offer": created,
            "inserted_item": inserted_item,
            "sub_total": o.sub_total,
            "discount_total": o.discount_total,
            "vat_total": o.vat_total,
            "grand_total": o.grand_total,
        })

    finally:
        db.close()

if __name__ == "__main__":
    main()




