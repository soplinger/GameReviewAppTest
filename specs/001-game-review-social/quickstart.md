# Quickstart Guide: Game Review Social Platform

**Feature**: 001-game-review-social  
**Stack**: FastAPI + React + Tailwind + SQLite  
**Updated**: 2026-01-14

## Prerequisites

### Required Software

- **Python**: 3.11 or higher ([Download](https://www.python.org/downloads/))
- **Node.js**: 18 or higher ([Download](https://nodejs.org/))
- **Git**: Latest version
- **Code Editor**: VS Code recommended

### Optional Tools

- **Postman** or **Insomnia**: API testing
- **DB Browser for SQLite**: Database inspection
- **React Developer Tools**: Browser extension

---

## Quick Setup (5 Minutes)

### 1. Clone Repository

```bash
git clone <repository-url>
cd GameReviewAppTest
git checkout 001-game-review-social
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
# or
cp .env.example .env    # macOS/Linux

# Run database migrations
alembic upgrade head

# Seed database with sample games (optional)
python scripts/seed_games.py

# Start development server
uvicorn src.main:app --reload
```

Backend will be running at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Create .env file
copy .env.example .env.local  # Windows
# or
cp .env.example .env.local    # macOS/Linux

# Start development server
npm run dev
```

Frontend will be running at: http://localhost:5173

### 4. Verify Installation

1. Open http://localhost:5173 in browser
2. Register a new account
3. Create your first game review
4. Check API docs at http://localhost:8000/docs

---

## Project Structure

```
GameReviewAppTest/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API routes
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── repositories/   # Data access
│   │   ├── core/           # Config, security
│   │   └── main.py         # App entry point
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API clients
│   │   ├── hooks/          # Custom hooks
│   │   ├── store/          # State management
│   │   └── styles/         # Tailwind CSS
│   ├── tests/              # Frontend tests
│   ├── package.json        # Node dependencies
│   └── .env.local          # Environment variables
│
└── database/               # SQLite database file
    └── gamereviews.db
```

---

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=sqlite:///./database/gamereviews.db

# Security
SECRET_KEY=your-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# OAuth (Optional - for gaming account linking)
STEAM_API_KEY=your_steam_api_key
STEAM_WEB_API_KEY=your_steam_web_api_key
XBOX_CLIENT_ID=your_xbox_client_id
XBOX_CLIENT_SECRET=your_xbox_client_secret
PSN_CLIENT_ID=your_psn_client_id
PSN_CLIENT_SECRET=your_psn_client_secret

# Game Data APIs (Required for game database)
IGDB_CLIENT_ID=your_twitch_client_id
IGDB_CLIENT_SECRET=your_twitch_client_secret
RAWG_API_KEY=your_rawg_api_key  # Free tier: 20k requests/month

# Email (Optional - for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
```

### Frontend (.env.local)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME="Game Review Platform"
```

---

## Common Commands

### Backend

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run development server
uvicorn src.main:app --reload --port 8000

# Run tests
pytest                           # All tests
pytest tests/unit               # Unit tests only
pytest tests/integration        # Integration tests
pytest --cov=src --cov-report=html  # With coverage

# Database migrations
alembic revision --autogenerate -m "Description"  # Create migration
alembic upgrade head                               # Apply migrations
alembic downgrade -1                               # Rollback one migration

# Game database seeding (initial setup)
python scripts/seed_games_from_igdb.py --limit 10000  # Seed 10k popular games
python scripts/sync_new_games.py --days 7             # Fetch new releases (last 7 days)

# Code quality
ruff check src/              # Lint code
black src/                   # Format code
mypy src/                    # Type checking
```

### Frontend

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test                     # Unit tests
npm run test:ui             # Tests with UI
npm run test:e2e            # End-to-end tests

# Code quality
npm run lint                 # ESLint
npm run format               # Prettier
npm run type-check           # TypeScript checking
```

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. TDD Workflow (Constitutional Requirement)

**Backend**:
```bash
# 1. Write failing test
# tests/unit/test_services/test_review_service.py

# 2. Run test (should fail - RED)
pytest tests/unit/test_services/test_review_service.py -v

# 3. Implement feature
# src/services/review_service.py

# 4. Run test (should pass - GREEN)
pytest tests/unit/test_services/test_review_service.py -v

# 5. Refactor if needed
# Improve code while keeping tests green
```

**Frontend**:
```bash
# 1. Write failing test
# src/components/__tests__/ReviewForm.test.tsx

# 2. Run test (should fail - RED)
npm test ReviewForm

# 3. Implement component
# src/components/reviews/ReviewForm.tsx

# 4. Run test (should pass - GREEN)
npm test ReviewForm

# 5. Refactor if needed
```

### 3. Code Quality Checks

```bash
# Backend
ruff check src/ && black --check src/ && mypy src/ && pytest

# Frontend
npm run lint && npm run type-check && npm test
```

### 4. Commit and Push

```bash
git add .
git commit -m "feat: add review creation feature"
git push origin feature/your-feature-name
```

---

## Testing

### Backend Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_services/test_auth_service.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

**Test Structure**:
- `tests/unit/`: Unit tests for services, repositories, utilities
- `tests/integration/`: API endpoint tests, database integration
- `tests/e2e/`: Complete user flow tests

### Frontend Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test -- --watch

# Run E2E tests
npm run test:e2e

# Run specific test file
npm test ReviewForm
```

**Test Structure**:
- `src/**/__tests__/`: Component and hook tests
- `tests/e2e/`: Playwright end-to-end tests

---

## Database Management

### Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Add review platform field"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### Database Inspection

```bash
# Open SQLite database (if you have sqlite3 CLI)
sqlite3 database/gamereviews.db

# Or use DB Browser for SQLite (GUI tool)
# Download from: https://sqlitebrowser.org/
```

### Reset Database

```bash
# WARNING: This deletes all data!
rm database/gamereviews.db
alembic upgrade head
python scripts/seed_games.py
```

---

## API Documentation

### Swagger UI
- **URL**: http://localhost:8000/docs
- **Features**: Interactive API testing, request/response examples
- **Authentication**: Use "Authorize" button with Bearer token

### ReDoc
- **URL**: http://localhost:8000/redoc
- **Features**: Clean, readable API documentation

### OpenAPI JSON
- **URL**: http://localhost:8000/openapi.json
- **Use**: Import into Postman, Insomnia, or other API clients

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

**Problem**: `OperationalError: unable to open database file`
```bash
# Solution: Create database directory
mkdir database
alembic upgrade head
```

**Problem**: `Port 8000 already in use`
```bash
# Solution: Kill process or use different port
uvicorn src.main:app --reload --port 8001
```

**Problem**: `IGDB API authentication failed`
```bash
# Solution: Get Twitch OAuth credentials
# 1. Register app at https://dev.twitch.tv/console/apps
# 2. Create new application
# 3. Copy Client ID and Client Secret to .env
# 4. Test with: curl -X POST https://id.twitch.tv/oauth2/token \
#    -d "client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&grant_type=client_credentials"
```

**Problem**: `RAWG API rate limit exceeded`
```bash
# Solution: Get free API key at https://rawg.io/apidocs
# Add to .env: RAWG_API_KEY=your_key
# Free tier: 20,000 requests/month
```

### Frontend Issues

**Problem**: `Cannot find module 'react'`
```bash
# Solution: Install dependencies
rm -rf node_modules package-lock.json
npm install
```

**Problem**: `API requests failing (CORS error)`
```bash
# Solution: Check backend .env CORS_ORIGINS includes frontend URL
# Add http://localhost:5173 to CORS_ORIGINS
```

**Problem**: `Vite port 5173 in use`
```bash
# Solution: Change port in vite.config.ts or kill process
npm run dev -- --port 3000
```

### Database Issues

**Problem**: `alembic.util.exc.CommandError: Can't locate revision`
```bash
# Solution: Reset migrations
rm alembic/versions/*.py
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## Performance Optimization

### Backend

1. **Enable SQLite WAL mode** (in database.py):
   ```python
   PRAGMA journal_mode=WAL;
   ```

2. **Use async endpoints**:
   ```python
   @router.get("/reviews")
   async def get_reviews(db: AsyncSession = Depends(get_db)):
       ...
   ```

3. **Add database indexes** (see data-model.md)

4. **Implement caching** for frequently accessed data

### Frontend

1. **Code splitting**:
   ```tsx
   const ReviewForm = lazy(() => import('./components/reviews/ReviewForm'));
   ```

2. **Virtual scrolling** for long lists (react-window)

3. **Image optimization**:
   - Use WebP format
   - Lazy load images
   - Responsive sizes

4. **React Query caching**:
   ```tsx
   const { data } = useQuery(['games'], fetchGames, {
     staleTime: 5 * 60 * 1000, // 5 minutes
   });
   ```

---

## Security Best Practices

1. **Never commit .env files** - Already in .gitignore
2. **Use strong SECRET_KEY** - Generate with: `openssl rand -hex 32`
3. **Enable HTTPS in production** - Use reverse proxy (nginx, Caddy)
4. **Implement rate limiting** - Add slowapi middleware
5. **Validate all inputs** - Pydantic schemas enforce this
6. **Hash passwords** - bcrypt already configured
7. **Sanitize user content** - Prevent XSS attacks

---

## Next Steps

1. ✅ Setup complete - Development environment ready
2. ⏭️ **Get API credentials** (see below) for game data
3. ⏭️ Read [spec.md](spec.md) for feature requirements
4. ⏭️ Review [data-model.md](data-model.md) for database schema
5. ⏭️ Check [contracts/](contracts/) for API contracts
6. ⏭️ Run game database seeding script
7. ⏭️ Run `/speckit.tasks` to generate task breakdown
8. ⏭️ Start implementing with TDD workflow

---

## Getting API Credentials

### IGDB (Primary Game Database - Required)

1. **Create Twitch Developer Account**: https://dev.twitch.tv/console/apps
2. **Register Application**:
   - Name: "Game Review Platform"
   - OAuth Redirect URLs: http://localhost
   - Category: Application Integration
3. **Copy Credentials**:
   - Client ID → `IGDB_CLIENT_ID` in .env
   - Client Secret → `IGDB_CLIENT_SECRET` in .env
4. **Test Authentication**:
   ```bash
   curl -X POST "https://id.twitch.tv/oauth2/token" \
     -d "client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&grant_type=client_credentials"
   ```
5. **Rate Limits**: 4 requests/second, 500,000 requests/month (free)

### RAWG (Fallback Game Database - Recommended)

1. **Sign Up**: https://rawg.io/signup
2. **Get API Key**: https://rawg.io/apidocs (auto-generated on signup)
3. **Copy Key**:
   - API Key → `RAWG_API_KEY` in .env
4. **Test API**:
   ```bash
   curl "https://api.rawg.io/api/games?key=YOUR_API_KEY&page_size=5"
   ```
5. **Rate Limits**: 20,000 requests/month (free tier)

### Steam API (Optional - For Account Linking)

1. **Get Steam API Key**: https://steamcommunity.com/dev/apikey
2. **Domain**: localhost
3. **Copy Key**:
   - Steam Web API Key → `STEAM_WEB_API_KEY` in .env

---

## Additional Resources

### Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **Tailwind CSS**: https://tailwindcss.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Alembic**: https://alembic.sqlalchemy.org/
- **IGDB API**: https://api-docs.igdb.com/
- **RAWG API**: https://rawg.io/apidocs

### Tools
- **DB Browser for SQLite**: https://sqlitebrowser.org/
- **Postman**: https://www.postman.com/
- **React Query**: https://tanstack.com/query/

### Testing
- **pytest**: https://docs.pytest.org/
- **Vitest**: https://vitest.dev/
- **Playwright**: https://playwright.dev/
- **React Testing Library**: https://testing-library.com/react

---

## Support

For questions or issues:
1. Check this quickstart guide
2. Review [research.md](research.md) for best practices
3. Check API docs at `/docs`
4. Review test examples in `tests/` directories
