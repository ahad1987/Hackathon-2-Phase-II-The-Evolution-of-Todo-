# Quick Start Guide - Todo Application

## Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL (via Neon)
- Internet connection

## Step 1: Start the Backend

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

✅ Backend is ready at: http://localhost:8000
✅ API Docs available at: http://localhost:8000/docs

## Step 2: Start the Frontend

Open a new terminal (keep backend running):

```bash
cd frontend
npm install  # Only needed first time
npm run dev
```

**Expected Output**:
```
Ready in 2.5s
```

✅ Frontend is ready at: http://localhost:3000

## Step 3: Use the Application

### 1. Sign Up
- Go to http://localhost:3000
- Click "Sign Up"
- Enter email and password
- Click "Create Account"
- ✅ You'll be logged in automatically

### 2. Create Your First Task
- Click "+ Add Task" button
- Enter task title (required)
- Enter description (optional)
- Click "Create Task"
- ✅ Task appears in list below

### 3. Manage Tasks
- **Check complete**: Click the checkbox
- **Edit**: Click "Edit" button, modify, click "Save"
- **Delete**: Click "Delete" button, confirm
- **View all**: Tasks are sorted by newest first

### 4. Logout
- Click "Logout" button in top right
- ✅ Redirected to login page

## Common Tasks

### View API Documentation
```
http://localhost:8000/docs
```
Shows all endpoints, request/response models, and test interface.

### Test API via curl
```bash
# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"SecurePass123"}'

# Get token from response above, then create task:
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"title":"My Task","description":"Do something"}'
```

### Check Database Connection
```bash
cd backend
python -c "
import asyncio
from src.database import engine
from src.models.user import User
from src.models.task import Task

async def check():
    async with engine.begin() as conn:
        tables = await conn.run_sync(lambda sync_conn: sync_conn.inspect().get_table_names())
        print('Tables:', tables)

asyncio.run(check())
"
```

## Troubleshooting

### Port Already in Use
If port 8000 or 3000 is in use:
```bash
# Kill existing processes or use different ports:
python -m uvicorn src.main:app --port 8001
npm run dev -- -p 3001
```
Update `NEXT_PUBLIC_API_URL=http://localhost:8001` in frontend.

### Database Connection Error
- Check `.env` file has valid DATABASE_URL
- Test connection: `psql $DATABASE_URL`
- Ensure Neon database is active (not sleeping)

### Node Modules Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Next.js Cache Issues
```bash
cd frontend
rm -rf .next
npm run dev
```

## Features Included

### Authentication
✅ Sign up with email/password
✅ Login with existing account
✅ Logout (clears session)
✅ Protected routes (redirects to login)
✅ JWT token-based auth (24hr expiry)

### Todo Management
✅ Create tasks with title and description
✅ View all your tasks
✅ Edit task details
✅ Mark tasks as complete/incomplete
✅ Delete tasks
✅ Task stats (total, completed, pending)

### Security
✅ Passwords hashed with bcrypt
✅ JWT tokens signed and verified
✅ User isolation (see only your tasks)
✅ Input validation on both sides
✅ CORS protection

### User Experience
✅ Responsive design (mobile-friendly)
✅ Real-time validation feedback
✅ Loading states
✅ Error messages
✅ Timestamps for tasks

## File Structure Reference

```
Phase-II/
├── backend/              # FastAPI backend
│   ├── src/
│   │   ├── main.py       # App entry
│   │   ├── api/          # Endpoints (auth, tasks)
│   │   ├── services/     # Business logic
│   │   ├── models/       # Data models
│   │   └── middleware/   # JWT auth
│   ├── requirements.txt  # Python packages
│   └── .env             # Config (DATABASE_URL, JWT_SECRET)
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/         # Pages (login, tasks)
│   │   ├── components/  # React components
│   │   └── lib/         # Utilities (API client, auth)
│   ├── package.json     # JS packages
│   └── .env.local       # Config
└── VERIFICATION_REPORT.md  # Complete documentation
```

## Next Steps

1. **Explore the API**: Open http://localhost:8000/docs
2. **Read Full Docs**: Check `VERIFICATION_REPORT.md` for details
3. **Run Tests**: `python test_application.py` (after fixing port)
4. **Deploy**: Follow deployment guides for Vercel (frontend) and Railway (backend)

## Support

- Backend issues: Check `src/main.py` logs
- Frontend issues: Check browser console (F12)
- Database issues: Test with psql directly
- API issues: Use http://localhost:8000/docs to test endpoints

---

**You're all set! Start coding.**
