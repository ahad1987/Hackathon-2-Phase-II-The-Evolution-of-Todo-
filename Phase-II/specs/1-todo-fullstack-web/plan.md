# Implementation Plan: Todo Full-Stack Web Application (Phase II)

**Branch**: `1-todo-fullstack-web` | **Date**: 2026-01-09 | **Spec**: [specs/1-todo-fullstack-web/spec.md](spec.md)
**Input**: Feature specification from `/specs/1-todo-fullstack-web/spec.md`

## Summary

Build a secure, multi-user todo web application by architecting three layers: Better Auth (authentication), FastAPI backend (authorization + task CRUD), and Next.js frontend (protected routes + task UI). Core approach: authenticate first, enforce user isolation on every query, persist data with user_id constraints. JWT tokens verify user identity across frontend and backend using shared secret. All CRUD operations scoped to authenticated user ID.

---

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/JavaScript (frontend)
**Primary Dependencies**: FastAPI (backend), Next.js 16+ (frontend), SQLModel (ORM), Better Auth (authentication)
**Storage**: PostgreSQL via Neon Serverless
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: Web (Linux server backend, modern browsers)
**Project Type**: Full-stack web application (monorepo with backend + frontend)
**Performance Goals**: Sub-second response for CRUD operations; support 5+ concurrent users in Phase II
**Constraints**: User isolation mandatory on all queries; JWT verification on every protected endpoint; no manual coding
**Scale/Scope**: Single-user (per authenticated session) task management; 8 user stories; 5 endpoints minimum

---

## Constitution Check

✅ **GATE: PASS** (all constitutional principles applicable and achievable)

**Verified Principles**:
- ✅ **Spec-Driven Development**: All implementation traces to 31 functional requirements (FR-001 through FR-031) in approved spec
- ✅ **Security by Design**: JWT authentication mandatory; user isolation enforced on all CRUD; 401/403 errors defined
- ✅ **Separation of Concerns**: Three layers clearly isolated (Better Auth ↔ FastAPI ↔ Next.js); no cross-layer business logic
- ✅ **Correctness Over Cleverness**: REST semantics enforced (POST for create, PUT for update, DELETE for remove); user-scoped queries
- ✅ **Evolvability**: Monorepo structure (frontend + backend separated); SQLModel ORM supports schema evolution; API contracts stable for Phase III

**No Complexity Violations**: Monorepo with 2 subprojects (frontend + backend) is justified by architecture (separation of concerns). Better Auth handles auth complexity so backend doesn't reimp lement. SQLModel ORM justified by data relationships and schema extensibility.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Browser / Next.js Frontend                  │
│  (Protected Routes, Task UI, JWT Token Storage, API Client)    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST + JWT Bearer Token
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Task API Layer)                   │
│  (Auth Middleware, User-Scoped Queries, CRUD Endpoints)        │
└────────────────────────────┬────────────────────────────────────┘
                             │ SQL + Connection Pool
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│          PostgreSQL / Neon (User & Task Data Storage)           │
│       (user_id foreign keys, isolation constraints)             │
└─────────────────────────────────────────────────────────────────┘

Parallel to Frontend + Backend:
┌─────────────────────────────────────────────────────────────────┐
│              Better Auth (Auth Service)                         │
│  (User Registration, Login, JWT Issuance, Session Management)   │
└────────────────────────────┬────────────────────────────────────┘
                             │ Shared Secret: BETTER_AUTH_SECRET
                             ↓ (Frontend validates, Backend verifies)
```

**Trust Boundaries**:
- **Public**: Signup, Login endpoints (no auth required)
- **Authenticated**: All task endpoints, logout (JWT required)
- **Backend Authorization**: Every task read/write verifies user_id from JWT matches ownership

**Data Flow**:
1. User registers/logs in via Better Auth → JWT token issued
2. Frontend stores JWT in HTTP-only cookie (Better Auth default)
3. Frontend sends JWT in Authorization header on all task requests
4. Backend extracts user_id from JWT, verifies signature using shared secret
5. Backend queries tasks where user_id = authenticated user_id
6. Backend returns only user's tasks or 403 Forbidden if ownership mismatch

---

## Authentication & Authorization Planning

### Better Auth Responsibilities (Frontend Integration)

**Signup Flow**:
- Frontend renders signup form (email, password)
- User submits credentials to Better Auth service
- Better Auth validates email format, password strength
- Better Auth creates user record in backend database
- Better Auth issues JWT token containing user_id claim
- Frontend receives JWT and stores in secure HTTP-only cookie
- Frontend redirects to task list (protected route)

**Login Flow**:
- Frontend renders login form (email, password)
- User submits credentials to Better Auth service
- Better Auth validates credentials against stored hashed password
- Better Auth issues JWT token if valid
- Frontend stores JWT in secure HTTP-only cookie
- Frontend redirects to task list; subsequent requests include JWT

**Token Persistence**:
- JWT stored in HTTP-only cookie (cannot be accessed by JavaScript, protected from XSS)
- Cookie sent automatically on same-origin requests
- Cookie survives page refreshes until expiration or logout

**Logout Flow**:
- User clicks logout button
- Frontend deletes JWT from cookies
- Frontend clears auth state (user context/store)
- Frontend redirects to login page
- Subsequent requests to protected routes fail with 401, redirect to login

### JWT Structure & Verification Flow

**JWT Components**:
- Header: Algorithm (HS256), type (JWT)
- Payload: `user_id` (unique identifier), `email` (user email), `iat` (issued at), `exp` (expiration time)
- Signature: HMAC-SHA256(header.payload, BETTER_AUTH_SECRET)

**Shared Secret Management**:
- `BETTER_AUTH_SECRET` environment variable shared between frontend and backend
- Frontend uses secret to verify token signature (optional, for immediate validation)
- Backend uses secret to verify token signature on every request (mandatory)
- Secret must be at least 32 characters; stored in `.env` files (not committed)

**Token Expiration & Refresh**:
- Access token expires in 24 hours (configurable)
- Expired tokens return 401 Unauthorized from backend
- Frontend detects 401 and redirects user to login
- No refresh token flow in Phase II (simplest approach)

### Authorization Enforcement Strategy

**Middleware Layer**:
- Every FastAPI endpoint (except /auth/signup, /auth/login) decorated with auth requirement
- Middleware extracts JWT from Authorization header: `Authorization: Bearer <token>`
- Middleware verifies JWT signature using BETTER_AUTH_SECRET
- Middleware extracts user_id from verified JWT payload
- Middleware attaches user_id to request context for use by endpoints
- If JWT missing, invalid, or expired → return 401 Unauthorized

**Endpoint-Level Authorization**:
- Task endpoints receive authenticated user_id from middleware
- Endpoints query database with constraint: `WHERE user_id = authenticated_user_id`
- Endpoints verify ownership before allowing update/delete: if task.user_id ≠ authenticated_user_id → return 403 Forbidden
- Endpoints never trust user_id from request parameters; only trust JWT

---

## Backend Planning (FastAPI)

### API Layer Responsibilities

**Endpoint Structure**:
- `/auth/signup` - POST, public, creates user, issues JWT
- `/auth/login` - POST, public, validates credentials, issues JWT
- `/auth/logout` - POST, private (JWT required), invalidates session (frontend-side token deletion)
- `/tasks` - GET (private), returns authenticated user's tasks
- `/tasks` - POST (private), creates task for authenticated user
- `/tasks/{taskId}` - PUT (private), updates task (ownership verified)
- `/tasks/{taskId}` - DELETE (private), deletes task (ownership verified)

**Request/Response Structure** (conceptual, no code):
- All requests use standard HTTP methods and headers
- Authentication requests accept email + password in JSON body
- Task endpoints accept JSON body (title, description, completed status)
- All responses return JSON with consistent structure: `{ data: {...}, error: {...} }`
- Errors include `code` (e.g., "INVALID_EMAIL") and `message` for debugging

**Status Codes**:
- 200 OK: Successful GET, successful update
- 201 Created: Successful task creation
- 400 Bad Request: Validation error (invalid email, missing title)
- 401 Unauthorized: Missing, invalid, or expired JWT
- 403 Forbidden: Valid JWT but user lacks ownership (cross-user access attempt)
- 404 Not Found: Task doesn't exist
- 500 Internal Server Error: Database connection failure, unhandled exception

### JWT Verification Middleware Planning

**Flow**:
1. Request arrives at backend
2. Middleware checks if route requires authentication (all except /auth/signup, /auth/login)
3. Middleware extracts Authorization header
4. Middleware extracts token from `Bearer <token>` format
5. Middleware verifies signature using BETTER_AUTH_SECRET
6. If valid, middleware extracts user_id claim and attaches to request
7. If invalid/missing/expired, middleware returns 401 with clear error message
8. Endpoint handler receives request with user_id pre-verified

**Error Handling**:
- Missing Authorization header → 401 "Authorization header required"
- Invalid Bearer format → 401 "Invalid authorization header format"
- Signature verification failed → 401 "Invalid or expired token"
- Token expired → 401 "Token has expired"

### User-Scoped Data Access Enforcement

**Query Pattern**:
- Backend receives authenticated user_id from middleware
- All task queries include filter: `WHERE user_id = :user_id`
- Queries never use user_id from request parameters
- Example: GET /tasks → `SELECT * FROM tasks WHERE user_id = :authenticated_user_id`
- Example: PUT /tasks/123 → verify task.user_id = :authenticated_user_id, if not → 403

**Database Constraint**:
- Tasks table includes `user_id` foreign key referencing users.id
- Foreign key constraint ensures referential integrity
- Task cannot exist without valid user owner
- Database prevents orphaned tasks

### Error Handling Strategy

**Validation Errors** (400 Bad Request):
- Email format invalid
- Email already registered (signup)
- Password too short
- Task title empty
- Task title exceeds length limit
- Response includes field-level error details

**Authentication Errors** (401 Unauthorized):
- Email not found (login)
- Password incorrect (login)
- JWT missing or invalid
- JWT expired
- Response includes clear reason (no sensitive info exposure)

**Authorization Errors** (403 Forbidden):
- User attempts to access another user's task
- User attempts to modify another user's task
- Response: "Task not found" or "Forbidden" (no info about other users' tasks)

**Server Errors** (500 Internal Server Error):
- Database connection failure
- Unhandled exception
- Response includes generic message; detailed errors logged server-side

---

## Database Interaction Planning

### Conceptual Data Ownership Model

**User Entity**:
- Unique identifier (UUID or sequential)
- Email (unique, required)
- Hashed password (required)
- Created at timestamp
- Updated at timestamp (if password changes supported in Phase II)

**Task Entity**:
- Unique identifier (UUID or sequential)
- User ID (foreign key referencing users.id)
- Title (required, non-empty string, max length)
- Description (optional, string)
- Completed status (boolean, default false)
- Created at timestamp
- Updated at timestamp
- Constraints: user_id is non-null, unique constraint on (user_id, title) if needed

**Relationship**:
- One user has many tasks (1:N)
- Each task belongs to exactly one user
- Deleting a user cascade-deletes their tasks (or prevents deletion if tasks exist)
- Task visibility scoped to task.user_id = authenticated user_id

### Task Lifecycle & Persistence Flow

**Task Creation**:
1. User authenticated via JWT (user_id extracted)
2. Frontend sends POST /tasks with title, description
3. Backend validates: title non-empty, length limits
4. Backend inserts: INSERT INTO tasks (user_id, title, description, completed, created_at) VALUES (:user_id, :title, :description, false, NOW())
5. Backend returns created task with ID
6. Frontend displays task in list immediately

**Task Retrieval**:
1. User authenticated via JWT (user_id extracted)
2. Frontend sends GET /tasks
3. Backend queries: SELECT * FROM tasks WHERE user_id = :user_id ORDER BY created_at DESC
4. Backend returns array of user's tasks
5. Frontend displays all tasks

**Task Update**:
1. User authenticated via JWT (user_id extracted)
2. Frontend sends PUT /tasks/:taskId with updated title, description, or completed status
3. Backend fetches task, verifies task.user_id = :user_id (ownership check)
4. If ownership check fails → return 403 Forbidden
5. If ownership check passes → UPDATE tasks SET title = :title, description = :description, completed = :completed, updated_at = NOW() WHERE id = :taskId
6. Backend returns updated task
7. Frontend updates UI

**Task Deletion**:
1. User authenticated via JWT (user_id extracted)
2. Frontend sends DELETE /tasks/:taskId
3. Backend fetches task, verifies task.user_id = :user_id
4. If ownership check fails → return 403 Forbidden
5. If ownership check passes → DELETE FROM tasks WHERE id = :taskId
6. Backend returns 204 No Content or success message
7. Frontend removes task from list

### Query-Level User Isolation Strategy

**Golden Rule**: Every query WHERE clause includes user_id filter

**SELECT Queries**:
- List tasks: `SELECT * FROM tasks WHERE user_id = $1`
- Get single task: `SELECT * FROM tasks WHERE id = $1 AND user_id = $2`

**INSERT Queries**:
- Require user_id in columns: `INSERT INTO tasks (user_id, title, ...) VALUES ($1, $2, ...)`

**UPDATE Queries**:
- Include user_id in WHERE clause: `UPDATE tasks SET ... WHERE id = $1 AND user_id = $2`

**DELETE Queries**:
- Include user_id in WHERE clause: `DELETE FROM tasks WHERE id = $1 AND user_id = $2`

**Benefit**: Even if attacker guesses another user's task ID, query returns zero rows (no error, no data leak)

---

## Frontend Planning (Next.js)

### Authentication Flow Planning

**App Initialization**:
1. Frontend loads; checks for valid JWT in HTTP-only cookie
2. If JWT present and valid → user considered authenticated, store user_id in context/state
3. If JWT missing or invalid → user considered unauthenticated, redirect to login
4. Context/state available to all components for UI decisions (show/hide buttons, conditional rendering)

**Signup Page**:
1. Render form with email and password inputs
2. On submit: send credentials to Better Auth via API call
3. On success: receive JWT, store in cookie (Better Auth handles), redirect to task list
4. On error: display error message (email taken, invalid format, etc.)
5. Link to login page if user already has account

**Login Page**:
1. Render form with email and password inputs
2. On submit: send credentials to Better Auth via API call
3. On success: receive JWT, store in cookie (Better Auth handles), redirect to task list
4. On error: display "Invalid email or password"
5. Link to signup page if user needs account

**Task List Page** (protected):
1. Only accessible if JWT present and valid
2. Fetch tasks from backend via GET /tasks (JWT attached automatically)
3. Display task list with edit/delete/toggle buttons for each task
4. Display button to create new task
5. Display logout button in header

### Protected Route Behavior

**Route Guard Pattern**:
1. Route requires authentication (e.g., /dashboard, /tasks)
2. On route load: check if JWT valid
3. If valid: render page component
4. If invalid/missing: redirect to login page with return URL
5. After login: redirect user back to original URL (optional, but good UX)

**Error Recovery**:
1. If API returns 401 (token expired mid-session), frontend detects
2. Frontend clears JWT from storage
3. Frontend redirects to login page with message: "Your session expired. Please log in again."

### API Client Responsibilities

**Token Attachment**:
- Every API request to private endpoints automatically includes JWT in Authorization header
- HTTP-only cookies handle this automatically (cookie sent on same-origin requests)
- Frontend doesn't manually set Authorization header if using cookie storage (simpler)

**Error Handling**:
- 400 Bad Request: Display field-level errors from backend to user
- 401 Unauthorized: Clear JWT, redirect to login
- 403 Forbidden: Display "You don't have permission to perform this action"
- 404 Not Found: Display "Task not found (may have been deleted)"
- 500 Server Error: Display "Server error. Please try again later."

**Retry Logic**:
- Transient errors (500, network timeout): retry once after short delay
- Auth errors (401): redirect to login immediately
- Validation errors (400): display to user without retry

### State Handling for Tasks & Auth

**Auth State**:
- Store authenticated user ID in context or state management (React Context, Zustand, etc.)
- Store user email for display
- Store JWT expiration time (optional, for proactive refresh warning)
- Clear all auth state on logout

**Task State**:
- List of user's tasks fetched from backend
- Local state for optimistic UI updates (show new task in list immediately before server confirmation)
- Track which task is being edited (modal open/closed)
- Handle loading states: "Loading...", "Saving...", etc.

**UI Feedback**:
- Empty state message when no tasks
- Loading spinner while fetching tasks
- Inline error messages for validation (title required, etc.)
- Success toast notifications: "Task created!", "Task deleted!"
- Disable buttons during API requests (prevent double-click)

---

## Cross-Layer Integration Planning

### Frontend → Backend Auth Handshake

**Signup/Login**:
1. Frontend collects email + password
2. Frontend sends to Better Auth (not backend directly)
3. Better Auth validates, creates user record in backend database
4. Better Auth generates JWT token
5. Better Auth returns JWT to frontend
6. Frontend stores JWT in HTTP-only cookie
7. JWT now attached to all subsequent backend requests

**Token Verification**:
1. Frontend sends: `Authorization: Bearer <JWT>`
2. Backend middleware extracts JWT from Authorization header
3. Backend verifies signature using BETTER_AUTH_SECRET
4. Backend trusts user_id claim in verified JWT
5. Backend attaches user_id to request context
6. Endpoint handler uses user_id for query filters and ownership checks

### Token Attachment Strategy

**Automatic (Cookie-Based)**:
- JWT stored in HTTP-only cookie (Better Auth default)
- Browser automatically sends cookie on same-origin requests
- No manual code to attach token to each request
- Simplest, most secure approach (cookie protected from XSS)

**Manual (Header-Based)** (if cookie storage not feasible):
- Frontend retrieves JWT from local storage
- Frontend manually adds to Authorization header on every request
- More error-prone (must remember on every fetch)
- Less secure (vulnerable to XSS if stored in localStorage)
- Plan to use automatic cookie-based if possible

### Failure & Retry Behavior

**Network Failure**:
- Request timeout or no response from backend
- Frontend shows error: "Unable to connect to server. Please check your connection."
- Offer retry button
- Don't clear JWT (likely temporary network issue)

**Auth Failure** (401 Unauthorized):
- JWT missing or invalid
- Backend returns 401
- Frontend detects 401 status code
- Frontend clears JWT from cookies
- Frontend redirects to login page
- Don't retry (auth failure is permanent until user logs in again)

**Task Operation Failure** (400, 403, 404, 500):
- Validation error (title empty) → display error message
- Cross-user access attempt → display "Permission denied"
- Task not found → display "Task was deleted by you or another session"
- Server error → display "Server error, please try again later" + offer retry button

**Optimistic Updates**:
- User creates task: show task in list immediately, then save to backend
- If backend save fails: remove task from list, show error, allow retry
- User toggles task completion: toggle checkbox immediately, save to backend
- If backend save fails: toggle back, show error

---

## Security & Validation Planning

### Request Validation Checkpoints

**Frontend Validation** (user experience):
1. Email format (basic regex check)
2. Password minimum 8 characters
3. Task title non-empty, max 255 characters
4. Show validation errors inline

**Backend Validation** (security):
1. Email format (strict RFC 5322 validation)
2. Email not already registered (signup)
3. Email exists in database (login)
4. Password hashed comparison (login)
5. Task title non-empty, max 255 characters
6. Task description max 5000 characters
7. User_id matches authenticated user (all task operations)

**Defense in Depth**: Frontend validation for UX, backend validation for security. Never trust client input.

### Authorization Failure Behavior

**Missing JWT** (401):
- Response: `{ error: "Authorization header required" }`
- Log: User attempted access without token

**Invalid JWT** (401):
- Response: `{ error: "Invalid or expired token" }`
- Log: User submitted malformed token (no sensitive details logged)

**Expired JWT** (401):
- Response: `{ error: "Token has expired" }`
- Log: User returned with expired token (expected behavior)

**User ID Mismatch** (403):
- Response: `{ error: "Forbidden" }` (no task details exposed)
- Log: User attempted to access another user's task (security event)
- Don't return "task not found" (could leak task existence)

### Stateless Backend Guarantees

**Principle**: Backend doesn't maintain session state; JWT is the only auth state

**Implications**:
- No session table in database (simpler schema)
- No session timeout tracking (JWT expiration handled by issuance time + exp claim)
- No logout state in database (logout is frontend-side token deletion)
- Multiple servers can authenticate JWT without coordination (no session replication needed)
- Token verification is stateless: only check signature using BETTER_AUTH_SECRET

**Scalability Benefit**: Backend can scale horizontally (multiple instances) without session affinity

---

## Testing & Verification Strategy

### Auth Flow Verification

**Signup Test**:
1. Register new user with valid email and password
2. Verify user account created in database
3. Verify JWT token returned
4. Verify JWT contains correct user_id and email claims
5. Verify token signature valid using BETTER_AUTH_SECRET

**Login Test**:
1. Log in with registered email and correct password
2. Verify JWT token returned
3. Verify JWT contains correct user_id
4. Verify token persists across page refresh
5. Log in with wrong password → verify 401 Unauthorized

**Logout Test**:
1. Log in, verify authenticated
2. Click logout
3. Verify JWT cleared from cookies
4. Attempt to access protected route → verify redirected to login
5. Verify 401 returned from backend if token sent after logout

**Token Expiration Test**:
1. Create token with short expiration (1 minute for testing)
2. Wait for expiration
3. Attempt to use expired token
4. Verify 401 Unauthorized
5. Verify user redirected to login

### Task Ownership Enforcement Checks

**Single-User Isolation**:
1. User A creates task "Task A"
2. User B logs in
3. User B fetches task list
4. Verify User B's list does NOT contain "Task A"
5. Verify User B cannot directly access Task A via URL or API

**Cross-User Access Prevention**:
1. User A creates task with ID 123
2. User B obtains task ID 123 (somehow)
3. User B attempts GET /tasks/123
4. Verify 403 Forbidden (or 404 if not exposing "forbidden" vs "not found")
5. User B attempts PUT /tasks/123 with new title
6. Verify 403 Forbidden

**Ownership After Update**:
1. User A creates task
2. User A updates task title
3. Verify task ownership (user_id) unchanged
4. Verify only User A can see updated task

**Ownership After Deletion**:
1. User A creates task
2. User A deletes task
3. Verify task removed from database
4. Verify other users unaffected

### API Error Consistency Checks

**Status Code Consistency**:
1. All missing auth headers → 401
2. All invalid tokens → 401
3. All ownership violations → 403
4. All validation errors → 400
5. All not-found → 404
6. All server errors → 500

**Error Response Format**:
1. All error responses include error code (e.g., "INVALID_EMAIL")
2. All error responses include human-readable message
3. No sensitive details exposed (no stack traces, database errors)

**Happy Path Consistency**:
1. All create operations return 201 Created with created resource
2. All update operations return 200 OK with updated resource
3. All delete operations return 204 No Content
4. All read operations return 200 OK with resource(s)

---

## Phase II Completion Criteria

### Functional Completeness Conditions

✅ **User Stories Implemented** (8/8):
- Registration (P1): User can sign up with email/password
- Login (P1): User can log in and receive JWT
- Logout (P1): User can log out and lose access
- View Tasks (P1): User sees only their own tasks
- Create Task (P1): User can create new task with title + optional description
- Update Task (P2): User can edit task details
- Delete Task (P2): User can permanently delete task
- Toggle Completion (P1): User can mark task complete/incomplete

✅ **API Endpoints Implemented** (5+ endpoints):
- POST /auth/signup
- POST /auth/login
- POST /auth/logout
- GET /tasks (user-scoped)
- POST /tasks (user-scoped)
- PUT /tasks/{taskId} (with ownership verification)
- DELETE /tasks/{taskId} (with ownership verification)

✅ **All Functional Requirements Met** (FR-001 through FR-031):
- Auth requirements: signup, login, JWT issuance, validation (FR-001 to FR-010)
- Task CRUD: create, read, update, delete with ownership enforcement (FR-011 to FR-022)
- Completion tracking: toggle status, defaults, persistence (FR-023 to FR-025)
- Data persistence: users and tasks stored in database (FR-026 to FR-028)
- API behavior: correct HTTP methods, status codes, JSON responses (FR-029 to FR-031)

### Security Correctness Requirements

✅ **JWT Verification Mandatory**:
- Every protected endpoint verifies JWT signature
- No endpoint trusts user_id from request parameters
- Backend uses BETTER_AUTH_SECRET for all verifications

✅ **User Isolation Enforced**:
- Every task query filters by authenticated user_id
- No SQL injection possible (parameterized queries)
- No task visible to unauthorized users (403 or 404 only)

✅ **Password Security**:
- Passwords hashed (not stored plaintext)
- Password validation on signup (minimum length, strength)
- Password comparison on login (secure comparison, no timing leaks)

✅ **Error Messages Safe**:
- No sensitive details in error responses
- No stack traces, database errors, or user existence leaks
- Generic "Invalid email or password" on login failure

### Readiness for `/sp.tasks`

✅ **Specification Detailed Enough**:
- All user stories have acceptance scenarios
- All requirements testable and unambiguous
- All non-goals explicitly excluded
- Edge cases identified and handled

✅ **Plan Detailed Enough**:
- Architecture clear: frontend, backend, database, auth layers
- API endpoints defined (HTTP method, path, auth requirement)
- Database model specified: users, tasks, user_id ownership
- Query patterns specified: all queries include user_id filter
- Security model specified: JWT verification, ownership checks, error handling

✅ **No Ambiguities for Task Generation**:
- Each user story maps to specific endpoint(s)
- Each endpoint has clear input/output specification
- Each database operation has clear ownership constraint
- Each error case has clear handling

**Next Step**: Run `/sp.tasks` to generate atomic, testable implementation tasks.

---

## Project Structure

### Documentation (this feature)

```text
specs/1-todo-fullstack-web/
├── spec.md              # Feature specification (user stories, requirements)
├── plan.md              # This file (architecture decisions)
├── research.md          # Phase 0 research (technologies, patterns, best practices)
├── data-model.md        # Phase 1 data design (User, Task entities, relationships)
├── quickstart.md        # Phase 1 quickstart guide (setup, running locally)
├── contracts/           # Phase 1 API contracts (OpenAPI/REST specs)
│   ├── auth.md          # Authentication API contract
│   ├── tasks.md         # Task API contract
│   └── errors.md        # Error response formats
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Phase 2 output: atomic implementation tasks (from /sp.tasks)
```

### Source Code (repository root)

```text
# Monorepo structure: frontend + backend separated
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Next.js app router pages
│   ├── hooks/           # Custom React hooks (useAuth, useTasks, etc.)
│   ├── lib/             # Utilities, API client, auth context
│   └── styles/          # Global styles, Tailwind config
├── tests/               # Frontend tests (Jest/Vitest)
├── public/              # Static assets
└── package.json

backend/
├── src/
│   ├── api/             # FastAPI route handlers (auth, tasks)
│   ├── models/          # SQLModel data models (User, Task)
│   ├── services/        # Business logic (task creation, auth)
│   ├── middleware/      # JWT verification middleware
│   ├── database.py      # Database connection, setup
│   ├── config.py        # Configuration (env vars, settings)
│   └── main.py          # FastAPI app entry point
├── tests/               # Backend tests (pytest)
├── alembic/             # Database migrations
└── pyproject.toml       # Poetry dependencies

.env                      # Environment variables (BETTER_AUTH_SECRET, DATABASE_URL, etc.)
.env.example              # Example env file (no secrets)
```

**Structure Decision**: Web application with frontend (Next.js) and backend (FastAPI) isolated. Justified by separation of concerns principle and independent deployment/scaling.

---

**Next Steps**:
1. `/sp.tasks` to generate atomic implementation tasks
2. `/sp.implement` to execute tasks via Claude Code agents
3. Iterative development with continuous verification against spec and plan
