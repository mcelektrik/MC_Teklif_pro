from __future__ import annotations
from pathlib import Path

PATH = Path(r"app\ui\main_window.py")
src = PATH.read_text(encoding="utf-8", errors="ignore").splitlines(True)

# Find anchors inside save_draft: "# Update Items" and "calculate_offer_totals(self.current_offer)"
start = None
end = None
for i,ln in enumerate(src):
    if "# Update Items" in ln:
        start = i
        break
if start is None:
    raise SystemExit("Anchor not found: # Update Items")

for j in range(start, len(src)):
    if "calculate_offer_totals(self.current_offer)" in src[j]:
        end = j
        break
if end is None:
    raise SystemExit("Anchor not found: calculate_offer_totals(self.current_offer)")

indent = src[start].split("#")[0]

block = []
block.append(f"{indent}# Update Items (safe, offer_id-based)\n")
block.append(f"{indent}# ensure offer is in session + has PK\n")
block.append(f"{indent}try:\n")
block.append(f"{indent}    _os = object_session(self.current_offer)\n")
block.append(f"{indent}except Exception:\n")
block.append(f"{indent}    _os = None\n")
block.append(f"{indent}if _os is None:\n")
block.append(f"{indent}    self.db.add(self.current_offer)\n")
block.append(f"{indent}    self.db.flush()\n")
block.append(f"{indent}\n")
block.append(f"{indent}# delete old items in DB to prevent accumulation\n")
block.append(f"{indent}self.db.query(OfferItem).filter(OfferItem.offer_id == self.current_offer.id).delete(synchronize_session=False)\n")
block.append(f"{indent}self.db.expire_all()\n")
block.append(f"{indent}\n")
block.append(f"{indent}item_n = 0\n")
block.append(f"{indent}for item in (self.items_model.items or []):\n")
block.append(f"{indent}    new_item = OfferItem(\n")
block.append(f"{indent}        offer_id=self.current_offer.id,\n")
block.append(f"{indent}        description=item.description,\n")
block.append(f"{indent}        quantity=item.quantity,\n")
block.append(f"{indent}        unit=item.unit,\n")
block.append(f"{indent}        unit_price=item.unit_price,\n")
block.append(f"{indent}        vat_rate=item.vat_rate,\n")
block.append(f"{indent}        discount_percent=item.discount_percent\n")
block.append(f"{indent}    )\n")
block.append(f"{indent}    self.db.add(new_item)\n")
block.append(f"{indent}    item_n += 1\n")
block.append(f"{indent}logger.info('DEBUG_SAVE_ITEMS_WRITTEN offer_id=%s n=%s', self.current_offer.id, item_n)\n")
block.append(f"{indent}\n")

out = src[:start] + block + src[end:]
PATH.write_text("".join(out), encoding="utf-8")
print("REWROTE_ITEMS_BLOCK=True")
print("START_LINE=", start+1, "END_LINE=", end+1)
