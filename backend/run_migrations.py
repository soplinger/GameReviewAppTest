"""Run Alembic migrations programmatically."""
from alembic.config import Config
from alembic import command

# Create Alembic configuration
alembic_cfg = Config("alembic.ini")

# Run migrations to head
print("Running migrations to head...")
command.upgrade(alembic_cfg, "head")
print("✓ Migrations complete!")
