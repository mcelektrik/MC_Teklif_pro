from __future__ import annotations
from pathlib import Path

PATH = Path(r"app\ui\main_window.py")
lines = PATH.read_text(encoding="utf-8", errors="ignore").splitlines(True)

def find_first(substr: str):
    for i,ln in enumerate(lines):
        if substr in ln:
            return i
    return None

# 1) enter marker right after "try:" inside save_draft
i_def = find_first("def save_draft(self):")
if i_def is None: raise SystemExit("save_draft not found")

i_try = None
for i in range(i_def, min(len(lines), i_def+40)):
    if lines[i].lstrip().startswith("try:"):
        i_try = i
        break
if i_try is None: raise SystemExit("save_draft try: not found")

indent_try = lines[i_try].split("try:")[0]
enter = f"{indent_try}    logger.info('DEBUG_SAVE_ENTER offer_id=%s ui_items=%s', getattr(self.current_offer,'id',None), len(getattr(self.items_model,'items',[]) or []))\n"
win = "".join(lines[i_try:i_try+6])
if "DEBUG_SAVE_ENTER" not in win:
    lines.insert(i_try+1, enter)

# 2) inside loop, increment counter
i_for = find_first("for item in self.items_model.items:")
if i_for is None: raise SystemExit("items loop not found")
indent_for = lines[i_for].split("for item in self.items_model.items:")[0]
# init counter just before loop
init_counter = f"{indent_for}item_n = 0\n"
if "item_n = 0" not in "".join(lines[max(0,i_for-5):i_for+1]):
    lines.insert(i_for, init_counter)
    i_for += 1

# after we add(new_item), bump counter and log once per save (not per item too noisy)
i_add = find_first("self.db.add(new_item)")
if i_add is None: raise SystemExit("self.db.add(new_item) not found (persist rewrite missing)")
indent_add = lines[i_add].split("self.db.add(new_item)")[0]
bump = f"{indent_add}item_n += 1\n"
if "item_n +=" not in "".join(lines[i_add:i_add+3]):
    lines.insert(i_add+1, bump)

# 3) after commit, log counter and db count for this offer
i_commit = find_first("self.db.commit()")
if i_commit is None: raise SystemExit("commit not found")
indent_commit = lines[i_commit].split("self.db.commit()")[0]
after = (
    f"{indent_commit}logger.info('DEBUG_SAVE_COMMIT_OK offer_id=%s wrote_items=%s', getattr(self.current_offer,'id',None), locals().get('item_n',None))\n"
)
if "DEBUG_SAVE_COMMIT_OK" not in "".join(lines[i_commit:i_commit+5]):
    lines.insert(i_commit+1, after)

PATH.write_text("".join(lines), encoding="utf-8", newline="\n")
print("DEBUG_ITEMS_PATCHED=True")
