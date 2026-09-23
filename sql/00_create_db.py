import sqlite3
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "..", "data", "ab_test_sessions.csv")
DB_PATH = os.path.join(SCRIPT_DIR, "..", "data", "novacart_ab_test.db")

df = pd.read_csv(CSV_PATH)

conn = sqlite3.connect(DB_PATH)
df.to_sql("ab_test_sessions", conn, if_exists="replace", index=False)


cur = conn.cursor()
cur.execute("CREATE INDEX IF NOT EXISTS idx_group ON ab_test_sessions(test_group);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_device ON ab_test_sessions(device_type);")
conn.commit()

print(f"Loaded {len(df):,} rows into {DB_PATH}, table ab_test_sessions")
conn.close()
