# Game Review Social Platform - Backend

FastAPI backend for the Game Review Social Platform.

## Setup

### Prerequisites

- Python 3.11 or higher
- pip and virtualenv

### Installation

```bash
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

# Edit .env and add your API keys
```

### Database Setup

```bash
# Create database directory
mkdir database

# Run migrations
alembic upgrade head
```

### Running the Server

```bash
# Development server with auto-reload
uvicorn src.main:app --reload --port 8000
```

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_services/test_auth_service.py
```

### Code Quality

```bash
# Lint
ruff check src/

# Format
black src/

# Type check
mypy src/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── api/             # API routes
│   ├── services/        # Business logic
│   ├── repositories/    # Data access layer
│   ├── core/            # Core configuration
│   └── main.py          # Application entry point
├── tests/               # Test files
├── alembic/             # Database migrations
├── scripts/             # Utility scripts
└── requirements.txt     # Python dependencies
```

## Constitution Compliance

This project follows the GameReviewApp Constitution v1.0.0:
- Code Quality: Functions <50 lines, complexity ≤10
- Testing: TDD workflow, 80% coverage minimum
- Performance: p95 <500ms API response times
