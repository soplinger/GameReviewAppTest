"""Incremental sync script for updating game data.

This script updates stale game records and fetches newly released games.
Run this daily via cron job or scheduled task to keep game data fresh.

Usage:
    python scripts/sync_games.py [--days DAYS] [--batch-size SIZE]
"""

import asyncio
import sys
from datetime import datetime
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
from repositories.game_repository import GameRepository
from services.external.igdb_client import IGDBClient
from services.game_data_service import GameDataService


async def sync_stale_games(stale_days: int = 30, batch_size: int = 50):
    """Update games that haven't been synced in N days.
    
    Args:
        stale_days: Days since last sync to consider stale
        batch_size: Number of games to update per batch
    """
    logger.info(f"Syncing games older than {stale_days} days...")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        game_repo = GameRepository(session)
        igdb_client = IGDBClient()
        game_service = GameDataService(game_repo, igdb_client=igdb_client)
        
        # Get stale games
        stale_games = await game_repo.get_stale_games(
            days=stale_days, limit=batch_size
        )
        
        if not stale_games:
            logger.info("No stale games found")
            await engine.dispose()
            return
        
        logger.info(f"Found {len(stale_games)} stale games to update")
        
        updated = 0
        failed = 0
        
        for game in stale_games:
            try:
                # Fetch fresh data from IGDB
                if game.igdb_id:
                    igdb_data = await igdb_client.get_game_by_id(game.igdb_id)
                    if igdb_data:
                        game_data = game_service._transform_igdb_game(igdb_data)
                        await game_repo.update(game.id, game_data)
                        updated += 1
                        logger.debug(f"Updated game: {game.name}")
                    else:
                        logger.warning(f"No data found for game ID {game.igdb_id}")
                        # Update sync timestamp even if no data
                        await game_repo.update_sync_timestamp(game.id)
                        failed += 1
                else:
                    logger.warning(f"Game {game.name} has no IGDB ID, skipping")
                    failed += 1
            except Exception as e:
                logger.error(f"Failed to update game {game.name}: {e}")
                failed += 1
        
        logger.info(f"Sync complete: {updated} updated, {failed} failed")
    
    await engine.dispose()


async def fetch_new_releases(days: int = 7, limit: int = 50):
    """Fetch games released in the last N days.
    
    Args:
        days: Number of days to look back
        limit: Maximum number of new releases to fetch
    """
    logger.info(f"Fetching games released in last {days} days...")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        game_repo = GameRepository(session)
        igdb_client = IGDBClient()
        game_service = GameDataService(game_repo, igdb_client=igdb_client)
        
        try:
            recent_games = await igdb_client.get_recent_games(days=days, limit=limit)
            
            if not recent_games:
                logger.info("No new releases found")
                await engine.dispose()
                return
            
            logger.info(f"Found {len(recent_games)} recent releases")
            
            added = 0
            skipped = 0
            
            for igdb_data in recent_games:
                igdb_id = igdb_data.get("id")
                if not igdb_id:
                    continue
                
                # Check if already exists
                existing = await game_repo.get_by_igdb_id(igdb_id)
                if existing:
                    skipped += 1
                    continue
                
                # Create new game
                game_data = game_service._transform_igdb_game(igdb_data)
                await game_repo.create(game_data)
                added += 1
                logger.debug(f"Added new game: {game_data['name']}")
            
            logger.info(f"New releases: {added} added, {skipped} already existed")
        except Exception as e:
            logger.error(f"Failed to fetch new releases: {e}")
    
    await engine.dispose()


async def full_sync(stale_days: int = 30, new_release_days: int = 7):
    """Run full sync: update stale games and fetch new releases.
    
    Args:
        stale_days: Days to consider games stale
        new_release_days: Days to look back for new releases
    """
    logger.info("Starting full game sync...")
    start_time = datetime.utcnow()
    
    # Update stale games
    await sync_stale_games(stale_days=stale_days, batch_size=100)
    
    # Fetch new releases
    await fetch_new_releases(days=new_release_days, limit=100)
    
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.success(f"Full sync completed in {duration:.2f} seconds")


def main():
    """Main entry point for sync script."""
    parser = ArgumentParser(description="Sync game data incrementally")
    parser.add_argument(
        "--stale-days",
        type=int,
        default=30,
        help="Days since last sync to consider stale (default: 30)",
    )
    parser.add_argument(
        "--new-release-days",
        type=int,
        default=7,
        help="Days to look back for new releases (default: 7)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for stale game updates (default: 50)",
    )
    parser.add_argument(
        "--mode",
        choices=["stale", "new", "full"],
        default="full",
        help="Sync mode: stale (update old), new (fetch releases), full (both)",
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "stale":
            asyncio.run(
                sync_stale_games(
                    stale_days=args.stale_days, batch_size=args.batch_size
                )
            )
        elif args.mode == "new":
            asyncio.run(fetch_new_releases(days=args.new_release_days, limit=100))
        else:
            asyncio.run(
                full_sync(
                    stale_days=args.stale_days,
                    new_release_days=args.new_release_days,
                )
            )
        logger.success("Sync completed successfully!")
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
