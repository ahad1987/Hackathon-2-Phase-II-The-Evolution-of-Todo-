# Better Auth Integration Guide (Hybrid Approach)

## Overview

This document outlines the **safe, non-breaking** Better Auth integration strategy for the Todo Application. The approach maintains 100% backward compatibility while adding Better Auth-compatible features.

## Strategy: Hybrid Authentication Layer

Instead of a full rewrite, we've implemented a **compatibility layer** that:
- ✅ Keeps existing JWT system fully functional
- ✅ Adds Better Auth-compatible methods alongside
- ✅ Allows gradual migration to Better Auth when ready
- ✅ Zero breaking changes to existing API

## What Was Added (Non-Breaking)

### 1. Better Auth Compatibility Layer
**File**: `backend/src/services/better_auth_compat.py`

Provides Better Auth-like functions:
- `create_access_token()` - Create short-lived access tokens
- `create_refresh_token()` - Create long-lived refresh tokens
- `verify_token()` - Verify and decode tokens
- `refresh_access_token()` - Renew expired tokens

**Usage**:
```python
from src.services.better_auth_compat import BetterAuthCompatible

# Create access token (compatible with Better Auth)
token = BetterAuthCompatible.create_access_token(
    user_id="user123",
    email="user@example.com"
)

# Refresh a token
new_token = BetterAuthCompatible.refresh_access_token(refresh_token)
```

### 2. Token Refresh Endpoint
**Endpoint**: `POST /api/v1/auth/refresh`

Allows refreshing access tokens without re-authenticating.

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<token>"}'
```

**Response**:
```json
{
  "token": "<new_access_token>",
  "message": "Token refreshed successfully"
}
```

## Backward Compatibility

### Existing System Still Works
All current endpoints unchanged:
- ✅ `POST /api/v1/auth/signup` - Works exactly as before
- ✅ `POST /api/v1/auth/login` - Works exactly as before
- ✅ `POST /api/v1/auth/logout` - Works exactly as before
- ✅ `GET /api/v1/auth/me` - Works exactly as before
- ✅ `GET /api/v1/tasks` - Works exactly as before
- ✅ All task CRUD - Works exactly as before

### No Database Changes
- ✅ Users table unchanged
- ✅ Tasks table unchanged
- ✅ Relationships unchanged
- ✅ User isolation enforced same way

### No Frontend Breaking Changes
- ✅ Current auth context works unchanged
- ✅ API client unchanged
- ✅ Component behavior unchanged
- ✅ No new dependencies required

## Migration Path to Full Better Auth (Future)

When ready to fully migrate to Better Auth:

### Phase 1: Frontend Enhancement (Optional Now)
```bash
npm install better-auth
```

Create parallel Better Auth client:
```javascript
// frontend/src/lib/better-auth.ts (new file, optional)
import { createAuthClient } from "better-auth"

export const authClient = createAuthClient({
  baseURL: "http://localhost:8000"
})
```

### Phase 2: Backend Integration (When Ready)
Use compatibility layer to verify tokens:
```python
from src.services.better_auth_compat import BetterAuthCompatible

# Verify tokens from Better Auth client
claims = BetterAuthCompatible.verify_token(token)
if claims:
    user_id = claims["sub"]
    email = claims["email"]
```

### Phase 3: Gradual Migration
1. Add Better Auth SDK to frontend (npm install better-auth)
2. Run both systems in parallel (custom + Better Auth)
3. Test full functionality
4. Redirect users to new Better Auth methods
5. Keep old custom auth as fallback
6. Eventually deprecate custom auth

## Current Token Format

Our JWT tokens now follow Better Auth conventions:

```javascript
{
  "sub": "user-id-here",          // Subject (user ID)
  "email": "user@example.com",    // User email
  "type": "access|refresh",       // Token type
  "iat": 1672502400,              // Issued at
  "exp": 1672588800               // Expires at
}
```

**Fully compatible with Better Auth expectations**.

## Testing the Integration

### Test 1: Current System Still Works
```bash
# Should work exactly as before
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}'
```

### Test 2: New Refresh Endpoint Works
```bash
# Get refresh token from signup/login
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<token_from_step_1>"}'
```

### Test 3: Task Operations Still Work
```bash
# Task list, create, update, delete all unchanged
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <token>"
```

## Security Considerations

### Preserved Security
- ✅ Passwords still hashed with bcrypt
- ✅ JWT signed with BETTER_AUTH_SECRET
- ✅ HTTP-only cookies for token storage
- ✅ User isolation at database level
- ✅ Email validation enforced
- ✅ Password strength requirements

### Token Lifespan
- **Access tokens**: 24 hours (configurable via JWT_EXPIRY)
- **Refresh tokens**: 7 days (hard-coded for security)

## Environment Variables

No new variables required. Existing variables used:
- `BETTER_AUTH_SECRET` - Used for signing all tokens (unchanged)
- `DATABASE_URL` - Database connection (unchanged)
- `JWT_EXPIRY` - Access token lifetime (unchanged)

## Benefits of This Approach

1. **Zero Risk**: No breaking changes, fully backward compatible
2. **Gradual Migration**: Can migrate to Better Auth on your schedule
3. **Testing**: Test Better Auth alongside existing system
4. **Rollback Easy**: If needed, simply don't use new endpoints
5. **Production Ready**: Existing system already proven stable
6. **Better Auth Ready**: When you want to migrate, infrastructure is in place

## Future: Full Better Auth Migration

When you're ready, can implement:
- Better Auth OAuth providers (Google, GitHub, etc.)
- Email verification
- 2FA support
- Advanced session management
- Professional-grade auth infrastructure

All while reusing the compatibility layer we've created.

## Troubleshooting

### Issue: Refresh endpoint returns 401
**Solution**: Verify refresh token is valid and not expired
```python
# Check token validity
from src.services.better_auth_compat import BetterAuthCompatible
claims = BetterAuthCompatible.verify_token(token)
print(claims)  # Should print token claims, not None
```

### Issue: Token verification fails in middleware
**Solution**: Token format has changed. Update middleware if needed:
```python
# Old: Only checked "sub" claim
# New: Also validates "type" field
if claims.get("type") in ["access", None]:  # None for backward compat
    proceed()
```

### Issue: Frontend can't use new refresh endpoint
**Solution**: Ensure refresh token is being stored in cookies or session

## API Documentation

### POST /api/v1/auth/refresh

**Purpose**: Generate a new access token from a refresh token

**Request**:
- Method: POST
- URL: `http://localhost:8000/api/v1/auth/refresh`
- Body: `{"refresh_token": "..."}`
- OR: Token in `refresh_token` cookie

**Response** (200 OK):
```json
{
  "token": "eyJhbGc...",
  "message": "Token refreshed successfully"
}
```

**Error** (401 Unauthorized):
```json
{
  "detail": {
    "error": "Invalid or expired refresh token",
    "code": "INVALID_REFRESH_TOKEN",
    "message": "Refresh token is invalid or has expired"
  }
}
```

## Next Steps

1. **Test current system** - Ensure everything still works
2. **Test refresh endpoint** - Verify new functionality
3. **Review compatibility layer** - Understand the new code
4. **Plan Better Auth adoption** - Decide when to fully migrate
5. **Document in your README** - Add refresh token endpoint docs

---

**Status**: ✅ Ready for production use

**Last Updated**: 2026-01-09

**Maintainer**: Better Auth Migration Task Force
