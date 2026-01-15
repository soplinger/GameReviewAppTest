# Research: Game Review Social Platform

**Feature**: 001-game-review-social  
**Created**: 2026-01-14  
**Purpose**: Technology research and best practices for FastAPI + React + SQLite stack

## Phase 0: Research & Technology Decisions

### 1. Backend Framework: FastAPI

**Decision**: Use FastAPI 0.109+ for backend REST API

**Rationale**:
- **Performance**: ASGI-based, async/await support, handles 500+ req/s easily
- **Type Safety**: Pydantic integration provides automatic validation and serialization
- **Documentation**: Auto-generates OpenAPI/Swagger documentation
- **Modern**: Built-in support for async operations, WebSocket (future real-time features)
- **Developer Experience**: Fast development, excellent IDE support with type hints

**Alternatives Considered**:
- Flask: Simpler but lacks async support and auto-documentation
- Django REST Framework: More features but heavier, slower, overkill for this scope
- Node.js/Express: Would require JavaScript on backend, team prefers Python

**Best Practices**:
- Use dependency injection for database sessions, authentication
- Implement repository pattern for data access
- Use Pydantic schemas for request/response validation
- Enable CORS middleware for frontend integration
- Implement rate limiting with slowapi
- Use async SQLAlchemy for database operations

**Key Patterns**:
```python
# Dependency injection
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

# Router organization
@router.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, db: AsyncSession = Depends(get_db)):
    ...
```

---

### 2. Game Database Source: IGDB & RAWG APIs

**Decision**: Use IGDB (Internet Game Database) API as primary source, RAWG API as secondary

**Rationale**:
- **IGDB**: Comprehensive game metadata (500k+ games), free tier available, owned by Twitch/Amazon
- **RAWG**: 800k+ games, completely free, well-documented REST API, no authentication required
- **Coverage**: Both cover PC, console, and mobile games across all platforms
- **Data Quality**: Professional-grade metadata including covers, screenshots, genres, developers
- **Active Maintenance**: Both APIs actively maintained and updated with new releases

**IGDB API Details**:
- **Endpoint**: https://api.igdb.com/v4/
- **Authentication**: Twitch OAuth (Client ID + Secret)
- **Rate Limits**: Free tier: 4 requests/second, 500,000 requests/month
- **Data Available**: Games, platforms, genres, companies, release dates, cover art, screenshots
- **Documentation**: https://api-docs.igdb.com/

**RAWG API Details**:
- **Endpoint**: https://api.rawg.io/api/
- **Authentication**: API key (free, no credit card required)
- **Rate Limits**: 20,000 requests/month free tier
- **Data Available**: Games, platforms, genres, developers, publishers, stores, ratings
- **Documentation**: https://rawg.io/apidocs

**Alternatives Considered**:
- **GiantBomb**: Good data but limited free tier, complex API
- **Steam API**: Only Steam games, limited metadata
- **OpenCritic**: Focused on review scores, not comprehensive game database
- **Manual Entry**: Too much work, won't scale

**Implementation Strategy**:

1. **Initial Seeding** (one-time):
   ```python
   # Seed 10k-50k popular games on first setup
   # Prioritize: recent releases, popular franchises, high-rated games
   python scripts/seed_games_from_igdb.py --limit 10000
   ```

2. **Incremental Updates** (daily cron job):
   ```python
   # Fetch new releases and updates daily
   # Only fetch games released in last 7 days
   python scripts/sync_new_games.py --days 7
   ```

3. **On-Demand Search**:
   - User searches for game not in local database
   - Search IGDB/RAWG APIs in real-time
   - Cache result in local database for future use
   - This handles long-tail games

4. **Fallback Strategy**:
   - Try IGDB first (primary)
   - If IGDB rate limit hit or failure, use RAWG (secondary)
   - If both fail, allow manual game entry (with admin approval)

**Data Mapping**:
```python
# Map IGDB response to our Game model
{
    "title": igdb.name,
    "slug": igdb.slug,
    "description": igdb.summary,
    "release_date": igdb.first_release_date,
    "developer": igdb.involved_companies[0].company.name,
    "publisher": igdb.involved_companies[1].company.name,
    "cover_image_url": f"https://images.igdb.com/igdb/image/upload/t_cover_big/{igdb.cover.image_id}.jpg",
    "platforms": [p.name for p in igdb.platforms],
    "genres": [g.name for g in igdb.genres]
}
```

**API Client Implementation**:
```python
# backend/src/services/game_data_service.py
class GameDataService:
    async def search_external_games(self, query: str) -> List[dict]:
        """Search IGDB and RAWG for games, cache results"""
        # Try IGDB first
        try:
            results = await self.igdb_client.search(query)
            if results:
                return results
        except RateLimitError:
            logger.warning("IGDB rate limit hit, falling back to RAWG")
        
        # Fallback to RAWG
        return await self.rawg_client.search(query)
    
    async def import_game(self, external_id: int, source: str) -> Game:
        """Import game from external API to local database"""
        if source == "igdb":
            data = await self.igdb_client.get_game(external_id)
        else:
            data = await self.rawg_client.get_game(external_id)
        
        # Map to our schema and save
        game = self.map_to_game_model(data)
        return await self.game_repository.create(game)
```

**Caching Strategy**:
- Cache API responses for 24 hours (Redis or in-memory)
- Store imported games permanently in SQLite
- Update game metadata weekly for active games
- Never re-fetch unless explicitly requested

**Cost & Rate Limit Management**:
- IGDB: Stay within 4 req/sec, monitor monthly quota
- RAWG: Stay within 20k requests/month
- Implement exponential backoff on errors
- Cache aggressively to minimize API calls
- Queue bulk imports to respect rate limits

**Best Practices**:
- Always include API key/credentials in .env (never commit)
- Handle rate limits gracefully with retry logic
- Validate and sanitize API responses before storing
- Log all external API calls for monitoring
- Implement circuit breaker pattern for API failures
- Have manual entry fallback for edge cases

---

### 3. Database: SQLite with SQLAlchemy

**Decision**: Use SQLite 3.40+ with SQLAlchemy 2.0+ ORM for local storage

**Rationale**:
- **Local Storage**: Requirement specified - no external database server needed
- **Simplicity**: File-based, zero configuration, perfect for development and small deployments
- **Performance**: Handles 100k users, 1M reviews efficiently with proper indexing
- **ACID Compliance**: Full transaction support for data integrity
- **SQLAlchemy**: ORM provides abstraction, easy to switch to PostgreSQL later if needed

**Limitations & Mitigations**:
- **Concurrency**: Limited write concurrency → Use WAL mode, queue writes if needed
- **Scaling**: Single file → Can migrate to PostgreSQL when reaching ~100k concurrent users
- **Backup**: File-based → Implement regular backup schedule, use SQLite backup API

**Best Practices**:
- Enable WAL (Write-Ahead Logging) mode for better concurrency
- Create indexes on foreign keys and frequently queried fields
- Use connection pooling (even for SQLite)
- Implement proper transaction management
- Use alembic for database migrations
- Implement soft deletes for critical data (users, reviews)

**Schema Design Principles**:
- Normalize data to 3NF to reduce redundancy
- Use foreign keys with CASCADE for referential integrity
- Index on: user_id, game_id, timestamps, friendship pairs
- Use composite indexes for common query patterns

---

### 3. Frontend: React 18 + Tailwind CSS

**Decision**: React 18 with TypeScript, Tailwind CSS 3, Vite bundler

**Rationale**:
- **React 18**: Industry standard, large ecosystem, concurrent features for better UX
- **TypeScript**: Type safety reduces bugs, better IDE support, aligns with Pydantic schemas
- **Tailwind CSS**: Utility-first, rapid development, responsive design, small bundle size
- **Vite**: Fast HMR, modern build tool, better than Create React App

**Alternatives Considered**:
- Vue.js: Good but smaller ecosystem, team more familiar with React
- Svelte: Excellent performance but smaller community, fewer libraries
- Plain CSS/SCSS: More control but slower development than Tailwind

**Component Architecture**:
- **Atomic Design**: atoms (buttons, inputs) → molecules (form fields) → organisms (forms) → pages
- **Smart/Dumb Components**: Container components for logic, presentational for UI
- **Custom Hooks**: Encapsulate API calls, state management, side effects

**State Management**:
- **React Query**: Server state caching, automatic refetch, optimistic updates
- **Context API**: Global auth state, theme, user preferences
- **Avoid Redux**: Overkill for this scope, React Query + Context sufficient

**Best Practices**:
- Code splitting with React.lazy() for route-based chunks
- Use React.memo() for expensive components
- Implement virtual scrolling for long lists (feed, search results)
- Use Tailwind @apply for reusable component styles
- Implement error boundaries for graceful error handling
- Use Suspense for loading states

---

### 4. Authentication & Security

**Decision**: JWT-based authentication with bcrypt password hashing

**Rationale**:
- **JWT**: Stateless, scalable, works well with REST APIs
- **bcrypt**: Industry standard for password hashing, resistant to brute force
- **OAuth**: For gaming platform integrations (Steam, PSN, Xbox)

**Implementation Approach**:
- **Access Tokens**: Short-lived (15 min), stored in httpOnly cookies
- **Refresh Tokens**: Long-lived (7 days), rotation on use
- **Password Requirements**: Min 8 chars, complexity validation
- **Rate Limiting**: Login attempts, API endpoints
- **CORS**: Whitelist frontend origin only

**Security Best Practices**:
- Never store passwords in plaintext
- Use HTTPS in production (TLS/SSL)
- Implement CSRF protection for state-changing operations
- Sanitize user inputs to prevent XSS/SQL injection
- Use parameterized queries (SQLAlchemy handles this)
- Implement content security policy (CSP) headers
- Regular dependency updates for security patches

---

### 5. Gaming Platform OAuth Integration

**Decision**: Use authlib for OAuth 2.0 integration with Steam, PlayStation, Xbox

**Rationale**:
- **Steam**: OpenID + Steam Web API for game library, playtime
- **PlayStation**: PlayStation Network OAuth (limited public API)
- **Xbox**: Xbox Live API via Microsoft Graph

**Integration Strategy**:
- Implement OAuth flow: redirect → authenticate → callback → exchange token
- Store tokens encrypted in database
- Periodic sync of game library and playtime (daily/on-demand)
- Graceful degradation if API unavailable
- Manual entry fallback if OAuth fails

**API Endpoints**:
- Steam Web API: GetOwnedGames, GetPlayerSummaries
- Xbox Live: /profile/gamepass, /userstats
- PlayStation: Limited - may need to use unofficial APIs or manual entry

**Challenges & Solutions**:
- **PSN Limitations**: No official public API → May use community APIs or require manual entry
- **Rate Limiting**: Respect API rate limits, cache data, implement backoff
- **Token Expiry**: Implement refresh token flow, re-authentication prompts

---

### 6. Recommendation Algorithm

**Decision**: Collaborative filtering initially, prepare for ML enhancement

**Rationale**:
- **Start Simple**: Item-based collaborative filtering (users who liked X also liked Y)
- **Scalable**: Can enhance with ML (TensorFlow, scikit-learn) as data grows
- **User Preferences**: Weight explicit likes/dislikes higher than ratings

**Algorithm Approach**:
1. **Content-Based**: Recommend games with similar genres/developers
2. **Collaborative**: Find similar users, recommend their highly-rated games
3. **Hybrid**: Combine both approaches with weighted scores
4. **Fallback**: Trending/popular games when insufficient data

**Implementation**:
- Calculate recommendations async (background job)
- Cache recommendations, refresh daily or on new reviews
- Use similarity metrics: cosine similarity, Pearson correlation
- Store pre-computed recommendations in database

---

### 7. Performance Optimization

**Backend**:
- **Async/Await**: Use FastAPI async handlers for I/O operations
- **Database Indexing**: Index foreign keys, user_id, game_id, timestamps
- **Query Optimization**: Use joins, avoid N+1 queries, use select_in_loading
- **Caching**: Redis for future scaling, in-memory for now (functools.lru_cache)
- **Pagination**: Cursor-based for feeds, offset for search results
- **Connection Pooling**: AsyncIO-compatible pool for SQLAlchemy

**Frontend**:
- **Code Splitting**: Route-based, lazy load heavy components
- **Image Optimization**: WebP format, lazy loading, responsive sizes
- **Bundle Size**: Tree shaking, minimize dependencies, analyze bundle
- **Virtual Scrolling**: For infinite scroll feeds (react-window)
- **Debouncing**: Search inputs, API calls
- **Service Worker**: Cache static assets, offline fallback

---

### 8. Testing Strategy

**Backend Testing**:
- **Unit Tests (70%)**: Services, repositories, utilities (pytest)
- **Integration Tests (20%)**: API endpoints, database operations (httpx)
- **E2E Tests (10%)**: Critical user flows (pytest + httpx)
- **Coverage**: 80% minimum, 95% for auth/review/social modules
- **Fixtures**: Factory pattern for test data, separate test database

**Frontend Testing**:
- **Unit Tests (70%)**: Components, hooks, utilities (Vitest + RTL)
- **Integration Tests (20%)**: Multi-component interactions, forms
- **E2E Tests (10%)**: Full user flows (Playwright)
- **Coverage**: 80% minimum
- **Mocking**: MSW for API mocking, test-utils for common setups

**Test Best Practices**:
- Write tests before code (TDD)
- Test behavior, not implementation
- Use meaningful test names (should/when/given format)
- Keep tests isolated and deterministic
- Use factories/fixtures for test data
- Mock external dependencies (OAuth, third-party APIs)

---

### 9. Accessibility (WCAG 2.1 AA)

**Requirements**:
- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Screen Readers**: ARIA labels, semantic HTML, alt text for images
- **Color Contrast**: 4.5:1 for normal text, 3:1 for large text
- **Focus Indicators**: Visible focus states for all interactive elements
- **Forms**: Labels, error messages, validation feedback

**Implementation**:
- Use semantic HTML (nav, main, article, section)
- Implement skip links for main content
- Test with screen readers (NVDA, JAWS, VoiceOver)
- Use axe-core for automated accessibility testing
- Ensure all images have meaningful alt text
- Provide text alternatives for icon-only buttons

---

### 10. Development Tools & Workflow

**Backend**:
- **Linting**: ruff (fast Python linter), mypy (type checking)
- **Formatting**: black (code formatter), isort (import sorting)
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **API Docs**: FastAPI auto-generates Swagger UI at /docs
- **Migrations**: Alembic for database schema versioning

**Frontend**:
- **Linting**: ESLint with TypeScript rules
- **Formatting**: Prettier
- **Type Checking**: TypeScript strict mode
- **Testing**: Vitest, React Testing Library, Playwright
- **Build**: Vite with TypeScript, Tailwind PostCSS

**CI/CD**:
- **GitHub Actions**: Run tests on PR, lint, type check
- **Code Coverage**: Upload to Codecov, enforce thresholds
- **Deployment**: Automated deploy on merge to main
- **Pre-commit Hooks**: Lint, format, type check before commit

---

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend Framework | FastAPI | 0.109+ | REST API, async operations |
| Backend Language | Python | 3.11+ | Type-safe, fast development |
| Database | SQLite | 3.40+ | Local file-based storage |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Validation | Pydantic | 2.0+ | Request/response schemas |
| Frontend Framework | React | 18+ | Component-based UI |
| Frontend Language | TypeScript | 5.0+ | Type-safe JavaScript |
| Styling | Tailwind CSS | 3+ | Utility-first CSS |
| Build Tool | Vite | 5+ | Fast bundling, HMR |
| State Management | React Query | 5+ | Server state caching |
| Authentication | JWT | - | Stateless auth |
| OAuth | authlib | 1.3+ | Gaming platform integration |
| Testing (Backend) | pytest | 7+ | Python testing |
| Testing (Frontend) | Vitest | 1+ | Fast unit testing |
| E2E Testing | Playwright | 1.40+ | Browser automation |
| Code Quality | ruff, ESLint | Latest | Linting |
| Formatting | black, Prettier | Latest | Code formatting |
| Type Checking | mypy, TypeScript | Latest | Static analysis |

---

## Risk Assessment & Mitigation

### Technical Risks

1. **SQLite Concurrency**
   - Risk: Write lock contention with high concurrent writes
   - Mitigation: WAL mode, write queuing, migrate to PostgreSQL if needed

2. **Gaming API Rate Limits**
   - Risk: Steam/Xbox/PSN APIs may rate limit or become unavailable
   - Mitigation: Caching, backoff retry, manual entry fallback, queue requests

3. **Recommendation Quality**
   - Risk: Poor recommendations with limited data (cold start problem)
   - Mitigation: Fallback to trending/popular, collect explicit preferences, hybrid approach

4. **OAuth Token Security**
   - Risk: Token theft, unauthorized access
   - Mitigation: Encryption at rest, HTTPS, httpOnly cookies, token rotation

### Operational Risks

1. **Database Backup**
   - Risk: SQLite file corruption, data loss
   - Mitigation: Automated backups, WAL checkpoints, transaction logs

2. **Scalability Ceiling**
   - Risk: SQLite hits limits at ~100k concurrent users
   - Mitigation: Design for PostgreSQL migration, use SQLAlchemy abstraction

3. **Performance Degradation**
   - Risk: Slow queries, large database file
   - Mitigation: Indexing, query optimization, pagination, archiving old data

---

## Next Steps (Phase 1)

1. ✅ Define data model and entity relationships → `data-model.md`
2. ✅ Design API contracts (OpenAPI specs) → `contracts/`
3. ✅ Create development quickstart guide → `quickstart.md`
4. ✅ Update agent context with technology stack
5. ⏭️ Proceed to task breakdown (Phase 2)
