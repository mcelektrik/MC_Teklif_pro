from __future__ import annotations
from pathlib import Path

PATH = Path(r"app\ui\main_window.py")
src = PATH.read_text(encoding="utf-8", errors="ignore").splitlines(True)

out=[]
i=0
removed=0
inserted=0

while i < len(src):
    ln = src[i]

    # remove any previously injected broken lines (wherever they are)
    if ln.lstrip().startswith("new_item.offer_id = self.current_offer.id"):
        removed += 1; i += 1; continue
    if ln.lstrip().startswith("self.db.add(new_item)"):
        removed += 1; i += 1; continue
    if "self.current_offer.items.append(new_item)" in ln:
        # drop append usage entirely
        removed += 1; i += 1; continue

    out.append(ln)

    # after finishing the OfferItem(...) constructor, insert correct persistence lines
    # pattern:
    #   new_item = OfferItem(
    #       ...
    #   )
    # We detect the closing line that is just ')', but only when we are inside a new_item constructor.
    if "new_item = OfferItem(" in ln:
        # scan forward until we see a line that starts with same indent + ")"
        indent = ln.split("new_item = OfferItem(")[0]
        j = i+1
        while j < len(src):
            out.append(src[j])
            if src[j].strip() == ")" and src[j].startswith(indent):
                # insert right after the closing paren line, at SAME indent level as new_item assignment line
                out.append(f"{indent}new_item.offer_id = self.current_offer.id\n")
                out.append(f"{indent}self.db.add(new_item)\n")
                inserted += 1
                i = j  # will be incremented below
                break
            j += 1
    i += 1

PATH.write_text("".join(out), encoding="utf-8", newline="\n")
print("REMOVED=", removed)
print("INSERTED_BLOCKS=", inserted)
