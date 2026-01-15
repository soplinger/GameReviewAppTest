"""Fix database migration state and apply pending migrations."""
import sqlite3
from alembic.config import Config
from alembic import command

# First, check what tables exist
conn = sqlite3.connect('game_reviews.db')
cursor = conn.cursor()
tables = [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"Existing tables: {tables}\n")

# Check if alembic_version exists
has_alembic_version = 'alembic_version' in tables
has_users = 'users' in tables
has_games = 'games' in tables
has_reviews = 'reviews' in tables

print(f"Has alembic_version: {has_alembic_version}")
print(f"Has users table: {has_users}")
print(f"Has games table: {has_games}")
print(f"Has reviews table: {has_reviews}\n")

conn.close()

# Create Alembic configuration
alembic_cfg = Config("alembic.ini")

if not has_alembic_version:
    # If no alembic_version table, we need to stamp the database
    if has_users and has_games:
        # Database has users and games, stamp with the games migration
        print("Stamping database with games migration (b1f4e2d3c5a6)...")
        command.stamp(alembic_cfg, "b1f4e2d3c5a6")
    elif has_users:
        # Database has only users, stamp with initial migration
        print("Stamping database with initial migration (aaecd3683a34)...")
        command.stamp(alembic_cfg, "aaecd3683a34")
    else:
        # Clean database, stamp with base
        print("Stamping clean database with base...")
        command.stamp(alembic_cfg, "base")

# Now run migrations to head (this should only apply pending migrations)
print("\nRunning pending migrations to head...")
command.upgrade(alembic_cfg, "head")
print("\n✓ All migrations complete!")

# Verify final state
conn = sqlite3.connect('game_reviews.db')
cursor = conn.cursor()
tables = [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
version = cursor.execute("SELECT * FROM alembic_version").fetchone()
print(f"\nFinal state:")
print(f"  Tables: {tables}")
print(f"  Alembic version: {version[0] if version else 'None'}")
conn.close()
