from __future__ import annotations
from pathlib import Path

PATH = Path(r"app\ui\main_window.py")
lines = PATH.read_text(encoding="utf-8", errors="ignore").splitlines(True)

target = "self.current_offer.items.append(new_item)"
hit = None
for i,ln in enumerate(lines):
    if target in ln:
        hit = i
        break

if hit is None:
    raise SystemExit("Anchor not found: " + target)

# detect indentation of the append line
indent = lines[hit].split(target)[0]

# if already patched, exit
window = "".join(lines[max(0,hit-3):min(len(lines),hit+3)])
if "new_item.offer_id = self.current_offer.id" in window and "self.db.add(new_item)" in window:
    print("ALREADY_PATCHED=True")
else:
    # replace single append line with 3-line block
    new_block = [
        f"{indent}new_item.offer_id = self.current_offer.id\n",
        f"{indent}self.db.add(new_item)\n",
        f"{indent}{target}\n",
    ]
    lines[hit:hit+1] = new_block
    PATH.write_text("".join(lines), encoding="utf-8", newline="\n")
    print("PATCHED=True")

# proof: print a small context around the patch
lines2 = PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
start = max(0, hit-6)
end = min(len(lines2), hit+10)
print("CONTEXT_START_LINE=", start+1)
for j in range(start, end):
    print(f"{j+1:4}: {lines2[j]}")
