# Better Auth Integration - Testing Checklist

## Pre-Integration Verification ✅

- [x] No breaking changes made to existing code
- [x] New files only added (not modified):
  - `backend/src/services/better_auth_compat.py` - New compatibility layer
  - `backend/src/api/auth.py` - Added ONE new endpoint (POST /refresh)
- [x] Task CRUD endpoints unchanged
- [x] Database schema unchanged
- [x] Frontend unchanged (no modifications)

## Full Test Suite (Before Using Better Auth Migration)

### Setup Phase
```bash
# 1. Start fresh from project root
cd /path/to/Phase-II

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt  # or poetry install
cd ..

# 3. Install frontend dependencies
cd frontend
npm install
cd ..
```

### Backend Tests

#### Test 1: Backend Starts Without Errors
```bash
cd backend
python -m uvicorn src.main:app --reload
# Expected: Application startup complete
# Verify: curl http://localhost:8000/health → 200 OK
```

#### Test 2: Signup Still Works (Backward Compatibility)
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@example.com","password":"Test123456"}'

# Expected Response (200 Created):
# {
#   "user": {
#     "id": "<uuid>",
#     "email": "user1@example.com",
#     "created_at": "2026-01-09T..."
#   },
#   "token": "eyJhbGc..."
# }
```

#### Test 3: Login Still Works (Backward Compatibility)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@example.com","password":"Test123456"}'

# Expected Response (200 OK):
# {
#   "user": {...},
#   "token": "eyJhbGc..."
# }

# Save token for next tests
TOKEN="<token_from_response>"
```

#### Test 4: Task List Works (Backward Compatibility)
```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"

# Expected Response (200 OK):
# { "tasks": [] } or list of tasks
```

#### Test 5: Add Task Works (Backward Compatibility)
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task","description":"Testing"}'

# Expected Response (201 Created or 200 OK):
# Task created successfully
```

#### Test 6: NEW - Token Refresh Works (New Feature)
```bash
# First, get a refresh token (need to modify signup to return it)
# For now, this test will work after phase 2

curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'

# Expected Response (200 OK):
# {
#   "token": "eyJhbGc...",
#   "message": "Token refreshed successfully"
# }
```

### Frontend Tests

#### Test 7: Frontend Builds Without Errors
```bash
cd frontend
npm run build

# Expected: Build succeeds, no errors
```

#### Test 8: Frontend Starts Without Errors
```bash
cd frontend
npm run dev

# Expected: Application starts, listen on port 3000
# Verify: Open http://localhost:3000 in browser
```

#### Test 9: Signup Form Still Works
1. Navigate to http://localhost:3000/signup
2. Enter email: `user2@example.com`
3. Enter password: `Test123456`
4. Click "Sign Up"

**Expected**:
- ✅ Account created
- ✅ Redirected to /tasks page
- ✅ See "My Tasks" heading
- ✅ No error messages

#### Test 10: Login Form Still Works
1. Logout if logged in
2. Navigate to http://localhost:3000/login
3. Enter email: `user1@example.com`
4. Enter password: `Test123456`
5. Click "Log In"

**Expected**:
- ✅ Logged in successfully
- ✅ Redirected to /tasks page
- ✅ See existing tasks (or empty task list)
- ✅ No error messages

#### Test 11: Task Operations Still Work
1. Logged in at /tasks page
2. Click "+ Add Task"
3. Enter "Test Task" as title
4. Click "Create Task"

**Expected**:
- ✅ Task appears in list
- ✅ "Total Tasks" count increases
- ✅ "Pending" count increases
- ✅ No errors

#### Test 12: Mark Complete Still Works
1. Click "Mark Complete" button on a task
2. Verify button changes to "Mark Incomplete"

**Expected**:
- ✅ Task has strikethrough text
- ✅ "Completed" count increases
- ✅ "Pending" count decreases
- ✅ Task background changes

#### Test 13: Logout Still Works
1. Click "Logout" button
2. Should redirect to login page
3. Try to navigate back to /tasks
4. Should redirect to /login

**Expected**:
- ✅ Logged out successfully
- ✅ Protected routes now redirect to login
- ✅ Session cleared

### Integration Tests

#### Test 14: Full User Journey
```
1. Signup new account (test3@example.com)
   ✅ Account created
2. Auto-logged in
   ✅ Redirect to /tasks
3. Add task
   ✅ Task appears
4. Mark complete
   ✅ Status updates
5. Refresh page
   ✅ Task still visible, still marked complete
6. Logout
   ✅ Redirected to login
7. Login with same account
   ✅ Task still exists with same status
8. Delete task
   ✅ Task removed
9. Logout
   ✅ Session cleared
```

#### Test 15: Multiple Users
```
1. User A signup and add "Task A"
2. User B signup and add "Task B"
3. User A login
   ✅ Only sees "Task A"
4. User B login
   ✅ Only sees "Task B"
5. Each user can only see their own tasks
   ✅ User isolation maintained
```

### Regression Tests (All Must Pass)

- [ ] No JavaScript errors in browser console
- [ ] No Python errors in backend terminal
- [ ] All 15 tests above pass
- [ ] Database still has correct data
- [ ] Passwords still hashed (not visible in DB)
- [ ] JWT tokens still signed correctly
- [ ] Task ownership properly enforced
- [ ] All cookies set correctly
- [ ] No CORS errors
- [ ] No 404 errors on valid routes
- [ ] All status codes correct (200, 201, 400, 401, 500 as appropriate)

## Rollback Procedure (If Any Test Fails)

```bash
# If any test fails, run this to undo changes:
cd /path/to/Phase-II

# Undo only auth.py changes (keep better_auth_compat.py for reference)
git checkout -- backend/src/api/auth.py

# If major issue, full rollback:
git reset --hard HEAD~1

# Reinstall dependencies
cd backend && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..

# Restart services and test again
```

## Safety Verification

**Changes Made**:
1. ✅ Added new file: `backend/src/services/better_auth_compat.py`
2. ✅ Modified `backend/src/api/auth.py` - Added ONE new endpoint
3. ✅ No other files modified
4. ✅ No database changes
5. ✅ No frontend changes

**Risk Assessment**: 🟢 **VERY LOW**
- New code is isolated (compatibility layer)
- Existing endpoints unchanged
- All tests should pass without modification
- Easy to rollback if needed

## Success Criteria

✅ **All tests above pass**
✅ **No existing functionality broken**
✅ **New refresh endpoint works**
✅ **Application ready for Better Auth migration (when desired)**

---

**Run These Tests Before Considering Better Auth Integration Complete**
