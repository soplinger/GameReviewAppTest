"""Manually fix the alembic version table."""
import sqlite3
from alembic.config import Config
from alembic import command

# Connect to database
conn = sqlite3.connect('game_reviews.db')
cursor = conn.cursor()

# Check what tables exist
tables = [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"Existing tables: {tables}\n")

# Create alembic_version table manually if it doesn't exist
if 'alembic_version' not in tables:
    print("Creating alembic_version table...")
    cursor.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))")
    conn.commit()

# Check if we have users and games tables
has_users = 'users' in tables
has_games = 'games' in tables

# Set the appropriate version
if has_users and has_games:
    # We have both users and games, set to games migration
    version = 'b1f4e2d3c5a6'
    print(f"Database has users and games tables, setting version to {version}")
elif has_users:
    # We only have users, set to initial migration
    version = 'aaecd3683a34'
    print(f"Database has users table only, setting version to {version}")
else:
    version = None
    print("No existing tables found")

if version:
    # Delete any existing version
    cursor.execute("DELETE FROM alembic_version")
    # Insert the correct version
    cursor.execute("INSERT INTO alembic_version (version_num) VALUES (?)", (version,))
    conn.commit()
    print(f"✓ Set alembic_version to {version}\n")

conn.close()

# Now run migrations to head
print("Running migrations to head...")
alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")
print("\n✓ All migrations complete!")

# Verify final state
conn = sqlite3.connect('game_reviews.db')
cursor = conn.cursor()
tables = [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
version_result = cursor.execute("SELECT * FROM alembic_version").fetchone()
print(f"\nFinal state:")
print(f"  Tables: {sorted(tables)}")
print(f"  Alembic version: {version_result[0] if version_result else 'None'}")

# Check if reviews table exists
if 'reviews' in tables:
    columns = cursor.execute("PRAGMA table_info(reviews)").fetchall()
    print(f"\n✓ Reviews table created with {len(columns)} columns")

conn.close()
