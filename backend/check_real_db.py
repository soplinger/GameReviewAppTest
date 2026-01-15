"""Check the correct database file."""
import sqlite3

conn = sqlite3.connect('database/game_review.db')
cursor = conn.cursor()

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
print(f"Tables in database/game_review.db: {[t[0] for t in tables]}\n")

for table in tables:
    table_name = table[0]
    count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"{table_name}: {count} rows")

    if table_name == 'alembic_version':
        version = cursor.execute("SELECT * FROM alembic_version").fetchone()
        if version:
            print(f"  Current version: {version[0]}")

conn.close()
