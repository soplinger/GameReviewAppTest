# iOS App Integration Guide (Game Review API)

This guide documents everything needed to build a feature-complete iOS app against the backend in `backend/src`.

## Base URL

- Local: `http://localhost:8000/api/v1`
- Production: `https://<your-domain>/api/v1`

## Authentication Model

The API uses JWT Bearer tokens.

- Send `Authorization: Bearer <access_token>` for authenticated endpoints.
- Access tokens expire quickly.
- Refresh tokens are rotated via `/auth/refresh`.
- On logout, delete tokens locally (`/auth/logout` is informational for parity).

### Auth Endpoints

#### `POST /auth/register`
Create account.

Request:
```json
{
  "username": "player_one",
  "email": "player@example.com",
  "password": "SuperStrong123"
}
```

#### `POST /auth/login`
Returns session payload for mobile token lifecycle management.

Response:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "access_token_expires_in": 900,
  "refresh_token_expires_in": 604800
}
```

#### `POST /auth/refresh`
Rotate tokens.

Request:
```json
{ "refresh_token": "..." }
```

Response matches `/auth/login`.

#### `GET /auth/me`
Get currently authenticated user profile.

#### `POST /auth/logout`
Stateless logout acknowledgement. iOS must clear tokens from Keychain.

---

## Core App Features / Endpoints

## Games

- `GET /games/search?query=<query>&page=<n>&page_size=<n>`
- `GET /games/popular`
- `GET /games/recent`
- `GET /games/{game_id}`
- `GET /games/slug/{slug}`

## Reviews

- `POST /reviews/` create review
- `PUT /reviews/{review_id}` update own review
- `DELETE /reviews/{review_id}` delete own review
- `GET /reviews/{review_id}` get single review
- `GET /reviews/?game_id=<id>&page=<n>&page_size=<n>`
- `GET /reviews/?user_id=<id>&page=<n>&page_size=<n>`
- `GET /reviews/users/me/reviews`
- `GET /reviews/feed` (friend activity feed)
- `POST /reviews/{review_id}/helpful`
- `GET /reviews/games/{game_id}/suggested-playtime`

## Social

- `POST /social/friends/request`
- `PUT /social/friends/{friendship_id}` (action: accept/decline/block)
- `DELETE /social/friends/{friend_id}`
- `GET /social/friends`
- `GET /social/friends/requests`
- `GET /social/users/search?query=<username>`
- `GET /social/friends/{user_id}/status`

## OAuth-linked game libraries

- `GET /oauth/{platform}` (get provider auth URL)
- `GET /oauth/{platform}/callback`
- `GET /oauth/accounts/me`
- `DELETE /oauth/accounts/{platform}`
- `POST /oauth/library/sync`
- `GET /oauth/library/sync/status/{job_id}`
- `GET /oauth/library/sync/jobs`
- `GET /oauth/library/me`
- `GET /oauth/library/games/{game_id}/playtime`

---

## iOS Architecture Recommendation

- `AuthManager`: login/register/refresh/logout, Keychain storage.
- `APIClient`: generic request layer with automatic bearer injection.
- `TokenRefreshInterceptor`: if 401 and refresh token exists, call `/auth/refresh`, retry once.
- `Repositories`:
  - `GamesRepository`
  - `ReviewsRepository`
  - `SocialRepository`
  - `LinkedAccountsRepository`

## Suggested Swift Models

```swift
struct AuthSession: Decodable {
    let accessToken: String
    let refreshToken: String
    let tokenType: String
    let accessTokenExpiresIn: Int
    let refreshTokenExpiresIn: Int
}

struct RefreshRequest: Encodable {
    let refreshToken: String
}
```

Use `CodingKeys` to map snake_case JSON to camelCase properties.

## Request/Response Conventions

- Validation/auth errors return standard FastAPI payload:
```json
{ "detail": "error message" }
```
- Paginated review responses include:
  - `reviews`
  - `total`
  - `page`
  - `page_size`
  - `total_pages`

---

## iOS Token Storage Rules

- Save `access_token` and `refresh_token` in Keychain only.
- Save expiry timestamps in Keychain/UserDefaults.
- Refresh proactively when token is near expiry (e.g., <60 seconds remaining).
- If refresh fails (401), force sign-out.

---

## Quick iOS Build Checklist

1. Implement auth screens (register/login).
2. Persist session in Keychain.
3. Add refresh-token retry middleware.
4. Build game search/details.
5. Build review CRUD + feed + profile reviews.
6. Build social search/friend requests/friend list.
7. Add linked account connect/sync flows via OAuth web view.
8. Add offline-safe UX for retries/loading/error states.

