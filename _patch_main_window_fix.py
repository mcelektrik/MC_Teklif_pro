from __future__ import annotations
from pathlib import Path
import re

PATH = Path(r"app\ui\main_window.py")

# --- Mojibake fixes: common UTF-8->Latin1 garbling for TR chars + a few punctuation artifacts
REPL = {
    "Ã§":"ç","Ã‡":"Ç",
    "ÄŸ":"ğ","Äž":"Ğ",
    "Ä±":"ı","Ä°":"İ",
    "Ã¶":"ö","Ã–":"Ö",
    "Ã¼":"ü","Ãœ":"Ü",
    "ÅŸ":"ş","Åž":"Ş",
    "Â ":" ", "Â ":" ", "Â":"",   # stray NBSP / Â artifacts
    "â€™":"’","â€˜":"‘",
    "â€œ":"“","â€�":"”",
    "â€“":"–","â€”":"—",
    "â€¦":"…",
}

txt = PATH.read_text(encoding="utf-8", errors="ignore")
orig = txt

for a,b in REPL.items():
    txt = txt.replace(a,b)

# --- Add object_session import if missing
# We'll add: from sqlalchemy.orm import object_session
if "object_session" not in txt:
    # try to attach to an existing sqlalchemy.orm import line
    m = re.search(r"^from\s+sqlalchemy\.orm\s+import\s+([^\n]+)$", txt, flags=re.M)
    if m:
        line = m.group(0)
        if "object_session" not in line:
            new_line = line.rstrip() + ", object_session"
            txt = txt.replace(line, new_line, 1)
    else:
        # fallback: insert after 'from sqlalchemy import ...' or near top imports
        ins_at = None
        m2 = re.search(r"^from\s+sqlalchemy\s+import\s+[^\n]+\n", txt, flags=re.M)
        if m2:
            ins_at = m2.end()
        else:
            m3 = re.search(r"^(import\s+[^\n]+\n)+", txt, flags=re.M)
            ins_at = m3.end() if m3 else 0
        txt = txt[:ins_at] + "from sqlalchemy.orm import object_session\n" + txt[ins_at:]

# --- Guard before self.db.flush() inside the area where offer/items are being persisted
# We only inject once: just before the first occurrence of "self.db.flush()" AFTER a line that mentions "Offer" or "offer"
lines = txt.splitlines(True)
out = []
injected = False

for i,ln in enumerate(lines):
    # heuristic: if this line flushes and we recently saw 'offer' variable, inject guard
    if (not injected) and ("self.db.flush()" in ln):
        # look back a few lines for "offer" usage
        window = "".join(lines[max(0,i-12):i]).lower()
        if "offer" in window:
            indent = re.match(r"^(\s*)", ln).group(1)
            out.append(f"{indent}# ensure Offer is in session (prevents SAWarning)\n")
            out.append(f"{indent}try:\n")
            out.append(f"{indent}    _os = object_session(offer)\n")
            out.append(f"{indent}except Exception:\n")
            out.append(f"{indent}    _os = None\n")
            out.append(f"{indent}if _os is None:\n")
            out.append(f"{indent}    self.db.add(offer)\n")
            injected = True
    out.append(ln)

txt2 = "".join(out)

# write back UTF-8 no BOM
PATH.write_text(txt2, encoding="utf-8", newline="\n")

print("CHANGED=", (txt2 != orig))
print("INJECTED_GUARD=", injected)
print("HAS_MOJIBAKE_NOW=", any(x in txt2 for x in ["Ã","Ä","Å","Â","�"]))
