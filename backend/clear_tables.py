#!/usr/bin/env python3
"""
Script to clear games and reviews tables for fresh IGDB import
"""

import asyncio
import sys
from pathlib import Path

# Add src to path so we can import modules
sys.path.append(str(Path(__file__).parent / "src"))

from sqlalchemy import text
from src.core.database import AsyncSessionLocal


async def clear_tables():
    """Clear games and reviews tables."""
    async with AsyncSessionLocal() as session:
        try:
            print("Clearing tables...")
            
            # Clear reviews first due to foreign key constraint
            await session.execute(text("DELETE FROM reviews"))
            print("✓ Cleared reviews table")
            
            # Clear games
            await session.execute(text("DELETE FROM games"))
            print("✓ Cleared games table")
            
            # Try to reset auto-increment counters (sqlite_sequence may not exist)
            try:
                await session.execute(text("DELETE FROM sqlite_sequence WHERE name IN ('games', 'reviews')"))
                print("✓ Reset auto-increment counters")
            except Exception:
                print("ℹ Auto-increment counters not reset (no sqlite_sequence table)")
            
            await session.commit()
            print("✅ All tables cleared successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error clearing tables: {e}")
            raise


async def main():
    """Main function."""
    try:
        await clear_tables()
    except Exception as e:
        print(f"Failed to clear tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())