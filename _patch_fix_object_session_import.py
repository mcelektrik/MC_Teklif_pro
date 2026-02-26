from __future__ import annotations
from pathlib import Path
import re

PATH = Path(r"app\ui\main_window.py")
txt = PATH.read_text(encoding="utf-8", errors="ignore")
orig = txt

# remove ANY standalone object_session import lines (we'll re-add cleanly)
txt = re.sub(r"^\s*from\s+sqlalchemy\.orm\s+import\s+object_session\s*$\n?", "", txt, flags=re.M)

# if there is a sqlalchemy.orm import line, append object_session safely
m = re.search(r"^from\s+sqlalchemy\.orm\s+import\s+([^\n]+)$", txt, flags=re.M)
if m:
    line = m.group(0)
    if "object_session" not in line:
        txt = txt.replace(line, line.rstrip() + ", object_session", 1)
else:
    # insert after initial import block (from/import lines at top), else at top
    mtop = re.search(r"^(?:from\s+[^\n]+\n|import\s+[^\n]+\n)+", txt, flags=re.M)
    ins = mtop.end() if mtop else 0
    txt = txt[:ins] + "from sqlalchemy.orm import object_session\n" + txt[ins:]

PATH.write_text(txt, encoding="utf-8", newline="\n")
print("CHANGED=", (txt != orig))
print("HAS_OBJECT_SESSION_IMPORT=", ("object_session" in txt))
