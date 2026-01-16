

 Game Data Management Scripts

This directory contains scripts for managing game data from external APIs (IGDB and RAWG).

## Prerequisites

Before running these scripts, ensure you have:

1. **IGDB API credentials** (Twitch Developer Console):
   - Register app at: https://dev.twitch.tv/console/apps
   - Set `IGDB_CLIENT_ID` and `IGDB_CLIENT_SECRET` in `.env`

2. **RAWG API key** (optional, used as fallback):
   - Get API key at: https://rawg.io/apidocs
   - Set `RAWG_API_KEY` in `.env`

## Scripts

### seed_games.py

Seeds the database with initial game data from IGDB.

**Usage:**
```bash
# Seed 100 popular games (default)
python scripts/seed_games.py

# Seed 500 popular games
python scripts/seed_games.py --limit 500

# Seed recent releases from last 90 days
python scripts/seed_games.py --recent --days 90

# Seed 200 recent games
python scripts/seed_games.py --recent --limit 200
```

**Options:**
- `--limit N`: Number of games to seed (max: 500 per run)
- `--recent`: Seed recently released games instead of popular games
- `--days N`: Days to look back for recent games (default: 90)

**When to use:**
- Initial database setup
- After clearing game data
- Building a comprehensive game catalog

---

### sync_games.py

Incrementally syncs game data - updates stale records and fetches new releases.

**Usage:**
```bash
# Full sync: update stale games + fetch new releases
python scripts/sync_games.py

# Only update games older than 30 days
python scripts/sync_games.py --mode stale --stale-days 30

# Only fetch games released in last 7 days
python scripts/sync_games.py --mode new --new-release-days 7

# Custom batch size for updates
python scripts/sync_games.py --batch-size 100
```

**Options:**
- `--mode [stale|new|full]`: Sync mode (default: full)
  - `stale`: Update games that haven't been synced recently
  - `new`: Fetch newly released games
  - `full`: Both stale updates and new releases
- `--stale-days N`: Days since last sync to consider stale (default: 30)
- `--new-release-days N`: Days to look back for new releases (default: 7)
- `--batch-size N`: Batch size for stale game updates (default: 50)

**When to use:**
- Daily via cron job/scheduled task
- Keeping game data fresh (ratings, screenshots, metadata)
- Discovering newly released games

---

## Recommended Workflow

### Initial Setup
```bash
# 1. Configure API credentials in .env
# 2. Seed popular games
python scripts/seed_games.py --limit 500

# 3. Seed recent releases
python scripts/seed_games.py --recent --days 180 --limit 500
```

### Daily Maintenance (Cron Job)
```bash
# Run once per day to keep data fresh
0 2 * * * cd /path/to/backend && python scripts/sync_games.py
```

### Weekly Deep Sync
```bash
# Update all games older than 7 days
python scripts/sync_games.py --stale-days 7 --batch-size 100
```

---

## Rate Limits

**IGDB:**
- 4 requests per second
- Unlimited requests per day
- Automatic rate limiting built into client

**RAWG:**
- 20,000 requests per month (~667 per day)
- Used as fallback only

**Best Practices:**
- Seed games during off-hours to avoid rate limit impact on live API
- Use `--batch-size` to control sync load
- Monitor logs for API errors or rate limit warnings

---

## Troubleshooting

### "Module not found" errors
```bash
# Ensure you're in the backend directory
cd backend
pip install -r requirements.txt
```

### "Authentication failed" errors
- Verify IGDB credentials are correct in `.env`
- Check Twitch app is active and not rate-limited
- Try regenerating Twitch OAuth token

### "No games found" warnings
- IGDB may be temporarily unavailable
- Check network connectivity
- Verify API credentials are valid

### Database locked errors
- Ensure backend server is not running
- Close any DB browser tools
- Wait for previous script to complete

---

## Monitoring

Check logs for sync status:
```bash
# Logs are output to console by default
python scripts/sync_games.py 2>&1 | tee sync.log
```

Query database to verify game count:
```bash
sqlite3 database/game_review.db "SELECT COUNT(*) FROM games;"
```

---

## Advanced Usage

### Custom Sync Schedule

**Windows (Task Scheduler):**
```powershell
# Create scheduled task for daily sync at 2 AM
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\path\to\backend\scripts\sync_games.py" -WorkingDirectory "C:\path\to\backend"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "GameReviewSync"
```

**Linux/Mac (Crontab):**
```bash
# Add to crontab (crontab -e)
0 2 * * * cd /path/to/backend && /usr/bin/python3 scripts/sync_games.py >> /var/log/game_sync.log 2>&1
```

---

## API Documentation

- **IGDB API Docs**: https://api-docs.igdb.com/
- **RAWG API Docs**: https://api.rawg.io/docs/
- **Twitch OAuth**: https://dev.twitch.tv/docs/authentication/

