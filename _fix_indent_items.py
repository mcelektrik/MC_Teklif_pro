from __future__ import annotations
from pathlib import Path

PATH = Path(r"app\ui\main_window.py")
lines = PATH.read_text(encoding="utf-8", errors="ignore").splitlines(True)

# find the append line and use its leading whitespace as the canonical indent
idx = None
for i,ln in enumerate(lines):
    if "self.current_offer.items.append(new_item)" in ln:
        idx = i
        break
if idx is None:
    raise SystemExit("append line not found")

base_indent = ln.split("self.current_offer.items.append(new_item)")[0]

# look at up to 5 lines above for our injected lines; normalize their indent to base_indent
targets = ["new_item.offer_id = self.current_offer.id", "self.db.add(new_item)"]
fixed = 0
for j in range(max(0, idx-5), idx):
    s = lines[j].lstrip()
    for t in targets:
        if s.startswith(t):
            lines[j] = base_indent + t + "\n"
            fixed += 1

# also ensure the append line itself uses base indent (safety)
lines[idx] = base_indent + "self.current_offer.items.append(new_item)\n"

PATH.write_text("".join(lines), encoding="utf-8", newline="\n")
print("FIXED_LINES=", fixed)
print("APPEND_LINE=", idx+1)
