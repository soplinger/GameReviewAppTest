"""Simple game seeding script with popular games for testing.

This script seeds the database with a curated list of popular games
without requiring external API access.

Usage:
    python scripts/simple_seed.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add backend root to Python path for proper imports
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.game import Game
from src.repositories.game_repository import GameRepository


def parse_date(date_string: str) -> datetime:
    """Parse date string to datetime object."""
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        return datetime.utcnow()


# Popular games for testing
POPULAR_GAMES = [
    {
        "igdb_id": 1942,
        "name": "The Witcher 3: Wild Hunt",
        "slug": "the-witcher-3-wild-hunt",
        "summary": "The Witcher 3: Wild Hunt is a story-driven, next-generation open world role-playing game set in a visually stunning fantasy universe full of meaningful choices and impactful consequences.",
        "storyline": "As war rages on throughout the Northern Realms, you take on the greatest contract of your life — tracking down the Child of Destiny, a living weapon that can alter the shape of the world.",
        "rating": 93.0,
        "release_date": "2015-05-19",
        "platforms": ["PC", "PlayStation 4", "Xbox One", "Nintendo Switch"],
        "genres": ["RPG", "Action", "Adventure"],
        "developers": ["CD Projekt RED"],
        "publishers": ["CD Projekt"],
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1wyy.jpg",
    },
    {
        "igdb_id": 1074,
        "name": "Red Dead Redemption 2",
        "slug": "red-dead-redemption-2",
        "summary": "Red Dead Redemption 2 is the epic tale of outlaw Arthur Morgan and the infamous Van der Linde gang, on the run across America at the dawn of the modern age.",
        "rating": 97.0,
        "release_date": "2018-10-26",
        "platforms": ["PC", "PlayStation 4", "Xbox One"],
        "genres": ["Action", "Adventure", "Shooter"],
        "developers": ["Rockstar Games"],
        "publishers": ["Rockstar Games"],
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co1q1f.jpg",
    },
    {
        "igdb_id": 1877,
        "name": "Cyberpunk 2077",
        "slug": "cyberpunk-2077",
        "summary": "Cyberpunk 2077 is an open-world, action-adventure story set in Night City, a megalopolis obsessed with power, glamour and body modification.",
        "rating": 86.0,
        "release_date": "2020-12-10",
        "platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S"],
        "genres": ["RPG", "Action", "Adventure"],
        "developers": ["CD Projekt RED"],
        "publishers": ["CD Projekt"],
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co2lbd.jpg",
    },
    {
        "igdb_id": 119133,
        "name": "Hades",
        "slug": "hades",
        "summary": "Hades is a god-like rogue-like dungeon crawler that combines the best aspects of Supergiant's critically acclaimed titles, including the fast-paced action of Bastion and the rich atmosphere and depth of Transistor.",
        "rating": 93.0,
        "release_date": "2020-09-17",
        "platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S", "Nintendo Switch"],
        "genres": ["Indie", "RPG", "Action"],
        "developers": ["Supergiant Games"],
        "publishers": ["Supergiant Games"],
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co2179.jpg",
    },
    {
        "igdb_id": 1030,
        "name": "The Elder Scrolls V: Skyrim",
        "slug": "the-elder-scrolls-v-skyrim",
        "summary": "The Elder Scrolls V: Skyrim is an action role-playing video game developed by Bethesda Game Studios and published by Bethesda Softworks.",
        "rating": 92.0,
        "release_date": "2011-11-11",
        "platforms": ["PC", "PlayStation 3", "PlayStation 4", "PlayStation 5", "Xbox 360", "Xbox One", "Xbox Series X/S", "Nintendo Switch"],
        "genres": ["RPG", "Action", "Adventure"],
        "developers": ["Bethesda Game Studios"],
        "publishers": ["Bethesda Softworks"],
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co3p2d.jpg",
    },
    {
        "igdb_id": 1009,
        "name": "Grand Theft Auto V",
        "slug": "grand-theft-auto-v",
        "summary": "Grand Theft Auto V is an action-adventure video game played from either a third-person or first-person perspective.",
        "rating": 97.0,
        "release_date": "2013-09-17",
        "platforms": ["PC", "PlayStation 3", "PlayStation 4", "PlayStation 5", "Xbox 360", "Xbox One", "Xbox Series X/S"],
        "genres": ["Action", "Adventure", "Racing"],
        "developers": ["Rockstar North"],
        "publishers": ["Rockstar Games"],
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co2lbk.jpg",
    },
    {
        "igdb_id": 121,
        "name": "Minecraft",
        "slug": "minecraft",
        "summary": "Minecraft is a sandbox video game developed by Mojang Studios. Players explore a blocky, procedurally-generated 3D world with virtually infinite terrain.",
        "rating": 93.0,
        "release_date": "2011-11-18",
        "platforms": ["PC", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S", "Nintendo Switch", "Mobile"],
        "genres": ["Adventure", "Indie", "Simulator"],
        "developers": ["Mojang Studios"],
        "publishers": ["Mojang Studios"],
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co49ai.jpg",
    },
    {
        "igdb_id": 137,
        "name": "Among Us",
        "slug": "among-us",
        "summary": "Among Us is an online multiplayer social deduction game developed and published by American game studio Innersloth.",
        "rating": 78.0,
        "release_date": "2018-06-15",
        "platforms": ["PC", "Mobile", "PlayStation 4", "PlayStation 5", "Xbox One", "Xbox Series X/S", "Nintendo Switch"],
        "genres": ["Strategy", "Indie"],
        "developers": ["InnerSloth"],
        "publishers": ["InnerSloth"],
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co4g0e.jpg",
    },
    {
        "igdb_id": 103303,
        "name": "The Legend of Zelda: Breath of the Wild",
        "slug": "the-legend-of-zelda-breath-of-the-wild",
        "summary": "The Legend of Zelda: Breath of the Wild is an action-adventure game developed and published by Nintendo for the Nintendo Switch and Wii U consoles.",
        "rating": 97.0,
        "release_date": "2017-03-03",
        "platforms": ["Nintendo Switch", "Wii U"],
        "genres": ["Adventure", "RPG"],
        "developers": ["Nintendo EPD"],
        "publishers": ["Nintendo"],
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co3p2d.jpg",
    },
    {
        "igdb_id": 119388,
        "name": "Valheim",
        "slug": "valheim",
        "summary": "Valheim is a brutal exploration and survival game for 1-10 players set in a procedurally-generated world inspired by Norse mythology.",
        "rating": 90.0,
        "release_date": "2021-02-02",
        "platforms": ["PC"],
        "genres": ["Adventure", "Indie", "RPG"],
        "developers": ["Iron Gate AB"],
        "publishers": ["Coffee Stain Publishing"],
        "cover_url": "https://images.igdb.com/igdb/image/upload/t_cover_big/co3p2h.jpg",
    },
]


async def seed_games():
    """Seed database with popular games."""
    logger.info("Starting game seeding with popular games...")
    
    # Create async engine and session with aiosqlite
    database_url = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
    engine = create_async_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    seeded_count = 0
    
    async with async_session() as session:
        game_repo = GameRepository(session)
        
        for game_data in POPULAR_GAMES:
            try:
                # Check if game already exists
                existing = await game_repo.get_by_igdb_id(game_data["igdb_id"])
                if existing:
                    logger.info(f"Game '{game_data['name']}' already exists, skipping...")
                    continue
                
                # Create new game
                release_date = None
                if game_data.get("release_date"):
                    release_date = parse_date(game_data["release_date"])
                
                game_dict = {
                    "igdb_id": game_data["igdb_id"],
                    "name": game_data["name"],
                    "slug": game_data["slug"],
                    "summary": game_data.get("summary"),
                    "storyline": game_data.get("storyline"),
                    "rating": game_data.get("rating"),
                    "release_date": release_date,
                    "platforms": game_data.get("platforms", []),
                    "genres": game_data.get("genres", []),
                    "developers": game_data.get("developers", []),
                    "publishers": game_data.get("publishers", []),
                    "cover_url": game_data.get("cover_url"),
                    "last_synced_at": datetime.utcnow(),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
                
                await game_repo.create(game_dict)
                seeded_count += 1
                logger.info(f"✅ Seeded: {game_data['name']}")
                
            except Exception as e:
                logger.error(f"❌ Failed to seed {game_data['name']}: {e}")
        
        await session.commit()
        
    await engine.dispose()
    
    logger.success(f"🎮 Successfully seeded {seeded_count} games!")
    return seeded_count


def main():
    """Main entry point."""
    try:
        asyncio.run(seed_games())
        logger.success("Game seeding completed successfully!")
    except Exception as e:
        logger.error(f"Game seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()