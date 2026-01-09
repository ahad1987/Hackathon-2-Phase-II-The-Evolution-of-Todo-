# Current Auth Implementation Snapshot

## Backend JWT Flow

### 1. User Registration (POST /api/v1/auth/signup)
```
Input: { email, password }
→ Validate email format
→ Hash password with bcrypt
→ Create user in database
→ Generate JWT token using BETTER_AUTH_SECRET
→ Return: { user: { id, email, created_at }, token }
```

### 2. User Login (POST /api/v1/auth/login)
```
Input: { email, password }
→ Find user by email
→ Verify password hash
→ Generate JWT token
→ Return: { user: { id, email, created_at }, token }
```

### 3. JWT Verification (Middleware)
```
Request with Authorization: Bearer <token>
→ Extract token from header
→ Verify signature using BETTER_AUTH_SECRET
→ Decode claims → Extract user_id
→ Attach user_id to request context
→ Proceed to route handler
```

### 4. Protected Routes (tasks)
```
GET /api/v1/tasks
→ Middleware extracts user_id from JWT
→ Query: SELECT * FROM tasks WHERE user_id = <current_user_id>
→ Return tasks (user isolation enforced)
```

## Frontend Auth Flow

### 1. Auth Context (React)
```
- Maintains: user (id, email), isAuthenticated, isLoading, error
- Methods: login(email, password), signup(email, password), logout()
- On mount: Checks for existing token in cookie, validates with /auth/me
```

### 2. Token Management
```
- Stored in: document.cookie (auth_token) with 24-hour expiry
- Sent with all API requests via: Authorization: Bearer <token>
- Cleared on logout or 401 response
```

### 3. Protected Routes
```
- / → Redirects to /login (if not auth) or /tasks (if auth)
- /login → Accessible only when not authenticated
- /signup → Accessible only when not authenticated
- /tasks → Requires valid JWT token
```

## Key Security Properties

✅ Passwords: Hashed with bcrypt (not stored in plaintext)
✅ Tokens: Signed JWT using BETTER_AUTH_SECRET
✅ Cookies: HTTP-only (inaccessible to JavaScript)
✅ Transmission: HTTPS only (in production)
✅ Validation: Email format check, password length check (8+ chars)
✅ User Isolation: Enforced at database query level

## Current Dependencies

### Backend (Python)
- fastapi: HTTP framework
- pyjwt: JWT token creation/verification
- bcrypt: Password hashing
- sqlmodel: ORM and schema definition
- python-dotenv: Environment variable loading

### Frontend (JavaScript)
- next: React framework
- axios: HTTP client
- react-context-api: State management
- tailwindcss: Styling

## Environment Variables

### Required
- BETTER_AUTH_SECRET: Used for JWT signing/verification (keep secret!)
- DATABASE_URL: PostgreSQL connection string

### Optional
- JWT_EXPIRY: Token expiration time (default: 86400 = 24 hours)
- API_BASE_URL: Backend URL (default: http://localhost:8000)
- NEXT_PUBLIC_API_URL: Frontend API endpoint (public, safe)

## Testing the Current System

### Manual Test Checklist
```bash
# 1. Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}'

# 3. Get current user (with token)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <token>"

# 4. List tasks
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <token>"
```

