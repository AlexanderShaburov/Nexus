---
type: architecture
scope: [system, api]
status: active
date: 2026-04-10
source_of_truth: true
tags: [auth, security]
---

# Authentication system structure

## Frontend components

| Component | Location | Role |
|-----------|----------|------|
| AuthProvider | `features/auth/authContext.tsx` | Provides `AuthContextValue` (user, login, logout, refetchUser) |
| RequireAuth | `app/guards/RequireAuth.tsx` | Route guard: redirects to `/admin/login` if unauthenticated |
| LoginPage | `pages/admin/LoginPage.tsx` | Login form |
| authApi | `features/auth/authApi.ts` | API calls with `credentials: 'include'` |

## Backend components

| Component | Location | Role |
|-----------|----------|------|
| Auth router | `routers/auth/auth.py` | Login/logout/me endpoints |
| SessionStore | `auth/session.py` | In-memory session tracking |
| Security | `auth/security.py` | JWT creation/validation, bcrypt |
| UserRepository | `auth/repository.py` | Loads users from `users.json` |
| get_current_user | `auth/dependencies.py` | FastAPI dependency for auth |

## Session model

- In-memory, per-process only
- Single session enforcement per user
- Activity timeout: configurable (default 30 min)
- JWT expiry: configurable (default 4 hours)

## Token type

JWT (HS256) stored as HTTP-only cookie named `session_token`.

## Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/auth/login` | POST | None | Login, set session cookie |
| `/auth/logout` | POST | Cookie | Logout, clear cookie |
| `/auth/me` | GET | Cookie | Current user info |

## Configuration

```python
secret_key: str
session_expire_minutes: int = 240
activity_timeout_minutes: int = 30
```

## Related

- [Auth behavior](../specs/spec--system--authentication-behavior.md)
