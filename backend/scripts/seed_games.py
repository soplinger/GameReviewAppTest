"""Seed database with initial game data from IGDB.

This script fetches popular games from IGDB and stores them in the database.
Run this after initial setup to populate the game catalog.

Usage:
    python scripts/seed_games.py [--limit LIMIT]
"""

import asyncio
import sys
from pathlib import Path

# Add backend/src to Python path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

from argparse import ArgumentParser

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import Base
from models.game import Game
from repositories.game_repository import GameRepository
from services.external.igdb_client import IGDBClient
from services.game_data_service import GameDataService


async def seed_games(limit: int = 100):
    """Seed database with popular games from IGDB.
    
    Args:
        limit: Number of games to seed (max: 500 per run due to API limits)
    """
    logger.info(f"Starting game seeding process for {limit} games...")
    
    # Create async engine and session
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create services
        game_repo = GameRepository(session)
        igdb_client = IGDBClient()
        game_service = GameDataService(game_repo, igdb_client=igdb_client)
        
        # Sync popular games
        synced_count = await game_service.sync_popular_games(limit=limit)
        
        logger.info(f"Successfully seeded {synced_count} games")
        
        # Get total game count
        total_games = await game_repo.count()
        logger.info(f"Total games in database: {total_games}")
    
    await engine.dispose()


async def seed_recent_games(days: int = 90, limit: int = 100):
    """Seed database with recently released games.
    
    Args:
        days: Number of days to look back for releases
        limit: Number of games to fetch
    """
    logger.info(f"Seeding recent games from last {days} days...")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        igdb_client = IGDBClient()
        game_repo = GameRepository(session)
        game_service = GameDataService(game_repo, igdb_client=igdb_client)
        
        # Fetch recent games from IGDB
        try:
            recent_games = await igdb_client.get_recent_games(days=days, limit=limit)
            synced = 0
            
            for igdb_data in recent_games:
                igdb_id = igdb_data.get("id")
                if not igdb_id:
                    continue
                
                # Check if already exists
                existing = await game_repo.get_by_igdb_id(igdb_id)
                if not existing:
                    # Transform and create
                    game_data = game_service._transform_igdb_game(igdb_data)
                    await game_repo.create(game_data)
                    synced += 1
            
            logger.info(f"Seeded {synced} recent games")
            total_games = await game_repo.count()
            logger.info(f"Total games in database: {total_games}")
        except Exception as e:
            logger.error(f"Failed to seed recent games: {e}")
    
    await engine.dispose()


def main():
    """Main entry point for seeding script."""
    parser = ArgumentParser(description="Seed database with game data from IGDB")
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of games to seed (default: 100, max: 500)",
    )
    parser.add_argument(
        "--recent",
        action="store_true",
        help="Seed recent games instead of popular games",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Days to look back for recent games (default: 90)",
    )
    
    args = parser.parse_args()
    
    # Validate limit
    if args.limit > 500:
        logger.warning("Limit capped at 500 due to IGDB API restrictions")
        args.limit = 500
    
    # Run seeding
    try:
        if args.recent:
            asyncio.run(seed_recent_games(days=args.days, limit=args.limit))
        else:
            asyncio.run(seed_games(limit=args.limit))
        logger.success("Game seeding completed successfully!")
    except Exception as e:
        logger.error(f"Game seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
