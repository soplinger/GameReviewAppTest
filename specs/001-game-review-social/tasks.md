# Tasks: Game Review Social Platform

**Feature**: 001-game-review-social  
**Input**: Design documents from `specs/001-game-review-social/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/  
**Generated**: 2026-01-14

## Format: `- [ ] [ID] [P?] [Story] Description`

- **[P]**: Parallelizable (different files, no blocking dependencies)
- **[Story]**: User story identifier (US1, US2, US3, US4, US5)
- All tasks include exact file paths for implementation

## Implementation Strategy

**MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1 - Review Creation)

**Delivery Approach**: 
- Complete Setup and Foundational phases first (blocking prerequisites)
- Implement User Stories in priority order (P1 → P2 → P3 → P4)
- Each user story is independently testable
- Parallel opportunities exist within each phase

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize project structure, dependencies, and development tooling

**Constitution Compliance**: Establish quality gates and tooling per all 4 principles

- [X] T001 Create backend project structure at backend/ with src/, tests/, alembic/ directories
- [X] T002 Create frontend project structure at frontend/ with src/, public/, tests/ directories
- [X] T003 [P] Initialize Python project with requirements.txt (FastAPI 0.109+, SQLAlchemy 2.0+, Pydantic 2.0+, pytest 7+, ruff, black, mypy)
- [X] T004 [P] Initialize Node.js project with package.json (React 18+, TypeScript 5+, Tailwind CSS 3+, Vite 5+, Vitest)
- [X] T005 [P] Configure backend linting (ruff) and formatting (black) in pyproject.toml with zero warnings policy
- [X] T006 [P] Configure frontend linting (ESLint) and formatting (Prettier) in .eslintrc.json and .prettierrc with zero warnings policy
- [X] T007 [P] Setup Python type checking with mypy in pyproject.toml (strict mode)
- [X] T008 [P] Setup TypeScript strict mode in tsconfig.json
- [X] T009 [P] Configure pytest with coverage reporting (80% threshold) in pytest.ini
- [X] T010 [P] Configure Vitest with coverage reporting in vite.config.ts
- [ ] T011 [P] Setup Playwright for E2E testing in tests/e2e/
- [X] T012 [P] Create .env.example files for backend and frontend with all required variables
- [ ] T013 [P] Setup pre-commit hooks for linting, formatting, and type checking
- [X] T014 [P] Create backend/README.md and frontend/README.md with setup instructions
- [X] T015 Configure Tailwind CSS with design tokens (colors, spacing, typography) in tailwind.config.js
- [X] T016 [P] Setup accessibility testing with axe-core in frontend tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Constitution Compliance**: Infrastructure supports all 4 core principles

### Database & Configuration

- [X] T017 Create SQLite database configuration in backend/src/core/database.py with WAL mode and connection pooling
- [X] T018 Initialize Alembic for migrations in backend/alembic/
- [X] T019 Create environment configuration in backend/src/core/config.py using Pydantic settings
- [X] T020 Create initial database migration for schema in backend/alembic/versions/

### Authentication & Security

- [X] T021 Implement password hashing utilities in backend/src/core/security.py using passlib with bcrypt
- [X] T022 Implement JWT token generation and validation in backend/src/core/security.py using python-jose
- [X] T023 Create User model in backend/src/models/user.py with all attributes from data-model.md
- [ ] T024 Create user authentication schema in backend/src/schemas/auth.py (register, login, token response)
- [ ] T025 Create user repository in backend/src/repositories/user_repository.py with CRUD operations
- [ ] T026 Implement authentication service in backend/src/services/auth_service.py (register, login, token refresh)
- [ ] T027 Create authentication dependency in backend/src/api/deps.py (get_current_user, get_db)
- [ ] T028 Implement authentication endpoints in backend/src/api/v1/auth.py per contracts/auth.yaml
- [ ] T029 [P] Setup CORS middleware in backend/src/main.py for frontend origin

### Game Data Integration (External APIs)

- [ ] T030 [P] Create IGDB API client in backend/src/services/external/igdb_client.py with OAuth authentication
- [ ] T031 [P] Create RAWG API client in backend/src/services/external/rawg_client.py with API key authentication
- [ ] T032 Create Game model in backend/src/models/game.py with igdb_id, rawg_id, last_synced_at fields
- [ ] T033 Create game repository in backend/src/repositories/game_repository.py with search and filter operations
- [ ] T034 Implement game data service in backend/src/services/game_data_service.py with API fallback logic
- [X] T035 Create game seeding script in backend/scripts/seed_games_from_igdb.py for initial 10k popular games
- [ ] T036 Create incremental sync script in backend/scripts/sync_new_games.py for daily updates

### Frontend Foundation

- [ ] T037 Create API client configuration in frontend/src/lib/api.ts with axios and base URL
- [ ] T038 Create auth context in frontend/src/contexts/AuthContext.tsx for global auth state
- [ ] T039 Setup React Router in frontend/src/App.tsx with route definitions
- [ ] T040 [P] Create base UI components in frontend/src/components/ui/ (Button, Input, Card, Spinner, Toast)
- [ ] T041 [P] Create layout components in frontend/src/components/layout/ (Header, Footer, Sidebar, Container)
- [ ] T042 [P] Create form components in frontend/src/components/forms/ (FormField, FormError, FormLabel)
- [ ] T043 Setup React Query in frontend/src/main.tsx for data fetching and caching

### Error Handling & Logging

- [ ] T044 [P] Create error handling middleware in backend/src/core/errors.py with custom exceptions
- [ ] T045 [P] Setup structured logging in backend/src/core/logging.py using structlog
- [ ] T046 [P] Create error boundary component in frontend/src/components/ErrorBoundary.tsx

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Publish Game Reviews (Priority: P1) 🎯 MVP

**Goal**: Enable users to write, edit, and publish reviews with ratings, creating the core content of the platform

**Independent Test**: Create account → Search for game → Write review with rating → Publish → Verify appears on profile

**Value Delivered**: Users can share gaming experiences and opinions (minimum viable product)

### Backend - Review Management

- [X] T047 [US1] Create Review model in backend/src/models/review.py with all attributes from data-model.md
- [X] T048 [US1] Create review repository in backend/src/repositories/review_repository.py (create, update, delete, get by user/game)
- [X] T049 [US1] Create review schemas in backend/src/schemas/review.py (create, update, response, list)
- [X] T050 [US1] Implement review service in backend/src/services/review_service.py with validation (one review per user/game, rating 1-5, content min 50 chars)
- [X] T051 [US1] Implement review endpoints in backend/src/api/v1/reviews.py per contracts/reviews.yaml (POST /reviews, PUT /reviews/{id}, DELETE /reviews/{id}, GET /reviews/{id}, GET /users/me/reviews)

### Backend - Game Database Access

- [X] T052 [P] [US1] Create game schemas in backend/src/schemas/game.py (game detail, game list, game search)
- [X] T053 [P] [US1] Implement game service in backend/src/services/game_service.py (search, get details, aggregate ratings calculation)
- [X] T054 [P] [US1] Implement game endpoints in backend/src/api/v1/games.py per contracts/games.yaml (GET /games/search, GET /games/{id})

### Frontend - Authentication Pages

- [X] T055 [P] [US1] Create registration page in frontend/src/pages/auth/RegisterPage.tsx with form validation
- [X] T056 [P] [US1] Create login page in frontend/src/pages/auth/LoginPage.tsx with JWT storage
- [X] T057 [P] [US1] Create protected route component in frontend/src/components/ProtectedRoute.tsx

### Frontend - Game Search & Discovery

- [X] T058 [P] [US1] Create game search service in frontend/src/services/gameService.ts with React Query hooks
- [X] T059 [P] [US1] Create game search page in frontend/src/pages/games/GameSearchPage.tsx with filters
- [X] T060 [P] [US1] Create game detail page in frontend/src/pages/games/GameDetailPage.tsx showing game info and reviews
- [X] T061 [P] [US1] Create GameCard component in frontend/src/components/games/GameCard.tsx for search results

### Frontend - Review Creation & Management

- [X] T062 [US1] Create review service in frontend/src/services/reviewService.ts with CRUD operations
- [X] T063 [US1] Create ReviewForm component in frontend/src/components/reviews/ReviewForm.tsx with star rating and text editor
- [X] T064 [US1] Create ReviewCard component in frontend/src/components/reviews/ReviewCard.tsx for displaying reviews
- [X] T065 [US1] Create user profile page in frontend/src/pages/profile/ProfilePage.tsx showing user's reviews
- [X] T066 [US1] Add review creation modal to game detail page with draft/publish toggle

### Testing - User Story 1

- [X] T067 [P] [US1] Unit tests for review service in backend/tests/unit/test_services/test_review_service.py (validation, permissions)
- [X] T068 [P] [US1] Unit tests for game service in backend/tests/unit/test_services/test_game_service.py (search, ratings)
- [X] T069 [P] [US1] Integration tests for review API in backend/tests/integration/test_api/test_reviews.py (CRUD operations)
- [X] T070 [P] [US1] Integration tests for game API in backend/tests/integration/test_api/test_games.py (search, details)
- [X] T071 [P] [US1] Component tests for ReviewForm in frontend/src/components/reviews/ReviewForm.test.tsx
- [X] T072 [P] [US1] Component tests for game search in frontend/src/pages/games/GameSearchPage.test.tsx
- [ ] T073 [US1] E2E test for complete review creation flow in tests/e2e/test_review_creation.spec.ts (SKIPPED - Playwright not configured)

**US1 Completion Criteria**: ✅ User can register, search games, write/edit/delete reviews, view reviews on profile

---

## Phase 4: User Story 2 - Social Feed with Friends' Reviews (Priority: P2)

**Goal**: Enable users to add friends and view a personalized feed of their reviews

**Independent Test**: Create 2 accounts → Send friend request → Accept → Post review → Verify in friend's feed

**Value Delivered**: Social discovery and network effects that differentiate from basic review sites

### Backend - Friendship Management

- [ ] T074 [US2] Create Friendship model in backend/src/models/friendship.py with status (pending/accepted/declined)
- [ ] T075 [US2] Create friendship repository in backend/src/repositories/friendship_repository.py (create request, update status, get friends list)
- [ ] T076 [US2] Create social schemas in backend/src/schemas/social.py (friend request, friend response, user search)
- [ ] T077 [US2] Implement social service in backend/src/services/social_service.py (send request, accept/decline, remove friend, search users)
- [ ] T078 [US2] Implement social endpoints in backend/src/api/v1/social.py per contracts/social.yaml (POST /friends/request, PUT /friends/{id}, DELETE /friends/{id}, GET /friends, GET /users/search)

### Backend - Feed Generation

- [ ] T079 [US2] Extend review repository with feed query in backend/src/repositories/review_repository.py (get reviews from friends, ordered by recency)
- [ ] T080 [US2] Implement feed service in backend/src/services/feed_service.py with pagination
- [ ] T081 [US2] Add feed endpoint to reviews router in backend/src/api/v1/reviews.py (GET /feed)

### Frontend - Friend Management

- [ ] T082 [P] [US2] Create social service in frontend/src/services/socialService.ts with friend request operations
- [ ] T083 [P] [US2] Create user search component in frontend/src/components/social/UserSearch.tsx
- [ ] T084 [P] [US2] Create friend list page in frontend/src/pages/social/FriendsPage.tsx showing friends and pending requests
- [ ] T085 [P] [US2] Create FriendRequestCard component in frontend/src/components/social/FriendRequestCard.tsx (accept/decline buttons)
- [ ] T086 [P] [US2] Create UserCard component in frontend/src/components/social/UserCard.tsx for search results with friend request button

### Frontend - Social Feed

- [ ] T087 [US2] Create feed service in frontend/src/services/feedService.ts with infinite scroll support
- [ ] T088 [US2] Create feed page in frontend/src/pages/feed/FeedPage.tsx showing friend reviews with pagination
- [ ] T089 [US2] Create FeedCard component in frontend/src/components/feed/FeedCard.tsx showing review with author info and game details
- [ ] T090 [US2] Add navigation link to feed in header component

### Testing - User Story 2

- [ ] T091 [P] [US2] Unit tests for social service in backend/tests/unit/test_services/test_social_service.py (friend logic, edge cases)
- [ ] T092 [P] [US2] Unit tests for feed service in backend/tests/unit/test_services/test_feed_service.py (pagination, ordering)
- [ ] T093 [P] [US2] Integration tests for social API in backend/tests/integration/test_api/test_social.py (friend requests, user search)
- [ ] T094 [P] [US2] Integration tests for feed API in backend/tests/integration/test_api/test_feed.py
- [ ] T095 [P] [US2] Component tests for FriendsPage in frontend/src/pages/social/FriendsPage.test.tsx
- [ ] T096 [P] [US2] Component tests for feed in frontend/src/pages/feed/FeedPage.test.tsx
- [ ] T097 [US2] E2E test for friendship and feed flow in tests/e2e/test_social_feed.spec.ts

**US2 Completion Criteria**: ✅ Users can search, add friends, accept requests, view feed of friend reviews

---

## Phase 5: User Story 3 - Link Gaming Accounts (Priority: P3)

**Goal**: Enable users to connect Steam/PSN/Xbox accounts to import play time and game libraries

**Independent Test**: Link Steam account → Verify play time imported → Reference in review

**Value Delivered**: Review credibility and automated data entry for better user experience

### Backend - OAuth Integration

- [ ] T098 [P] [US3] Create Steam OAuth client in backend/src/services/oauth/steam_oauth.py using authlib
- [ ] T099 [P] [US3] Create PSN OAuth client in backend/src/services/oauth/psn_oauth.py using authlib
- [ ] T100 [P] [US3] Create Xbox OAuth client in backend/src/services/oauth/xbox_oauth.py using authlib

### Backend - Account Linking

- [ ] T101 [US3] Create LinkedAccount model in backend/src/models/linked_account.py with platform type and sync date
- [ ] T102 [US3] Create GameLibrary model in backend/src/models/game_library.py with play time and achievements
- [ ] T103 [US3] Create linked account repository in backend/src/repositories/linked_account_repository.py
- [ ] T104 [US3] Create game library repository in backend/src/repositories/game_library_repository.py
- [ ] T105 [US3] Implement OAuth service in backend/src/services/oauth_service.py (initiate OAuth, callback handling, token storage, account unlinking)
- [ ] T106 [US3] Implement library sync service in backend/src/services/library_sync_service.py (import games and play time from each platform)
- [ ] T107 [US3] Add OAuth endpoints to auth router in backend/src/api/v1/auth.py (GET /oauth/{platform}, GET /oauth/{platform}/callback, DELETE /linked-accounts/{id})

### Backend - Play Time Integration

- [ ] T108 [US3] Extend review service to include play time from linked accounts in backend/src/services/review_service.py
- [ ] T109 [US3] Update review schema to include play_time_hours in backend/src/schemas/review.py
- [ ] T110 [US3] Add endpoint to get user's game library in backend/src/api/v1/auth.py (GET /users/me/library)

### Frontend - Account Linking UI

- [ ] T111 [P] [US3] Create OAuth service in frontend/src/services/oauthService.ts with platform linking flow
- [ ] T112 [P] [US3] Create linked accounts page in frontend/src/pages/settings/LinkedAccountsPage.tsx showing connected accounts
- [ ] T113 [P] [US3] Create PlatformLinkButton component in frontend/src/components/oauth/PlatformLinkButton.tsx (Steam/PSN/Xbox)
- [ ] T114 [P] [US3] Create LinkedAccountCard component in frontend/src/components/oauth/LinkedAccountCard.tsx showing platform icon and unlink button
- [ ] T115 [P] [US3] Create game library page in frontend/src/pages/library/GameLibraryPage.tsx showing imported games with play time
- [ ] T116 [US3] Update ReviewForm to display play time for linked accounts in frontend/src/components/reviews/ReviewForm.tsx

### Testing - User Story 3

- [ ] T117 [P] [US3] Unit tests for OAuth service in backend/tests/unit/test_services/test_oauth_service.py (token handling, errors)
- [ ] T118 [P] [US3] Unit tests for library sync in backend/tests/unit/test_services/test_library_sync_service.py (data mapping)
- [ ] T119 [P] [US3] Integration tests for OAuth flow in backend/tests/integration/test_api/test_oauth.py (mocked external APIs)
- [ ] T120 [P] [US3] Component tests for linked accounts in frontend/src/pages/settings/LinkedAccountsPage.test.tsx
- [ ] T121 [US3] E2E test for account linking flow in tests/e2e/test_oauth_linking.spec.ts (with mocked OAuth provider)

**US3 Completion Criteria**: ✅ Users can link gaming accounts, view imported library, see play time in reviews

---

## Phase 6: User Story 4 - Game Information Database (Priority: P3)

**Goal**: Provide comprehensive game search and filtering with detailed game information pages

**Independent Test**: Search for game by title → Filter by platform/genre → View game details page

**Value Delivered**: Easy game discovery and browsing for review creation

### Backend - Game Search Enhancement

- [ ] T122 [US4] Add full-text search index on game title in backend/alembic/versions/ migration
- [ ] T123 [US4] Extend game repository with advanced filtering in backend/src/repositories/game_repository.py (by platform, genre, release date range)
- [ ] T124 [US4] Enhance game service with multi-criteria search in backend/src/services/game_service.py
- [ ] T125 [US4] Add game filtering endpoints in backend/src/api/v1/games.py (GET /games with platform/genre query params)
- [ ] T126 [P] [US4] Create game metadata update service in backend/src/services/game_metadata_service.py for weekly sync of active games

### Frontend - Advanced Game Discovery

- [ ] T127 [P] [US4] Create advanced search filters component in frontend/src/components/games/GameFilters.tsx (platform, genre, release date)
- [ ] T128 [P] [US4] Enhance game search page with filters in frontend/src/pages/games/GameSearchPage.tsx
- [ ] T129 [P] [US4] Create game browse page in frontend/src/pages/games/GameBrowsePage.tsx with trending/new/top-rated sections
- [ ] T130 [P] [US4] Create game detail page enhancements in frontend/src/pages/games/GameDetailPage.tsx (aggregate ratings, review count, platform badges)
- [ ] T131 [P] [US4] Create GameMetadata component in frontend/src/components/games/GameMetadata.tsx (developer, publisher, release date, genres)

### Testing - User Story 4

- [ ] T132 [P] [US4] Unit tests for enhanced game search in backend/tests/unit/test_services/test_game_service.py (filtering, sorting)
- [ ] T133 [P] [US4] Integration tests for game filtering API in backend/tests/integration/test_api/test_games.py
- [ ] T134 [P] [US4] Component tests for game filters in frontend/src/components/games/GameFilters.test.tsx
- [ ] T135 [US4] E2E test for game discovery flow in tests/e2e/test_game_discovery.spec.ts

**US4 Completion Criteria**: ✅ Users can search/filter games by multiple criteria, view detailed game information

---

## Phase 7: User Story 5 - Personalized Game Recommendations (Priority: P4)

**Goal**: Generate personalized game recommendations based on review history and explicit preferences

**Independent Test**: Create 10+ reviews with varied ratings → Mark games as liked/disliked → View recommendations page

**Value Delivered**: Personalized discovery that helps users find new games matching their tastes

### Backend - Preference Management

- [ ] T136 [US5] Create UserPreference model in backend/src/models/user_preference.py with preference type (enjoyed/disliked)
- [ ] T137 [US5] Create Recommendation model in backend/src/models/recommendation.py with confidence score and reasoning
- [ ] T138 [US5] Create preference repository in backend/src/repositories/preference_repository.py
- [ ] T139 [US5] Create recommendation repository in backend/src/repositories/recommendation_repository.py

### Backend - Recommendation Engine

- [ ] T140 [US5] Implement recommendation service in backend/src/services/recommendation_service.py with collaborative filtering algorithm
- [ ] T141 [US5] Create recommendation schemas in backend/src/schemas/recommendation.py (recommendation response with reasoning)
- [ ] T142 [US5] Implement recommendation endpoints in backend/src/api/v1/recommendations.py per contracts/recommendations.yaml (GET /recommendations, POST /preferences, DELETE /recommendations/{id})
- [ ] T143 [US5] Create daily recommendation generation task in backend/scripts/generate_recommendations.py

### Frontend - Recommendations UI

- [ ] T144 [P] [US5] Create recommendation service in frontend/src/services/recommendationService.ts
- [ ] T145 [P] [US5] Create recommendations page in frontend/src/pages/recommendations/RecommendationsPage.tsx showing suggested games
- [ ] T146 [P] [US5] Create RecommendationCard component in frontend/src/components/recommendations/RecommendationCard.tsx with dismiss button and reasoning
- [ ] T147 [P] [US5] Add preference marking buttons to game detail page in frontend/src/pages/games/GameDetailPage.tsx (enjoyed/disliked)
- [ ] T148 [P] [US5] Create preferences management page in frontend/src/pages/preferences/PreferencesPage.tsx showing marked games

### Testing - User Story 5

- [ ] T149 [P] [US5] Unit tests for recommendation algorithm in backend/tests/unit/test_services/test_recommendation_service.py (collaborative filtering, fallback)
- [ ] T150 [P] [US5] Integration tests for recommendations API in backend/tests/integration/test_api/test_recommendations.py
- [ ] T151 [P] [US5] Component tests for recommendations page in frontend/src/pages/recommendations/RecommendationsPage.test.tsx
- [ ] T152 [US5] E2E test for recommendation flow in tests/e2e/test_recommendations.spec.ts

**US5 Completion Criteria**: ✅ Users receive personalized recommendations, can mark preferences, dismiss suggestions

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements, performance optimization, and production readiness

### Content Moderation

- [ ] T153 [P] Create report functionality in backend/src/services/moderation_service.py
- [ ] T154 [P] Add report endpoints in backend/src/api/v1/reviews.py (POST /reviews/{id}/report)
- [ ] T155 [P] Create moderation page in frontend/src/pages/admin/ModerationPage.tsx (admin only)

### Performance Optimization

- [ ] T156 [P] Implement Redis caching for frequently accessed data in backend/src/core/cache.py
- [ ] T157 [P] Add database query optimization and eager loading in repositories
- [ ] T158 [P] Implement virtual scrolling for feed and search results in frontend
- [ ] T159 [P] Add image lazy loading and WebP optimization in frontend
- [ ] T160 [P] Implement code splitting and route-based lazy loading in frontend

### Accessibility & UX Polish

- [ ] T161 [P] Audit all pages with axe-core and fix violations (WCAG 2.1 AA)
- [ ] T162 [P] Add keyboard navigation support for all interactive elements
- [ ] T163 [P] Add screen reader announcements for dynamic content updates
- [ ] T164 [P] Implement loading skeleton screens for all async content
- [ ] T165 [P] Add optimistic UI updates for friend requests and reviews

### Security Hardening

- [ ] T166 [P] Implement rate limiting on all API endpoints in backend/src/core/rate_limit.py
- [ ] T167 [P] Add CSRF protection for state-changing operations
- [ ] T168 [P] Implement API input validation and sanitization
- [ ] T169 [P] Add security headers (CSP, HSTS, X-Frame-Options) in backend middleware

### Documentation & Monitoring

- [ ] T170 [P] Generate OpenAPI documentation and test in Swagger UI
- [ ] T171 [P] Add API usage examples to all endpoint docstrings
- [ ] T172 [P] Setup error tracking and monitoring (Sentry or equivalent)
- [ ] T173 [P] Create deployment documentation in docs/deployment.md
- [ ] T174 [P] Add component storybook for design system documentation

---

## Dependencies & Parallel Execution

### Dependency Graph (User Story Completion Order)

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKING for all user stories
    ↓
    ├→ Phase 3 (US1 - P1) ← MVP - MUST complete first
    │       ↓
    ├→ Phase 4 (US2 - P2) ← Depends on US1 (reviews must exist for feed)
    │       ↓
    ├→ Phase 5 (US3 - P3) ← Independent of US2, can run parallel after US1
    │
    ├→ Phase 6 (US4 - P3) ← Independent of US2/US3, can run parallel after US1
    │
    └→ Phase 7 (US5 - P4) ← Depends on US1 (needs review data)
            ↓
Phase 8 (Polish) ← Final cross-cutting improvements
```

### Parallel Execution Examples

**After Phase 2 (Foundational) Completion**:
- Start Phase 3 (US1) - MUST complete for MVP

**After Phase 3 (US1) Completion**:
- Phase 4 (US2) AND Phase 5 (US3) AND Phase 6 (US4) can ALL run in parallel
- Phase 7 (US5) can also start but needs review data

**Within Each Phase**:
- Tasks marked [P] can run in parallel (different files)
- Backend and frontend work can proceed simultaneously
- Testing can be done in parallel with implementation (TDD approach)

**Example: Phase 3 Parallel Work**:
- T047-T051 (Backend review logic)
- T052-T054 (Backend game logic) - Parallel
- T055-T057 (Frontend auth) - Parallel
- T058-T061 (Frontend games) - Parallel
- T062-T066 (Frontend reviews) - After review service complete
- T067-T073 (All tests) - Parallel during implementation (TDD)

---

## Task Summary

**Total Tasks**: 174
- Phase 1 (Setup): 16 tasks
- Phase 2 (Foundational): 30 tasks (T017-T046)
- Phase 3 (US1 - MVP): 27 tasks (T047-T073)
- Phase 4 (US2): 24 tasks (T074-T097)
- Phase 5 (US3): 24 tasks (T098-T121)
- Phase 6 (US4): 14 tasks (T122-T135)
- Phase 7 (US5): 17 tasks (T136-T152)
- Phase 8 (Polish): 22 tasks (T153-T174)

**Parallelization**:
- 89 tasks marked [P] (51% parallelizable)
- Backend/Frontend work can proceed simultaneously
- User stories US2, US3, US4 can run in parallel after US1

**MVP Scope** (Suggested First Delivery):
- Phase 1: Setup (T001-T016)
- Phase 2: Foundational (T017-T046)
- Phase 3: User Story 1 (T047-T073)
- **Total MVP Tasks**: 73 tasks

**Estimated MVP Timeline**: 3-4 weeks for 1 developer, 2-3 weeks for 2 developers (with parallelization)

---

## Format Validation ✅

All tasks follow required format:
- ✅ Checkbox: `- [ ]` prefix
- ✅ Task ID: Sequential T001-T174
- ✅ [P] marker: 89 tasks parallelizable
- ✅ [Story] label: All Phase 3-7 tasks have US1-US5 labels
- ✅ File paths: Specific paths included in descriptions
- ✅ Organized by user story: Each phase = one user story (except setup/foundational/polish)

**Independent Test Criteria per Story**:
- US1: Create account → Write review → Publish → View on profile ✅
- US2: Add friend → Post review → View in friend's feed ✅
- US3: Link account → Import play time → Reference in review ✅
- US4: Search games → Filter by criteria → View details ✅
- US5: Create reviews → Mark preferences → View recommendations ✅
