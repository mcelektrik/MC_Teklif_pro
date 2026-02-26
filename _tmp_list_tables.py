import sqlite3
from app.core.db import DB_PATH

p = str(DB_PATH)
con = sqlite3.connect(p)
rows = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print("DB_PATH =", p)
print("TABLES  =", [r[0] for r in rows])
con.close()
