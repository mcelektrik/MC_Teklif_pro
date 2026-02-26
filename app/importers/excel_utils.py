from __future__ import annotations
from typing import Any

BAD_MARKERS = ("Ã","Ä","Å","Â","�","ƒ","†","â")

def norm_str(x: Any) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    if s.upper() == "TL":
        return "TRY"
    return s

def norm_currency(x: Any) -> str:
    s = norm_str(x).upper()
    if s in ("TL", "TRY"):
        return "TRY"
    if s in ("USD", "EUR"):
        return s
    return s

def norm_float(x: Any) -> float | None:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None

def is_note_row(stok_kodu: Any) -> bool:
    sc = norm_str(stok_kodu)
    if not sc:
        return True
    if sc.upper().startswith("NOTLAR"):
        return True
    return False
