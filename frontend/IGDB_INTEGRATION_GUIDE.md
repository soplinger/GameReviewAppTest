# IGDB Integration Guide

This guide explains how to use the IGDB (Internet Game Database) integration features in the Game Review App.

## Features Overview

### 🔍 Hybrid Search
- **Smart Search**: Searches your local database first, then automatically syncs from IGDB if needed
- **Auto-sync Toggle**: Control whether the system should automatically fetch missing games from IGDB
- **Local-first Strategy**: Fast results from local database with seamless IGDB fallback

### 🎮 Sync Panel
Access comprehensive game syncing tools to populate your database with games from IGDB.

## Using the Sync Panel

### 1. Access the Sync Panel
- Navigate to the Game Search page
- Click the **"Show IGDB Sync"** button in the top-right corner
- The sync panel will appear with various sync options

### 2. Sync Popular Games
- **Purpose**: Get the most highly-rated and popular games
- **How to**: 
  1. Set the limit (1-100 games)
  2. Click "Sync Popular"
- **Default**: 20 games
- **Best for**: Building a foundation of well-known games

### 3. Sync by Search
- **Purpose**: Find and sync specific games by name
- **How to**:
  1. Enter a search term (e.g., "zelda", "mario", "cyberpunk")
  2. Set the limit (1-50 games)  
  3. Click "Sync Search"
- **Best for**: Adding specific games or franchises

### 4. Sync by Genre
- **Purpose**: Populate your database with games from specific genres
- **How to**:
  1. Select a genre from the dropdown
  2. Set the limit (1-50 games)
  3. Click "Sync Genre"
- **Available Genres**: Action, Adventure, RPG, Strategy, Shooter, Sports, Racing, Fighting, Puzzle, Simulation, Horror, Platformer
- **Quick Actions**: Use the genre buttons at the bottom for instant syncing (10 games each)

### 5. Sync Recent Releases
- **Purpose**: Get recently released games
- **How to**:
  1. Set the limit (1-100 games)
  2. Set how many days back to look (1-365 days)
  3. Click "Sync Recent"
- **Default**: 25 games from the last 90 days
- **Best for**: Staying current with new releases

## Search Features

### Smart Search
When you perform a search with the auto-sync option enabled:

1. **Local Search**: System searches your local database first
2. **IGDB Fallback**: If no local results found, automatically searches IGDB
3. **Auto-sync**: Relevant games are automatically added to your database
4. **Instant Results**: See IGDB results immediately while syncing happens in background

### Search Indicators
- **IGDB Results Badge**: Blue badge indicates results came from IGDB
- **Sync Counter**: Green checkmark shows how many new games were added
- **Auto-sync Toggle**: Control automatic syncing behavior per search

## Tips for Best Results

### 🎯 Strategic Syncing
1. **Start with Popular**: Sync 50-100 popular games for a solid foundation
2. **Add Genres**: Sync 15-20 games from each genre you're interested in
3. **Stay Current**: Regularly sync recent games (weekly/monthly)
4. **Targeted Search**: Use search sync for specific games users request

### ⚡ Performance Tips
- **Batch Operations**: Sync multiple categories at once using different limits
- **Auto-sync Smart**: Keep auto-sync enabled for the best search experience
- **Monitor Limits**: IGDB has rate limits (4 requests/second), so don't exceed recommended limits
- **Clear Database**: If needed, use the clear_tables.py script to start fresh

### 🔧 Troubleshooting

#### No Games Syncing
- Check IGDB credentials in backend/.env
- Verify internet connection
- Check backend logs for API errors

#### Sync Taking Too Long
- Reduce the limit per operation
- IGDB rate limits may be causing delays
- Check network connection stability

#### Duplicate Games
- The system automatically handles duplicates by IGDB ID
- Existing games are updated, not duplicated
- Check logs if you see unexpected behavior

#### Search Not Finding Games
- Try enabling auto-sync in search
- Use the sync panel to specifically add games
- Check spelling and try variations of game names

## API Rate Limits

IGDB has the following limits:
- **4 requests per second**
- **Automatic token refresh** (handled by backend)
- **10,000 requests per month** (generous limit for most use cases)

The system respects these limits automatically.

## Integration with Reviews

Once games are synced:
- Users can write reviews for any synced game
- Games appear in search results immediately
- All game metadata (genres, platforms, release dates) is available
- Game covers and screenshots are included

## Advanced Usage

### Bulk Operations
For initial setup, consider this sync strategy:
1. Sync Popular Games (limit: 100)
2. Sync each main genre (limit: 20 each)
3. Sync Recent Games (limit: 50, 180 days back)
4. Use search sync for user-requested games

### Maintenance
- Weekly: Sync recent games (7 days back)
- Monthly: Sync popular games (to catch new trending titles)
- As-needed: Search sync for specific user requests

## Support

If you encounter issues:
1. Check the browser console for errors
2. Review backend logs for API issues
3. Verify IGDB credentials are correct
4. Ensure backend server is running

The IGDB integration provides a powerful way to build a comprehensive game database while maintaining fast local search performance.