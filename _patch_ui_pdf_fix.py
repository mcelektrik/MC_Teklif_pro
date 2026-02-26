from __future__ import annotations
from pathlib import Path

PATH = Path(r"app\ui\main_window.py")
txt = PATH.read_text(encoding="utf-8", errors="ignore")
orig = txt

# --- A) Fix broken Turkish UI literals (common ones you reported)
# We patch only if the broken forms exist.
repls = [
    ("M'TERİ BİLGİLERİ", "MÜŞTERİ BİLGİLERİ"),
    ("M'TERİ", "MÜŞTERİ"),
    ("AD/'NVAN", "AD/ÜNVAN"),
    ("Ad/'nvan", "Ad/Ünvan"),
    ("SE'İLİ SATR SİL", "SEÇİLİ SATIR SİL"),
    ("Se'ili Satır Sil", "Seçili Satır Sil"),
    ("SATIR", "SATIR"),  # no-op; keeps list readable
]

for a,b in repls:
    if a in txt:
        txt = txt.replace(a,b)

# If you had a few other common corruptions (Ç->' , Ü->' etc.) inside specific known labels:
# patch only those specific phrases, not globally.

# --- B) Add "Yetkili Kişi" UI field if missing
# Anchor: existing customer form row for tax_no usually exists:
anchor = "cust_form.addRow(\"Vergi No\", self.cust_tax_no)"
if "self.cust_contact" not in txt:
    if anchor in txt:
        insert = (
            "        self.cust_contact = QLineEdit()\n"
            "        cust_form.addRow(\"Yetkili Kişi\", self.cust_contact)\n"
        )
        # place it right after tax_no widget creation block; best effort: after self.cust_tax_no init
        # fallback: insert after anchor row so it shows under Vergi No.
        txt = txt.replace(anchor, anchor + "\n" + insert, 1)

# Also load/save it best-effort if Customer has a field; we won't assume schema.
# We'll just store it in address text if no field exists? -> NO. Keep UI only for now.

# --- C) Stop OfferItem accumulation: delete old items in DB when saving existing draft
# Anchor: "self.current_offer.items = [] # Clear and re-add (simple way)"
needle = "self.current_offer.items = [] # Clear and re-add (simple way)"
if needle in txt and "DELETE_OLD_ITEMS_FOR_OFFER" not in txt:
    block = (
        "            # DELETE_OLD_ITEMS_FOR_OFFER (prevents item accumulation / huge PDFs)\n"
        "            if self.current_offer.id:\n"
        "                try:\n"
        "                    self.db.query(OfferItem).filter(OfferItem.offer_id == self.current_offer.id).delete(synchronize_session=False)\n"
        "                    self.db.flush()\n"
        "                except Exception:\n"
        "                    # if schema differs, keep going; relationship clear below will still work for in-memory\n"
        "                    pass\n"
        "\n"
    )
    txt = txt.replace(needle, block + "            " + needle, 1)

# --- D) When loading an existing draft into UI, try to populate cust_contact if available on Customer
# We'll do soft getattr to avoid crashes.
if "self.cust_contact.setText" not in txt:
    # anchor near other customer setText calls (name/address/tax_office/tax_no)
    a2 = "self.cust_tax_no.setText(draft.customer.tax_no)"
    if a2 in txt:
        ins2 = (
            a2 + "\n"
            "                    if hasattr(self, 'cust_contact'):\n"
            "                        self.cust_contact.setText(getattr(draft.customer, 'contact_person', '') or getattr(draft.customer, 'contact', '') or '')"
        )
        txt = txt.replace(a2, ins2, 1)

# --- E) On save, read cust_contact and try to persist if model has a field; best effort.
# anchor where customer.tax_no set
a3 = "customer.tax_no = self.cust_tax_no.text()"
if a3 in txt and "customer.contact_person" not in txt:
    ins3 = (
        a3 + "\n"
        "            # best-effort: persist 'Yetkili Kişi' if field exists\n"
        "            if hasattr(customer, 'contact_person') and hasattr(self, 'cust_contact'):\n"
        "                customer.contact_person = self.cust_contact.text()\n"
        "            elif hasattr(customer, 'contact') and hasattr(self, 'cust_contact'):\n"
        "                customer.contact = self.cust_contact.text()\n"
    )
    txt = txt.replace(a3, ins3, 1)

PATH.write_text(txt, encoding="utf-8", newline="\n")

print("CHANGED=", (txt != orig))
print("HAS_BROKEN_MTERI=", ("M'TER" in txt))
print("HAS_BROKEN_ADUNVAN=", ("AD/'" in txt))
print("HAS_BROKEN_SECILI=", ("SE'" in txt))
print("HAS_CUST_CONTACT_UI=", ("cust_contact" in txt))
print("HAS_DELETE_OLD_ITEMS_PATCH=", ("DELETE_OLD_ITEMS_FOR_OFFER" in txt))
