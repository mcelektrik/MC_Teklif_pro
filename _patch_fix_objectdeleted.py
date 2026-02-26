from __future__ import annotations
from pathlib import Path
import re

PATH = Path(r"app\ui\main_window.py")
txt = PATH.read_text(encoding="utf-8", errors="ignore")

# 1) ensure SimpleNamespace import (top-level)
if "SimpleNamespace" not in txt:
    m = re.search(r"^(import\s+[^\n]+\n)+", txt, flags=re.M)
    ins = m.end() if m else 0
    txt = txt[:ins] + "from types import SimpleNamespace\n" + txt[ins:]

# 2) Locate our rewritten block anchor line
needle = "for item in (self.items_model.items or []):"
if needle not in txt:
    raise SystemExit("Anchor not found: " + needle)

# 3) Replace loop header with snapshot-building + loop over snapshot
# Also reset UI list to detached objects to avoid ObjectDeletedError in Qt model
replacement = (
    "ui_items = []\n"
    "            for _it in (self.items_model.items or []):\n"
    "                ui_items.append({\n"
    "                    'description': getattr(_it, 'description', ''),\n"
    "                    'quantity': getattr(_it, 'quantity', 0),\n"
    "                    'unit': getattr(_it, 'unit', ''),\n"
    "                    'unit_price': getattr(_it, 'unit_price', 0),\n"
    "                    'vat_rate': getattr(_it, 'vat_rate', 0),\n"
    "                    'discount_percent': getattr(_it, 'discount_percent', 0),\n"
    "                })\n"
    "            # detach UI from ORM objects (prevents ObjectDeletedError after bulk delete)\n"
    "            self.items_model.items = [SimpleNamespace(**d) for d in ui_items]\n"
    "            try:\n"
    "                self.items_model.layoutChanged.emit()\n"
    "            except Exception:\n"
    "                pass\n"
    "\n"
    "            for item in ui_items:\n"
)

# preserve indentation by taking indent from the existing needle line
lines = txt.splitlines(True)
idx = None
for i,ln in enumerate(lines):
    if needle in ln:
        idx = i
        base_indent = ln.split(needle)[0]
        break
if idx is None:
    raise SystemExit("needle line not found in splitlines")

rep_lines = []
for ln in replacement.splitlines(True):
    # indent all replacement lines with base_indent
    rep_lines.append(base_indent + ln if ln.strip() != "" else "\n")

# replace the single line containing the needle
lines[idx:idx+1] = rep_lines
txt2 = "".join(lines)

# 4) Adjust OfferItem constructor attribute access: item is now dict
# Replace item.description -> item['description'] etc only inside our block by simple global safe replacements
txt2 = txt2.replace("description=item.description", "description=item.get('description','')")
txt2 = txt2.replace("quantity=item.quantity", "quantity=item.get('quantity',0)")
txt2 = txt2.replace("unit=item.unit", "unit=item.get('unit','')")
txt2 = txt2.replace("unit_price=item.unit_price", "unit_price=item.get('unit_price',0)")
txt2 = txt2.replace("vat_rate=item.vat_rate", "vat_rate=item.get('vat_rate',0)")
txt2 = txt2.replace("discount_percent=item.discount_percent", "discount_percent=item.get('discount_percent',0)")

PATH.write_text(txt2, encoding="utf-8")
print("PATCH_OBJECTDELETED_OK=True")
