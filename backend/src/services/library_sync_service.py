"""Library sync service for importing games and playtime from gaming platforms."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.linked_account import LinkedAccount, PlatformType
from ..models.game_library import GameLibrary
from ..repositories.linked_account_repository import LinkedAccountRepository
from ..repositories.game_library_repository import GameLibraryRepository
from ..repositories.game_repository import GameRepository
from ..core.logging import get_logger
from ..core.errors import NotFoundError, ExternalServiceError
from .oauth_service import OAuthService
from .oauth.steam_client import SteamOAuthClient
from .oauth.playstation_client import PlayStationOAuthClient
from .oauth.xbox_client import XboxOAuthClient
from .game_data_service import GameDataService

logger = get_logger(__name__)


class LibrarySyncService:
    """
    Service for syncing game libraries from gaming platforms.
    
    Handles:
    - Importing games from Steam, PSN, Xbox
    - Syncing playtime and achievement data
    - Matching platform games to our database games
    - Updating library entries on each sync
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.linked_account_repo = LinkedAccountRepository(db)
        self.game_library_repo = GameLibraryRepository(db)
        self.game_repo = GameRepository(db)
        self.oauth_service = OAuthService(db)
        self.game_data_service = GameDataService(self.game_repo)
        self.steam_client = SteamOAuthClient()
        self.psn_client = PlayStationOAuthClient()
        self.xbox_client = XboxOAuthClient()
    
    async def sync_user_library(
        self,
        user_id: int,
        platform: Optional[PlatformType] = None
    ) -> Dict[str, Any]:
        """
        Sync game library for a user from one or all platforms.
        
        Args:
            user_id: User ID to sync library for
            platform: Specific platform to sync, or None for all
            
        Returns:
            Sync summary with counts and status
        """
        if platform:
            platforms = [platform]
        else:
            # Get all linked platforms for user
            linked_accounts = await self.linked_account_repo.get_user_accounts(user_id)
            platforms = [account.platform for account in linked_accounts]
        
        if not platforms:
            logger.warning("no_platforms_linked", user_id=user_id)
            return {
                "synced_platforms": [],
                "total_games": 0,
                "new_games": 0,
                "updated_games": 0,
                "errors": []
            }
        
        summary = {
            "synced_platforms": [],
            "total_games": 0,
            "new_games": 0,
            "updated_games": 0,
            "errors": []
        }
        
        for plat in platforms:
            try:
                result = await self._sync_platform_library(user_id, plat)
                summary["synced_platforms"].append(plat.value)
                summary["total_games"] += result["total"]
                summary["new_games"] += result["new"]
                summary["updated_games"] += result["updated"]
            except Exception as e:
                error_msg = f"{plat.value}: {str(e)}"
                summary["errors"].append(error_msg)
                logger.error(
                    "platform_sync_failed",
                    user_id=user_id,
                    platform=plat.value,
                    error=str(e)
                )
        
        logger.info(
            "library_sync_completed",
            user_id=user_id,
            summary=summary
        )
        
        return summary
    
    async def _sync_platform_library(
        self,
        user_id: int,
        platform: PlatformType
    ) -> Dict[str, int]:
        """
        Sync library from a specific platform.
        
        Args:
            user_id: User ID
            platform: Platform to sync
            
        Returns:
            Dict with total, new, and updated counts
        """
        # Get linked account
        linked_account = await self.linked_account_repo.get_by_user_and_platform(
            user_id, platform
        )
        if not linked_account:
            raise NotFoundError(f"No {platform.value} account linked")
        
        # Refresh token if needed
        linked_account = await self.oauth_service.refresh_token_if_needed(linked_account)
        
        # Fetch games from platform
        platform_games = await self._fetch_platform_games(linked_account)
        
        if not platform_games:
            logger.warning(
                "no_games_found",
                user_id=user_id,
                platform=platform.value
            )
            return {"total": 0, "new": 0, "updated": 0}
        
        # Process each game
        new_count = 0
        updated_count = 0
        
        for platform_game in platform_games:
            try:
                # Try to match platform game to our database game
                game = await self._match_platform_game(platform_game, platform)
                
                if not game:
                    logger.debug(
                        "game_not_matched",
                        platform_game_id=platform_game["platform_game_id"],
                        name=platform_game.get("name")
                    )
                    continue
                
                # Calculate achievements count
                achievements_count = self._calculate_achievements(platform_game, platform)
                
                # Upsert library entry
                was_created = await self.game_library_repo.upsert(
                    user_id=user_id,
                    game_id=game.id,
                    linked_account_id=linked_account.id,
                    playtime_hours=platform_game.get("playtime_hours", 0),
                    achievements_count=achievements_count,
                    last_played_at=platform_game.get("last_played_at") or platform_game.get("last_played") or platform_game.get("last_updated")
                )
                
                if was_created:
                    new_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                logger.error(
                    "game_import_failed",
                    platform_game_id=platform_game.get("platform_game_id"),
                    error=str(e)
                )
                continue
        
        # Update last synced time
        await self.linked_account_repo.update_sync_time(linked_account.id)
        
        logger.info(
            "platform_library_synced",
            user_id=user_id,
            platform=platform.value,
            total=len(platform_games),
            new=new_count,
            updated=updated_count
        )
        
        return {
            "total": len(platform_games),
            "new": new_count,
            "updated": updated_count
        }
    
    async def _fetch_platform_games(
        self,
        linked_account: LinkedAccount
    ) -> List[Dict[str, Any]]:
        """
        Fetch games from platform API.
        
        Args:
            linked_account: Linked account with tokens
            
        Returns:
            List of platform game data
        """
        platform = linked_account.platform
        
        try:
            if platform == PlatformType.STEAM:
                games = await self.steam_client.get_owned_games(
                    linked_account.platform_user_id
                )
            elif platform == PlatformType.PLAYSTATION:
                games = await self.psn_client.get_user_titles(
                    linked_account.access_token,
                    linked_account.platform_user_id
                )
            elif platform == PlatformType.XBOX:
                # Xbox needs XSTS token - we'll parse from access_token metadata
                # In production, store XSTS token separately
                games = await self.xbox_client.get_user_titles(
                    linked_account.platform_user_id,
                    linked_account.access_token  # This should be XSTS token
                )
            else:
                raise ValueError(f"Unsupported platform: {platform}")
            
            return games
            
        except Exception as e:
            logger.error(
                "fetch_platform_games_failed",
                platform=platform.value,
                linked_account_id=linked_account.id,
                error=str(e)
            )
            raise ExternalServiceError(f"Failed to fetch games from {platform.value}")
    
    async def _match_platform_game(
        self,
        platform_game: Dict[str, Any],
        platform: PlatformType
    ) -> Optional[Any]:
        """
        Match a platform game to a game in our database.
        
        Args:
            platform_game: Game data from platform
            platform: Platform type
            
        Returns:
            Matched Game model or None
        """
        game_name = platform_game.get("name")
        if not game_name:
            return None
        
        # Try to find game by name (case-insensitive)
        games = await self.game_repo.search_by_name(game_name, limit=1)
        
        if games:
            logger.debug(
                "game_matched_local",
                platform_game_id=platform_game.get("platform_game_id"),
                game_id=games[0].id,
                name=game_name
            )
            return games[0]
        
        # Game not found locally - try to fetch from IGDB
        try:
            logger.info(
                "fetching_game_from_igdb",
                name=game_name,
                platform=platform.value
            )
            
            # Search IGDB and sync first result
            synced_count = await self.game_data_service.sync_games_by_search(
                query=game_name,
                limit=1
            )
            
            if synced_count > 0:
                # Try finding again after sync
                games = await self.game_repo.search_by_name(game_name, limit=1)
                if games:
                    logger.info(
                        "game_fetched_from_igdb",
                        game_id=games[0].id,
                        name=game_name
                    )
                    return games[0]
            
            logger.warning(
                "game_not_found_in_igdb",
                name=game_name,
                platform=platform.value
            )
            
        except Exception as e:
            logger.error(
                "failed_to_fetch_game_from_igdb",
                name=game_name,
                error=str(e)
            )
        
        return None
    
    def _calculate_achievements(
        self,
        platform_game: Dict[str, Any],
        platform: PlatformType
    ) -> int:
        """
        Calculate achievement count from platform game data.
        
        Args:
            platform_game: Game data from platform
            platform: Platform type
            
        Returns:
            Number of achievements earned
        """
        if platform == PlatformType.STEAM:
            # Steam doesn't provide achievement count in owned games API
            # Would need separate API call per game
            return 0
        
        elif platform == PlatformType.PLAYSTATION:
            # PSN provides earned trophies
            earned = platform_game.get("earned_trophies", {})
            return sum([
                earned.get("bronze", 0),
                earned.get("silver", 0),
                earned.get("gold", 0),
                earned.get("platinum", 0)
            ])
        
        elif platform == PlatformType.XBOX:
            # Xbox provides achievements earned
            return platform_game.get("achievements_earned", 0)
        
        return 0
    
    async def get_user_library(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        platform: Optional[PlatformType] = None
    ) -> tuple[List[GameLibrary], int]:
        """
        Get user's game library with optional platform filter.
        
        Args:
            user_id: User ID
            skip: Pagination offset
            limit: Page size
            platform: Optional platform filter
            
        Returns:
            Tuple of (library entries, total count)
        """
        # Get linked account if platform specified
        linked_account_id = None
        if platform:
            linked_account = await self.linked_account_repo.get_by_user_and_platform(
                user_id, platform
            )
            if linked_account:
                linked_account_id = linked_account.id
        
        library = await self.game_library_repo.get_user_library(
            user_id,
            limit=limit,
            offset=skip,  # Use offset instead of skip
            linked_account_id=linked_account_id
        )
        
        total_count = await self.game_library_repo.count_user_library(
            user_id,
            linked_account_id=linked_account_id
        )
        
        logger.info(
            "fetched_user_library",
            user_id=user_id,
            count=len(library),
            total=total_count,
            platform=platform.value if platform else "all"
        )
        
        return library, total_count
    
    async def get_game_playtime(
        self,
        user_id: int,
        game_id: int
    ) -> float:
        """
        Get total playtime for a game across all platforms.
        
        Args:
            user_id: User ID
            game_id: Game ID
            
        Returns:
            Total playtime in hours
        """
        playtime = await self.game_library_repo.get_game_playtime(user_id, game_id)
        
        logger.debug(
            "fetched_game_playtime",
            user_id=user_id,
            game_id=game_id,
            playtime_hours=playtime
        )
        
        return playtime
