---
type: spec
scope: [system, api]
status: active
date: 2026-04-10
source_of_truth: false
tags: [auth, behavior]
---

# Authentication behavior

## Login flow

1. User submits username/password on LoginPage
2. `POST /auth/login` → verify bcrypt password
3. Backend creates JWT (HS256), stores session in SessionStore, sets HTTP-only cookie
4. Frontend receives 200, AuthProvider updates state (isAuthenticated = true)
5. RequireAuth allows access to admin routes

## Session validation (every authenticated request)

1. `get_current_user()` dependency extracts `session_token` cookie
2. Validates session exists in SessionStore
3. Checks activity timeout (last_activity vs now)
4. Verifies JWT signature and expiry
5. Loads user from UserRepository
6. Updates `last_activity` timestamp
7. Returns User (or raises 401)

## Single session enforcement

New login invalidates any existing session for the same user. Only one active session per username.

## Frontend mount check

AuthProvider calls `GET /auth/me` on mount to check existing session cookie. If valid → `isAuthenticated = true`. If 401 → `isAuthenticated = false`.

## RequireAuth guard

Checks `isAuthenticated`. If false → redirect to `/admin/login` with saved location for post-login redirect. If loading → shows "Loading...".

## Legacy admin token

`require_admin_token()` in `deps.py` currently returns hardcoded `"dev-admin"`. Applied to `/upload` POST and `/art/catalog/update` POST alongside session auth.

## Related

- [Auth structure](../architecture/architecture--system--authentication.md)
