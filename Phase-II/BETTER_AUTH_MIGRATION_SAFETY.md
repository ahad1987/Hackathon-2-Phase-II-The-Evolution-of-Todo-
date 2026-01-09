# Better Auth Migration - Safety & Rollback Plan

## Pre-Migration State (Snapshot)
- **Date**: 2026-01-09
- **Branch**: main
- **Status**: ✅ All features working (signup, login, tasks, counting)
- **Auth Type**: Custom JWT
- **Database**: PostgreSQL (Neon)

## Safety Checkpoints

### Checkpoint 1: Before Installing Dependencies
```bash
git status
git log --oneline -5
npm list (frontend)
pip freeze (backend)
```

### Checkpoint 2: Before Frontend Changes
```bash
npm run build  # Must succeed
npm run dev    # Must start without errors
```

### Checkpoint 3: Before Backend Changes
```bash
python -m pytest  # All tests pass
uvicorn src.main:app --reload  # Must start
```

### Checkpoint 4: After Better Auth Setup
```bash
npm run dev  # Frontend must load
uvicorn src.main:app --reload  # Backend must start
curl http://localhost:8000/health  # Must return 200
```

## Rollback Strategy

If any step breaks functionality:

### Quick Rollback (Within Same Session)
```bash
# Undo last change
git checkout -- <file>
# Reinstall original deps
npm install (or pip install)
# Restart servers
```

### Full Rollback (If Major Break)
```bash
# Revert to last known good state
git reset --hard HEAD

# Or revert specific commit
git revert <commit-hash>

# Reinstall original dependencies
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# Restart both services
```

## Testing Protocol

### Auth Tests (Each Step)
- [ ] Signup creates account
- [ ] Login works with correct credentials
- [ ] Login fails with wrong credentials
- [ ] Logout clears session
- [ ] Protected routes redirect to login
- [ ] JWT token in cookies

### Task Tests (Each Step)
- [ ] Add task works
- [ ] Task count updates
- [ ] Mark complete works
- [ ] Task list shows correct count
- [ ] Delete task works
- [ ] Completed/Pending counts correct

### Integration Tests
- [ ] Signup → Auto login → See tasks
- [ ] Login → Add task → Logout → Login → See task
- [ ] Multiple users don't see each other's tasks
- [ ] Page refresh keeps session

## Current Files (For Rollback Reference)

### Frontend Auth Files
- `frontend/src/lib/auth-context.tsx` - Current auth context
- `frontend/src/lib/api-client.ts` - Token management
- `frontend/src/components/LoginForm.tsx` - Login component
- `frontend/src/components/SignupForm.tsx` - Signup component

### Backend Auth Files
- `backend/src/api/auth.py` - Auth endpoints
- `backend/src/middleware/auth.py` - JWT verification
- `backend/src/services/user_service.py` - User operations
- `backend/src/models/user.py` - User model

## Breaking Points to Watch

❌ **DO NOT CHANGE**:
- Task CRUD endpoints (`GET /tasks`, `POST /tasks`, etc.)
- Database schema (users, tasks tables)
- User isolation logic
- API response formats
- HTTP status codes

✅ **OK TO CHANGE**:
- Auth endpoint implementation (internal only)
- JWT generation mechanism
- JWT verification process
- Auth context implementation
- Session handling

## Environmental Safeguards

### Variables to Preserve
```
BETTER_AUTH_SECRET=<preserved>
DATABASE_URL=<unchanged>
API_BASE_URL=<unchanged>
```

### Config Files Not Modified
```
docker-compose.yml
.env.example
nginx.conf (if exists)
```

## Pre-Migration Checks

Run this before starting:
```bash
# Check all tests pass
cd backend && python -m pytest && cd ..
npm run build --prefix frontend

# Check servers start
pkill -f "uvicorn\|next dev"
cd backend && python -m uvicorn src.main:app --reload &
cd ../frontend && npm run dev &
sleep 5

# Check endpoints respond
curl http://localhost:8000/health
curl http://localhost:3000

# Stop servers
pkill -f "uvicorn\|next dev"

echo "✅ All pre-migration checks passed"
```

## Emergency Contacts

If something breaks:
1. Check this file for rollback steps
2. Review the checkpoint tests
3. Run git diff to see what changed
4. Use git revert to undo commits
5. Reinstall dependencies fresh

---

**Remember**: It's better to proceed slowly and verify at each step than to break everything and spend hours debugging.

