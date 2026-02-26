from __future__ import annotations
from pathlib import Path
import re

ROOT = Path("app")

# Mojibake map (utf-8 -> latin1/125x bozulmaları)
MAP = {
    "Ã¼":"ü","Ãœ":"Ü",
    "Ã¶":"ö","Ã–":"Ö",
    "Ã§":"ç","Ã‡":"Ç",
    "ÄŸ":"ğ","Äž":"Ğ",
    "ÅŸ":"ş","Åž":"Ş",
    "Ä±":"ı","Ä°":"İ",
    "Â":"",  # çoğu zaman çöp karakter
    "â€“":"–","â€”":"—",
    "â€™":"'",
    "â€œ":'"',"â€�":'"',
}

def decode_bytes(b: bytes) -> str:
    # önce strict utf-8, olmazsa 1254, olmazsa 1252, en son replace
    for enc in ("utf-8", "cp1254", "cp1252"):
        try:
            return b.decode(enc, errors="strict")
        except UnicodeDecodeError:
            pass
    return b.decode("utf-8", errors="replace")

def fix_text(s: str) -> str:
    for k, v in MAP.items():
        s = s.replace(k, v)

    EURO = chr(0x20AC)  # €
    LIRA = chr(0x20BA)  # ₺

    # "EUR": "� " gibi bozulmaları düzelt (regex repl string değil, lambda!)
    s = re.sub(r'"EUR"\s*:\s*"\ufffd\s*"', lambda m: f'"EUR": "{EURO} "', s)
    s = re.sub(r'"TL"\s*:\s*"\ufffd\s*"',  lambda m: f'"TL": "{LIRA} "',  s)

    return s

def main():
    exts = {".py", ".ui", ".html", ".jinja", ".txt"}
    scanned = 0
    changed = 0

    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        scanned += 1
        b = p.read_bytes()
        t = decode_bytes(b)
        t2 = fix_text(t)
        if t2 != t:
            p.write_text(t2, encoding="utf-8", newline="\n")
            changed += 1

    # kalan şüpheli pattern taraması
    suspects = ["Ã", "Ä", "Å", "Â", "\ufffd", "â€“", "â€”", "â€™", "â€œ", "â€�"]
    bad = []
    for p in ROOT.rglob("*.py"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        if any(x in t for x in suspects):
            bad.append(p)

    print(f"SCANNED={scanned} CHANGED={changed}")
    if bad:
        print("STILL_SUSPECT_FILES:")
        for x in bad[:40]:
            print(" -", x.as_posix())
    else:
        print("OK: no suspect patterns in app/*.py")

if __name__ == "__main__":
    main()
