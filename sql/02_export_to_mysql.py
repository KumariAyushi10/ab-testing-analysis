"""
02_export_to_mysql.py
------------------------------------------------------------
Generates sql/mysql_import.sql -- a MySQL-compatible SQL script
that creates the ab_test_sessions table and inserts all 20,000
rows using efficient multi-row INSERT statements.

This lets you use MySQL Workbench (or any MySQL server) instead
of SQLite:

  1. Open MySQL Workbench, connect to your local MySQL server
  2. Create a new schema (database), e.g. "novacart_ab_test"
  3. File -> Open SQL Script -> select sql/mysql_import.sql
  4. Click the lightning bolt (Execute) to run the whole script
  5. The ab_test_sessions table will appear under your schema,
     fully populated -- then run sql/01_analysis_queries.sql
     against it (the queries are plain ANSI SQL and work in
     both SQLite and MySQL unmodified).
------------------------------------------------------------
"""

import pandas as pd

CSV_PATH = "/home/claude/ab_test_project/data/ab_test_sessions.csv"
OUT_PATH = "/home/claude/ab_test_project/sql/mysql_import.sql"

df = pd.read_csv(CSV_PATH)

lines = []
lines.append("-- ============================================================")
lines.append("-- NovaCart A/B Test -- MySQL import script")
lines.append("-- Generated from data/ab_test_sessions.csv")
lines.append("-- Run this whole file in MySQL Workbench (Execute / lightning bolt icon)")
lines.append("-- ============================================================")
lines.append("")
lines.append("CREATE DATABASE IF NOT EXISTS novacart_ab_test;")
lines.append("USE novacart_ab_test;")
lines.append("")
lines.append("DROP TABLE IF EXISTS ab_test_sessions;")
lines.append("""CREATE TABLE ab_test_sessions (
    user_id INT NOT NULL,
    session_timestamp DATETIME NOT NULL,
    test_group VARCHAR(1) NOT NULL,
    device_type VARCHAR(20) NOT NULL,
    country VARCHAR(5) NOT NULL,
    traffic_source VARCHAR(20) NOT NULL,
    new_visitor TINYINT NOT NULL,
    added_to_cart TINYINT NOT NULL,
    checkout_time_seconds DECIMAL(6,1) NOT NULL,
    converted TINYINT NOT NULL,
    order_value_usd DECIMAL(8,2) NOT NULL,
    items_in_cart INT NOT NULL,
    abandoned_cart TINYINT NOT NULL,
    PRIMARY KEY (user_id, session_timestamp)
);""")
lines.append("")
lines.append("CREATE INDEX idx_group ON ab_test_sessions(test_group);")
lines.append("CREATE INDEX idx_device ON ab_test_sessions(device_type);")
lines.append("")

cols = list(df.columns)
col_list = ", ".join(cols)

BATCH_SIZE = 500
n = len(df)

def sql_escape(val, col):
    if col in ("test_group", "device_type", "country", "traffic_source", "session_timestamp"):
        return "'" + str(val).replace("'", "''") + "'"
    return str(val)

for start in range(0, n, BATCH_SIZE):
    chunk = df.iloc[start:start + BATCH_SIZE]
    value_rows = []
    for row in chunk.itertuples(index=False):
        vals = [sql_escape(getattr(row, c), c) for c in cols]
        value_rows.append("(" + ", ".join(vals) + ")")
    stmt = f"INSERT INTO ab_test_sessions ({col_list}) VALUES\n" + ",\n".join(value_rows) + ";"
    lines.append(stmt)
    lines.append("")

lines.append("-- Done. 20,000 rows loaded into ab_test_sessions.")
lines.append("-- Now run the queries in sql/01_analysis_queries.sql against this table.")

with open(OUT_PATH, "w") as f:
    f.write("\n".join(lines))

print(f"Saved MySQL import script to {OUT_PATH}")
print(f"File size: {sum(len(l) for l in lines) / 1024:.1f} KB (approx)")
