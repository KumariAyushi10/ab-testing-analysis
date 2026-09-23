"""
00_create_db.py
------------------------------------------------------------
Loads data/ab_test_sessions.csv into a SQLite database
(data/novacart_ab_test.db) so the .sql analysis queries in this
folder can be run with any SQLite client (DB Browser for SQLite,
the `sqlite3` command line tool, VS Code SQLite extension, etc).

SQLite is used because it needs no server install -- perfect for
a portfolio project anyone can open with a single file.
------------------------------------------------------------
"""

import sqlite3
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "..", "data", "ab_test_sessions.csv")
DB_PATH = os.path.join(SCRIPT_DIR, "..", "data", "novacart_ab_test.db")

df = pd.read_csv(CSV_PATH)

conn = sqlite3.connect(DB_PATH)
df.to_sql("ab_test_sessions", conn, if_exists="replace", index=False)

# Helpful indexes for the SQL analysis queries
cur = conn.cursor()
cur.execute("CREATE INDEX IF NOT EXISTS idx_group ON ab_test_sessions(test_group);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_device ON ab_test_sessions(device_type);")
conn.commit()

print(f"Loaded {len(df):,} rows into {DB_PATH}, table ab_test_sessions")
conn.close()
