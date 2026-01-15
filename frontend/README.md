# Game Review Social Platform - Frontend

React + TypeScript frontend for the Game Review Social Platform.

## Setup

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create .env file
copy .env.example .env.local  # Windows
# or
cp .env.example .env.local    # macOS/Linux
```

### Running the Development Server

```bash
npm run dev
```

Application will be available at http://localhost:5173

## Development

### Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Lint
npm run lint

# Type check
npm run type-check

# Format code
npm run format
```

### Code Quality

```bash
# Check linting and types
npm run lint && npm run type-check

# Auto-fix linting issues
npm run lint:fix

# Format all files
npm run format
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   ├── pages/           # Page components
│   ├── services/        # API services
│   ├── contexts/        # React contexts
│   ├── hooks/           # Custom hooks
│   ├── lib/             # Utilities
│   ├── types/           # TypeScript types
│   └── test/            # Test utilities
├── public/              # Static assets
└── tests/               # Test files
```

## Constitution Compliance

This project follows the GameReviewApp Constitution v1.0.0:
- Code Quality: Functions <50 lines, complexity ≤10
- Testing: 80% coverage minimum
- UX: WCAG 2.1 AA compliance, responsive design
- Performance: FCP <1.5s, TTI <3.5s
