"""Direct database inspection."""
import sqlite3

# Connect to the actual database file
db_path = 'game_reviews.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"Database file: {db_path}")
print(f"Tables found: {len(tables)}\n")

for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    
    print(f"Table: {table_name} ({count} rows)")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    print()

conn.close()
