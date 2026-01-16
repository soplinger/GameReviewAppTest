# Data Model: Game Review Social Platform

**Feature**: 001-game-review-social  
**Created**: 2026-01-14  
**Database**: SQLite 3.40+ with SQLAlchemy 2.0 ORM

## Entity Relationship Overview

```
User (1) ─────── (∞) Review (∞) ─────── (1) Game
  │                                          │
  │                                          │
  │ (∞)                                   (∞) │
  │                                          │
Friendship (self-referencing)          GameLibrary
  │                                          │
  │                                          │
  │ (∞)                                   (1) │
  │                                          │
User (1) ─────── (∞) LinkedAccount          User
  │
  │ (∞)
  │
UserPreference (∞) ─────── (1) Game
  │
  │ (∞)
  │
Recommendation (∞) ─────── (1) Game
```

---

## Core Entities

### 1. User

**Purpose**: Represents a platform user account

**Attributes**:
- `id` (Integer, PK): Unique identifier
- `username` (String, 50, unique, not null): Display name
- `email` (String, 255, unique, not null): User email (login)
- `password_hash` (String, 255, not null): Bcrypt hashed password
- `bio` (Text, nullable): User profile description
- `avatar_url` (String, 500, nullable): Profile picture URL
- `created_at` (DateTime, not null): Account creation timestamp
- `updated_at` (DateTime, not null): Last profile update
- `is_active` (Boolean, default=True): Account status
- `last_login` (DateTime, nullable): Last login timestamp

**Relationships**:
- `reviews` → One-to-Many with Review
- `friendships_initiated` → One-to-Many with Friendship (as user_id)
- `friendships_received` → One-to-Many with Friendship (as friend_id)
- `linked_accounts` → One-to-Many with LinkedAccount
- `game_library` → One-to-Many with GameLibrary
- `preferences` → One-to-Many with UserPreference
- `recommendations` → One-to-Many with Recommendation

**Indexes**:
- `idx_user_email` on (email)
- `idx_user_username` on (username)
- `idx_user_created_at` on (created_at)

**Validation Rules**:
- Email must be valid format
- Username: 3-50 characters, alphanumeric + underscore/hyphen
- Password: Minimum 8 characters (hashed before storage)
- Bio: Maximum 500 characters

---

### 2. Review

**Purpose**: User's review of a game

**Attributes**:
- `id` (Integer, PK): Unique identifier
- `user_id` (Integer, FK→User.id, not null): Review author
- `game_id` (Integer, FK→Game.id, not null): Reviewed game
- `rating` (Integer, not null): Star rating (1-5)
- `content` (Text, not null): Review text
- `is_draft` (Boolean, default=False): Publication status
- `playtime_hours` (Integer, nullable): Hours played (from linked account)
- `platform` (String, 50, nullable): Platform played on
- `created_at` (DateTime, not null): Review creation
- `updated_at` (DateTime, not null): Last edit timestamp
- `published_at` (DateTime, nullable): Publication timestamp

**Relationships**:
- `user` → Many-to-One with User
- `game` → Many-to-One with Game

**Indexes**:
- `idx_review_user_id` on (user_id)
- `idx_review_game_id` on (game_id)
- `idx_review_published_at` on (published_at) WHERE is_draft=False
- `idx_review_rating` on (rating)
- **Unique Constraint**: (user_id, game_id) - one review per user per game

**Validation Rules**:
- Rating: 1-5 (integer)
- Content: Minimum 50 characters, maximum 10,000 characters
- Cannot publish without both rating and content
- playtime_hours: >= 0 if provided

---

### 3. Game

**Purpose**: Video game metadata (sourced from IGDB/RAWG APIs)

**Data Source Strategy**:
- **Primary Source**: IGDB API (500k+ games, Twitch OAuth)
- **Secondary Source**: RAWG API (800k+ games, fallback)
- **Initial Seeding**: 10k-50k popular games on first setup
- **Incremental Updates**: Daily cron job for new releases (last 7 days)
- **On-Demand**: Search external APIs when user searches for missing game, cache result
- **Sync Frequency**: Weekly metadata refresh for active games (games with reviews in last 30 days)

**External ID Mapping**:
- `igdb_id` (Integer, nullable): IGDB game ID for API sync
- `rawg_id` (Integer, nullable): RAWG game ID for fallback
- `last_synced_at` (DateTime, nullable): Last external API sync timestamp

**Attributes**:
- `id` (Integer, PK): Unique identifier
- `title` (String, 255, not null): Game title
- `slug` (String, 255, unique, not null): URL-friendly identifier
- `description` (Text, nullable): Game description
- `release_date` (Date, nullable): Release date
- `developer` (String, 255, nullable): Developer/studio
- `publisher` (String, 255, nullable): Publisher
- `cover_image_url` (String, 500, nullable): Cover art URL
- `platforms` (JSON, not null): List of platforms (["PC", "PS5", "Xbox"])
- `genres` (JSON, not null): List of genres (["RPG", "Action"])
- `average_rating` (Float, nullable): Calculated average from reviews
- `review_count` (Integer, default=0): Total published reviews
- `igdb_id` (Integer, nullable, unique): IGDB external ID
- `rawg_id` (Integer, nullable, unique): RAWG external ID
- `last_synced_at` (DateTime, nullable): Last external metadata sync
- `created_at` (DateTime, not null): Entry creation
- `updated_at` (DateTime, not null): Last update

**Relationships**:
- `reviews` → One-to-Many with Review
- `library_entries` → One-to-Many with GameLibrary
- `preferences` → One-to-Many with UserPreference
- `recommendations` → One-to-Many with Recommendation

**Indexes**:
- `idx_game_slug` on (slug)
- `idx_game_title` on (title) - for search
- `idx_game_release_date` on (release_date)
- `idx_game_average_rating` on (average_rating)
- `idx_game_igdb_id` on (igdb_id) - for API sync
- `idx_game_rawg_id` on (rawg_id) - for API sync

**Computed Fields**:
- `average_rating` = AVG(reviews.rating) WHERE is_draft=False
- `review_count` = COUNT(reviews) WHERE is_draft=False

**Validation Rules**:
- Title: 1-255 characters
- Slug: Generated from title (lowercase, hyphens)
- Platforms: At least one platform
- Genres: At least one genre

**API Mapping Example** (IGDB → Game):
```python
{
    "igdb_id": igdb.id,
    "title": igdb.name,
    "slug": igdb.slug,
    "description": igdb.summary,
    "release_date": datetime.fromtimestamp(igdb.first_release_date),
    "developer": igdb.involved_companies[0].company.name,
    "publisher": igdb.involved_companies[1].company.name,
    "cover_image_url": f"https://images.igdb.com/igdb/image/upload/t_cover_big/{igdb.cover.image_id}.jpg",
    "platforms": [p.name for p in igdb.platforms],
    "genres": [g.name for g in igdb.genres],
    "last_synced_at": datetime.now()
}
```

---

### 4. Friendship

**Purpose**: Bidirectional friend relationship between users

**Attributes**:
- `id` (Integer, PK): Unique identifier
- `user_id` (Integer, FK→User.id, not null): User who initiated request
- `friend_id` (Integer, FK→User.id, not null): User who received request
- `status` (Enum, not null): 'pending', 'accepted', 'declined'
- `requested_at` (DateTime, not null): When request was sent
- `responded_at` (DateTime, nullable): When request was accepted/declined

**Relationships**:
- `user` → Many-to-One with User (initiator)
- `friend` → Many-to-One with User (receiver)

**Indexes**:
- `idx_friendship_user_id` on (user_id)
- `idx_friendship_friend_id` on (friend_id)
- `idx_friendship_status` on (status)
- **Unique Constraint**: (user_id, friend_id) - prevent duplicate requests
- **Check Constraint**: user_id != friend_id - prevent self-friending

**Validation Rules**:
- Cannot send request to self
- Cannot send duplicate requests (check both directions)
- Status transitions: pending → accepted/declined (no reversals)

**Note**: Friendship is bidirectional - if (A, B) is accepted, both users are friends

---

### 5. LinkedAccount

**Purpose**: Connection to gaming platform account (Steam, PSN, Xbox)

**Attributes**:
- `id` (Integer, PK): Unique identifier
- `user_id` (Integer, FK→User.id, not null): Owner
- `platform` (Enum, not null): 'steam', 'playstation', 'xbox'
- `platform_user_id` (String, 255, not null): External user ID
- `platform_username` (String, 255, nullable): Display name on platform
- `access_token` (String, 1000, encrypted, nullable): OAuth access token
- `refresh_token` (String, 1000, encrypted, nullable): OAuth refresh token
- `token_expires_at` (DateTime, nullable): Token expiration
- `connected_at` (DateTime, not null): When account was linked
- `last_synced_at` (DateTime, nullable): Last library sync

**Relationships**:
- `user` → Many-to-One with User
- `library_entries` → One-to-Many with GameLibrary

**Indexes**:
- `idx_linked_account_user_id` on (user_id)
- `idx_linked_account_platform` on (platform)
- **Unique Constraint**: (user_id, platform) - one account per platform per user
- **Unique Constraint**: (platform, platform_user_id) - prevent duplicate links

**Security**:
- `access_token` and `refresh_token` must be encrypted at rest
- Tokens never exposed in API responses
- Implement token refresh flow

**Validation Rules**:
- Platform must be supported enum value
- Platform user ID must be valid for that platform

---

### 6. GameLibrary

**Purpose**: Games owned/played from linked accounts

**Attributes**:
- `id` (Integer, PK): Unique identifier
- `user_id` (Integer, FK→User.id, not null): Owner
- `game_id` (Integer, FK→Game.id, not null): Game reference
- `linked_account_id` (Integer, FK→LinkedAccount.id, nullable): Source
- `playtime_hours` (Integer, default=0): Total hours played
- `achievements_count` (Integer, default=0): Achievements unlocked
- `last_played_at` (DateTime, nullable): Last play session
- `imported_at` (DateTime, not null): When entry was created

**Relationships**:
- `user` → Many-to-One with User
- `game` → Many-to-One with Game
- `linked_account` → Many-to-One with LinkedAccount

**Indexes**:
- `idx_game_library_user_id` on (user_id)
- `idx_game_library_game_id` on (game_id)
- **Unique Constraint**: (user_id, game_id, linked_account_id)

**Validation Rules**:
- playtime_hours >= 0
- achievements_count >= 0

---

### 7. UserPreference

**Purpose**: Explicit user preferences (liked/disliked games)

**Attributes**:
- `id` (Integer, PK): Unique identifier
- `user_id` (Integer, FK→User.id, not null): User
- `game_id` (Integer, FK→Game.id, not null): Game
- `preference_type` (Enum, not null): 'enjoyed', 'disliked'
- `created_at` (DateTime, not null): When preference was set

**Relationships**:
- `user` → Many-to-One with User
- `game` → Many-to-One with Game

**Indexes**:
- `idx_user_pref_user_id` on (user_id)
- `idx_user_pref_game_id` on (game_id)
- **Unique Constraint**: (user_id, game_id) - one preference per game

**Validation Rules**:
- Preference type must be 'enjoyed' or 'disliked'
- Cannot have both enjoyed and disliked for same game

---

### 8. Recommendation

**Purpose**: Personalized game recommendations

**Attributes**:
- `id` (Integer, PK): Unique identifier
- `user_id` (Integer, FK→User.id, not null): User
- `game_id` (Integer, FK→Game.id, not null): Recommended game
- `score` (Float, not null): Recommendation confidence (0.0-1.0)
- `reasoning` (Text, nullable): Why this was recommended
- `is_dismissed` (Boolean, default=False): User dismissed recommendation
- `generated_at` (DateTime, not null): When recommendation was created
- `algorithm_version` (String, 50, not null): Algorithm version for tracking

**Relationships**:
- `user` → Many-to-One with User
- `game` → Many-to-One with Game

**Indexes**:
- `idx_recommendation_user_id` on (user_id)
- `idx_recommendation_score` on (score)
- `idx_recommendation_dismissed` on (is_dismissed)

**Validation Rules**:
- Score: 0.0 to 1.0
- Generate top 20 recommendations per user
- Refresh recommendations: daily or after new reviews

---

## Database Schema (SQLite DDL)

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    bio TEXT,
    avatar_url VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    last_login DATETIME
);
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_user_created_at ON users(created_at);

-- Games table
CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    release_date DATE,
    developer VARCHAR(255),
    publisher VARCHAR(255),
    cover_image_url VARCHAR(500),
    platforms TEXT NOT NULL, -- JSON array
    genres TEXT NOT NULL, -- JSON array
    average_rating REAL,
    review_count INTEGER NOT NULL DEFAULT 0,
    igdb_id INTEGER UNIQUE, -- IGDB external ID for API sync
    rawg_id INTEGER UNIQUE, -- RAWG external ID for fallback
    last_synced_at DATETIME, -- Last external API metadata sync
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_game_slug ON games(slug);
CREATE INDEX idx_game_title ON games(title);
CREATE INDEX idx_game_release_date ON games(release_date);
CREATE INDEX idx_game_average_rating ON games(average_rating);
CREATE INDEX idx_game_igdb_id ON games(igdb_id);
CREATE INDEX idx_game_rawg_id ON games(rawg_id);
CREATE INDEX idx_game_title ON games(title);
CREATE INDEX idx_game_release_date ON games(release_date);
CREATE INDEX idx_game_average_rating ON games(average_rating);

-- Reviews table
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    content TEXT NOT NULL,
    is_draft BOOLEAN NOT NULL DEFAULT 0,
    playtime_hours INTEGER,
    platform VARCHAR(50),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    published_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    UNIQUE(user_id, game_id)
);
CREATE INDEX idx_review_user_id ON reviews(user_id);
CREATE INDEX idx_review_game_id ON reviews(game_id);
CREATE INDEX idx_review_published_at ON reviews(published_at) WHERE is_draft = 0;
CREATE INDEX idx_review_rating ON reviews(rating);

-- Friendships table
CREATE TABLE friendships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    friend_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL CHECK(status IN ('pending', 'accepted', 'declined')),
    requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    responded_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (friend_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, friend_id),
    CHECK(user_id != friend_id)
);
CREATE INDEX idx_friendship_user_id ON friendships(user_id);
CREATE INDEX idx_friendship_friend_id ON friendships(friend_id);
CREATE INDEX idx_friendship_status ON friendships(status);

-- Linked accounts table
CREATE TABLE linked_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK(platform IN ('steam', 'playstation', 'xbox')),
    platform_user_id VARCHAR(255) NOT NULL,
    platform_username VARCHAR(255),
    access_token TEXT, -- Encrypted
    refresh_token TEXT, -- Encrypted
    token_expires_at DATETIME,
    connected_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_synced_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, platform),
    UNIQUE(platform, platform_user_id)
);
CREATE INDEX idx_linked_account_user_id ON linked_accounts(user_id);
CREATE INDEX idx_linked_account_platform ON linked_accounts(platform);

-- Game library table
CREATE TABLE game_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    linked_account_id INTEGER,
    playtime_hours INTEGER NOT NULL DEFAULT 0,
    achievements_count INTEGER NOT NULL DEFAULT 0,
    last_played_at DATETIME,
    imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    FOREIGN KEY (linked_account_id) REFERENCES linked_accounts(id) ON DELETE SET NULL,
    UNIQUE(user_id, game_id, linked_account_id)
);
CREATE INDEX idx_game_library_user_id ON game_library(user_id);
CREATE INDEX idx_game_library_game_id ON game_library(game_id);

-- User preferences table
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    preference_type VARCHAR(20) NOT NULL CHECK(preference_type IN ('enjoyed', 'disliked')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    UNIQUE(user_id, game_id)
);
CREATE INDEX idx_user_pref_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_pref_game_id ON user_preferences(game_id);

-- Recommendations table
CREATE TABLE recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    score REAL NOT NULL CHECK(score BETWEEN 0.0 AND 1.0),
    reasoning TEXT,
    is_dismissed BOOLEAN NOT NULL DEFAULT 0,
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    algorithm_version VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);
CREATE INDEX idx_recommendation_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendation_score ON recommendations(score);
CREATE INDEX idx_recommendation_dismissed ON recommendations(is_dismissed);

-- Enable WAL mode for better concurrency
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
```

---

## Migration Strategy

**Alembic Migrations**:
1. Initial migration: Create all tables with indexes
2. Seed migration: Add sample games from IGDB/GiantBomb
3. Future migrations: Schema changes versioned and reversible

**Data Seeding**:
- Import 10k+ games from IGDB API or public datasets
- Create indexes after bulk import for performance
- Implement incremental sync for new games

---

## Query Optimization Patterns

**Common Queries**:
1. **User Feed**: Get friend reviews ordered by date
   ```sql
   SELECT r.* FROM reviews r
   JOIN friendships f ON (f.user_id = ? AND f.friend_id = r.user_id AND f.status = 'accepted')
   WHERE r.is_draft = 0
   ORDER BY r.published_at DESC
   LIMIT 20 OFFSET ?;
   ```

2. **Game Reviews**: Get all reviews for a game
   ```sql
   SELECT r.*, u.username, u.avatar_url 
   FROM reviews r
   JOIN users u ON r.user_id = u.id
   WHERE r.game_id = ? AND r.is_draft = 0
   ORDER BY r.published_at DESC;
   ```

3. **User Profile**: Get user with review count
   ```sql
   SELECT u.*, COUNT(r.id) as review_count
   FROM users u
   LEFT JOIN reviews r ON u.id = r.user_id AND r.is_draft = 0
   WHERE u.id = ?
   GROUP BY u.id;
   ```

**Performance Tips**:
- Use composite indexes for frequently combined filters
- Implement cursor-based pagination for feeds
- Cache aggregated ratings and counts
- Use SELECT DISTINCT wisely to avoid duplicates
