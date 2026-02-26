from __future__ import annotations
from pathlib import Path
import re

PATH = Path(r"app\ui\main_window.py")
txt = PATH.read_text(encoding="utf-8", errors="ignore")

# ---- A) Mojibake fix (line-based, latin1->utf8 decode up to 2 passes only on suspicious lines)
bad_markers = ("Ã","Ä","Å","Â","�","ƒ","†","â")
lines = txt.splitlines(True)
fixed = []
changed_moj = False

def fix_line(s: str) -> str:
    t = s
    for _ in range(2):
        if any(m in t for m in bad_markers):
            try:
                t2 = t.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
            except Exception:
                break
            if t2 == t:
                break
            t = t2
        else:
            break
    return t

for ln in lines:
    if any(m in ln for m in bad_markers):
        nl = fix_line(ln)
        if nl != ln:
            changed_moj = True
        fixed.append(nl)
    else:
        fixed.append(ln)

txt = "".join(fixed)

# ---- B) Ensure object_session import exists (correct way)
if "object_session" not in txt:
    m = re.search(r"^from\s+sqlalchemy\.orm\s+import\s+([^\n]+)$", txt, flags=re.M)
    if m:
        line = m.group(0)
        if "object_session" not in line:
            txt = txt.replace(line, line.rstrip() + ", object_session", 1)
    else:
        # insert near the top (after first block of imports)
        m3 = re.search(r"^(?:from\s+[^\n]+\n|import\s+[^\n]+\n)+", txt, flags=re.M)
        ins = m3.end() if m3 else 0
        txt = txt[:ins] + "from sqlalchemy.orm import object_session\n" + txt[ins:]

# ---- C) Remove WRONG previously-injected block if it exists (anything referencing object_session(offer) / self.db.add(offer))
txt_before = txt
txt = re.sub(
    r"\n[ \t]*# ensure Offer is in session \(prevents SAWarning\)\n"
    r"[ \t]*try:\n[ \t]*\s*_os = object_session\(offer\)\n"
    r"[ \t]*except Exception:\n[ \t]*\s*_os = None\n"
    r"[ \t]*if _os is None:\n[ \t]*\s*self\.db\.add\(offer\)\n",
    "\n",
    txt,
    flags=re.M
)

# ---- D) Insert CORRECT guard using self.current_offer, right before clearing/re-adding items
# We anchor on: "self.current_offer.items = []"
needle = "self.current_offer.items = []"
if needle not in txt:
    raise SystemExit("Anchor not found: 'self.current_offer.items = []'")

# only insert once
if "object_session(self.current_offer)" not in txt:
    txt = txt.replace(
        needle,
        (
            "# ensure Offer is in session BEFORE touching relationship items (prevents SAWarning)\n"
            "            try:\n"
            "                _os = object_session(self.current_offer)\n"
            "            except Exception:\n"
            "                _os = None\n"
            "            if _os is None:\n"
            "                self.db.add(self.current_offer)\n"
            "                self.db.flush()  # allocate PK for relationship rows\n"
            "\n"
            "            " + needle
        ),
        1
    )

# write back UTF-8 no BOM, normalize newlines
PATH.write_text(txt, encoding="utf-8", newline="\n")

print("MOJIBAKE_CHANGED=", changed_moj)
print("HAS_MOJIBAKE_NOW=", any(m in txt for m in bad_markers))
print("GUARD_OK=", "object_session(self.current_offer)" in txt)
print("REMOVED_BAD_GUARD=", ("object_session(offer)" not in txt))
