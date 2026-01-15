"""Stamp the alembic version for the existing database."""
import sqlite3

conn = sqlite3.connect('database/game_review.db')
cursor = conn.cursor()

# The database has users, games, and reviews tables
# The latest migration is c3f5d7e9b2a4 (reviews table)
version = 'c3f5d7e9b2a4'

print("Setting alembic version to:", version)
cursor.execute("DELETE FROM alembic_version")
cursor.execute("INSERT INTO alembic_version (version_num) VALUES (?)", (version,))
conn.commit()

result = cursor.execute("SELECT * FROM alembic_version").fetchone()
print(f"✓ Alembic version set to: {result[0]}")

conn.close()
