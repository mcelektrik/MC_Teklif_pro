from __future__ import annotations
from pathlib import Path

PATH = Path(r"app\ui\main_window.py")
lines = PATH.read_text(encoding="utf-8", errors="ignore").splitlines(True)

def find_first(substr: str):
    for i,ln in enumerate(lines):
        if substr in ln:
            return i
    return None

# Insert at start of save_draft try block
idx = find_first("def save_draft(self):")
if idx is None:
    raise SystemExit("save_draft not found")

# find the line with 'try:' right after def save_draft
idx_try = None
for i in range(idx, min(len(lines), idx+20)):
    if lines[i].lstrip().startswith("try:"):
        idx_try = i
        break
if idx_try is None:
    raise SystemExit("try: in save_draft not found")

indent = lines[idx_try].split("try:")[0]

marker1 = f"{indent}    logger.info('DEBUG_SAVE_DRAFT_ENTER offer_id=%s items_model=%s', getattr(self.current_offer,'id',None), len(getattr(self.items_model,'items',[]) or []))\n"
# prevent double insert
window = "".join(lines[max(0,idx_try-2):min(len(lines),idx_try+8)])
if "DEBUG_SAVE_DRAFT_ENTER" not in window:
    lines.insert(idx_try+1, marker1)

# After commit(), add marker
idx_commit = find_first("self.db.commit()")
if idx_commit is not None:
    ind2 = lines[idx_commit].split("self.db.commit()")[0]
    marker2 = f"{ind2}logger.info('DEBUG_SAVE_DRAFT_COMMIT_OK offer_id=%s', getattr(self.current_offer,'id',None))\n"
    win2 = "".join(lines[max(0,idx_commit-2):min(len(lines),idx_commit+3)])
    if "DEBUG_SAVE_DRAFT_COMMIT_OK" not in win2:
        lines.insert(idx_commit+1, marker2)

# In except block, upgrade to exception log with marker
idx_exc = find_first("except Exception as e:")
if idx_exc is not None:
    ind3 = lines[idx_exc].split("except Exception as e:")[0]
    marker3 = f"{ind3}    logger.exception('DEBUG_SAVE_DRAFT_EXCEPTION')\n"
    win3 = "".join(lines[max(0,idx_exc):min(len(lines),idx_exc+6)])
    if "DEBUG_SAVE_DRAFT_EXCEPTION" not in win3:
        lines.insert(idx_exc+1, marker3)

PATH.write_text("".join(lines), encoding="utf-8", newline="\n")
print("DEBUG_PATCHED_OK=True")
