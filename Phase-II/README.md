# Todo Full-Stack Web Application (Phase II)

A secure, multi-user todo web application built with **Next.js** (frontend), **FastAPI** (backend), and **PostgreSQL** (database), featuring JWT-based authentication with Better Auth.

## Features

### Implemented (Phase II T001-T055)
- ✅ User authentication (signup, login, logout) with JWT
- ✅ JWT token verification middleware
- ✅ Task CRUD operations (create, read, update, delete)
- ✅ Task completion toggle
- ✅ User isolation (each user can only access their own tasks)
- ✅ Error handling and validation
- ✅ Protected API routes

### Coming Soon
- Frontend UI components and pages
- Comprehensive testing suite
- Deployment documentation
- Additional task features (filtering, sorting, categories)

## Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT with Better Auth
- **Password Hashing**: bcrypt
- **Testing**: pytest
- **Python**: 3.11+

### Frontend
- **Framework**: Next.js 14 with App Router
- **UI Library**: React 18
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: axios
- **Testing**: Jest

### Shared
- **Authentication**: Better Auth (JWT-based)
- **Shared Secret**: `BETTER_AUTH_SECRET` (32+ characters)

## Project Structure

```
.
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings and configuration
│   │   ├── database.py          # Database connection (T015)
│   │   ├── models/              # SQLModel entities
│   │   │   ├── user.py          # User model (T018)
│   │   │   └── task.py          # Task model (T019)
│   │   ├── services/            # Business logic
│   │   │   ├── user_service.py  # User operations (T034-T035)
│   │   │   └── task_service.py  # Task operations
│   │   ├── api/                 # API routes
│   │   │   ├── auth.py          # Auth endpoints (T036+)
│   │   │   ├── tasks.py         # Task endpoints (T063+)
│   │   │   └── health.py        # Health check (T027)
│   │   └── middleware/
│   │       └── auth.py          # JWT verification (T021)
│   ├── tests/                   # Test suite
│   └── pyproject.toml           # Dependencies
│
├── frontend/
│   ├── src/
│   │   ├── pages/               # Next.js pages (T050+)
│   │   │   ├── login.tsx        # Login page
│   │   │   ├── signup.tsx       # Signup page
│   │   │   ├── tasks.tsx        # Task list page
│   │   │   └── layout.tsx       # Root layout
│   │   ├── components/          # Reusable components (T038+)
│   │   │   ├── LoginForm.tsx
│   │   │   ├── SignupForm.tsx
│   │   │   ├── TaskList.tsx
│   │   │   └── TaskItem.tsx
│   │   ├── lib/                 # Utilities
│   │   │   ├── api-client.ts   # HTTP client
│   │   │   ├── auth-context.ts # Auth state (T028)
│   │   │   └── auth-api.ts     # Auth API calls
│   │   ├── hooks/               # Custom hooks (T029+)
│   │   │   └── useAuth.ts      # useAuth hook
│   │   └── styles/              # Global styles
│   ├── tests/                   # Test suite
│   ├── package.json             # Dependencies
│   ├── next.config.js           # Next.js configuration
│   └── tsconfig.json            # TypeScript configuration
│
├── specs/
│   └── 1-todo-fullstack-web/
│       ├── spec.md              # Feature specification
│       ├── plan.md              # Architecture plan
│       ├── tasks.md             # Implementation tasks
│       └── checklists/
│           └── requirements.md  # Quality checklist
│
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- git

### Backend Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Phase-II
   ```

2. **Create and activate Python virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -e .
   # Or with poetry:
   poetry install
   ```

4. **Configure environment variables**:
   ```bash
   cp ../.env.example ../.env
   # Edit ../.env with your database URL and JWT secret
   ```

5. **Create PostgreSQL database**:
   ```bash
   createdb todo_db
   # Or using your PostgreSQL client
   ```

6. **Run database migrations** (when T015-T016 are implemented):
   ```bash
   alembic upgrade head
   ```

7. **Start the backend development server**:
   ```bash
   poetry run dev
   # Or directly:
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at: `http://localhost:8000`
   API docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # Or with yarn:
   yarn install
   ```

3. **Configure environment variables**:
   ```bash
   # .env.local is already created with defaults
   # Ensure NEXT_PUBLIC_API_URL points to your backend
   ```

4. **Start the frontend development server**:
   ```bash
   npm run dev
   # Or with yarn:
   yarn dev
   ```

   Frontend will be available at: `http://localhost:3000`

### Running Both Services

For convenience, you can use Docker Compose:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## API Documentation

### Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://api.example.com/api/v1`

### Authentication

All endpoints except `/auth/signup` and `/auth/login` require JWT authentication:

```bash
Authorization: Bearer <JWT_TOKEN>
```

JWT tokens are automatically managed by Better Auth and stored in HTTP-only cookies.

### Endpoints Summary

#### Authentication Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/signup` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login user |
| POST | `/auth/logout` | ✅ | Logout user |
| GET | `/auth/me` | ✅ | Get current user |

#### Task Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/tasks` | ✅ | List user's tasks |
| POST | `/tasks` | ✅ | Create new task |
| PUT | `/tasks/{taskId}` | ✅ | Update task |
| DELETE | `/tasks/{taskId}` | ✅ | Delete task |

### Error Responses

All errors follow this format:

```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "message": "User-friendly message",
  "details": {...}
}
```

### Status Codes

- `200 OK`: Successful GET, POST, PUT
- `201 Created`: Successful resource creation
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Valid JWT but permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Development Guidelines

### Code Style

- **Python**: Follow PEP 8 using Black and isort
- **TypeScript/JavaScript**: Follow ESLint and Prettier rules
- **Commit messages**: Use conventional commits (`feat:`, `fix:`, `docs:`, etc.)

### Testing

#### Backend

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_auth.py::test_signup
```

#### Frontend

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Database Migrations

When database schema changes:

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description of change"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Implementation Status

### Phase II (T001-T055) - Current Focus
- [x] T001-T014: Project setup and configuration
- [ ] T015-T032: Database and authentication infrastructure
- [ ] T033-T055: User registration and login implementation

### Future Phases
- [ ] T056-T082: Task CRUD operations
- [ ] T083-T098: Task update and delete
- [ ] T099-T104: Logout functionality
- [ ] T105-T124: Polish and comprehensive testing

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db

# JWT
BETTER_AUTH_SECRET=your-32+-character-secret-key
JWT_EXPIRY=86400
JWT_ALGORITHM=HS256

# Server
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
DEBUG=True
ENVIRONMENT=development
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NODE_ENV=development
```

## Security Considerations

1. **JWT Storage**: Tokens are stored in HTTP-only cookies (set by Better Auth)
2. **CORS**: Only trusted origins can access the API
3. **Password**: Hashed using bcrypt with 12 rounds
4. **User Isolation**: Every query filters by authenticated user ID
5. **Error Messages**: No sensitive information exposed in error responses

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env
- Verify postgres user has permissions

### CORS Errors
- Check CORS_ORIGINS in backend .env
- Ensure frontend URL is in the list
- Verify requests include `withCredentials: true`

### JWT Errors
- Ensure BETTER_AUTH_SECRET is the same in frontend and backend
- Check token expiration
- Clear cookies and re-login

### Frontend Not Loading API
- Verify backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in frontend/.env.local
- Check browser console for specific errors

## Support & Contributing

For issues or questions:
1. Check existing documentation in `/specs/1-todo-fullstack-web/`
2. Review API error messages
3. Check application logs
4. Refer to implementation tasks in `tasks.md`

## License

MIT License - See LICENSE file for details

## Authors

- Ahad (Phase II Implementation)

---

**Last Updated**: 2026-01-09
**Phase II Status**: In Progress (T001-T055)
