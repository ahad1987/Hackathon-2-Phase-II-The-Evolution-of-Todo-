# Deployment Guide: Vercel (Frontend) + Railway (Backend)

This guide covers deploying the Phase II Todo application to production with:
- **Frontend**: Vercel (Next.js)
- **Backend**: Railway or Render (FastAPI)

> **Note**: Vercel's Python support is limited. Railway or Render are better choices for FastAPI deployments.

---

## Part 1: Frontend Deployment (Vercel)

### Prerequisites
- Vercel account: https://vercel.com/signup
- GitHub account with the project pushed
- Node.js 18+ installed locally

### Step 1: Connect GitHub to Vercel

1. Go to https://vercel.com/new
2. Select **"Import Git Repository"**
3. Find and select your GitHub repo: `Hackathon-2-Phase-II-The-Evolution-of-Todo-`
4. Click **"Import"**

### Step 2: Configure Frontend Project

When Vercel shows the import screen:

1. **Select Project Type**: Choose "Next.js"
2. **Root Directory**: Set to `frontend/`
3. **Build Settings**:
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`
4. **Environment Variables**: Add the following
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app  (replace with your backend URL)
   NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.railway.app
   NEXT_PUBLIC_BETTER_AUTH_SECRET=your-32-char-secret-key
   NODE_ENV=production
   ```

5. Click **"Deploy"**

### Step 3: Post-Deployment

After deployment completes:
- Your frontend URL will be: `https://your-project-name.vercel.app`
- Update backend CORS settings to allow this domain
- Test the application at the Vercel URL

---

## Part 2: Backend Deployment

### Option A: Railway (Recommended for FastAPI)

#### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"Start New Project"**

#### Step 2: Connect GitHub Repository

1. Select **"Deploy from GitHub"**
2. Find your repository: `Hackathon-2-Phase-II-The-Evolution-of-Todo-`
3. Select it and click **"Deploy Now"**

#### Step 3: Configure Railway Project

1. Add environment variables in Railway dashboard:
   ```
   PYTHON_VERSION=3.11
   DATABASE_URL=your-postgresql-connection-string
   SECRET_KEY=your-jwt-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

2. Set root directory to `backend/`

3. Click **"Deploy"**

#### Step 4: Get Your Backend URL

- Railway will provide a domain like: `https://backend-prod-xxxx.railway.app`
- Update frontend environment variables with this URL
- Trigger a frontend redeploy on Vercel

---

### Option B: Render (Alternative)

#### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

#### Step 2: Deploy Backend Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - Name: `todo-backend-phase-ii`
   - Runtime: `Python 3.11`
   - Build Command: `pip install -r requirements.txt && poetry install`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
   - Root Directory: `backend/`

4. Add environment variables (same as Railway)

5. Click **"Create Web Service"**

#### Step 3: Get Your Backend URL
- Render provides URL like: `https://todo-backend-phase-ii.onrender.com`

---

## Part 3: Database Setup

### PostgreSQL on Neon (Recommended)

1. Go to https://neon.tech
2. Create a free PostgreSQL project
3. Copy your connection string: `postgresql://user:password@host/database`
4. Add to Railway/Render environment variables as `DATABASE_URL`

### Alternatively: PostgreSQL on Railway
- Railway offers integrated PostgreSQL
- When deploying, add PostgreSQL plugin to your Railway project
- Connection string auto-populated

---

## Part 4: Environment Variables Checklist

### Frontend (Vercel)
- [ ] `NEXT_PUBLIC_API_URL` → Backend URL
- [ ] `NEXT_PUBLIC_BACKEND_URL` → Backend URL
- [ ] `NEXT_PUBLIC_BETTER_AUTH_SECRET` → 32+ char secret
- [ ] `NODE_ENV` → `production`

### Backend (Railway/Render)
- [ ] `DATABASE_URL` → PostgreSQL connection string
- [ ] `SECRET_KEY` → JWT signing key (32+ chars)
- [ ] `ALGORITHM` → `HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` → `30`
- [ ] `ALLOWED_ORIGINS` → Frontend Vercel URL (for CORS)

---

## Part 5: CORS Configuration

Update your FastAPI backend to allow Vercel frontend:

```python
# backend/src/main.py
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://your-project-name.vercel.app",
    "http://localhost:3000",  # For local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Part 6: Verify Deployments

### Frontend Health Check
```bash
# Visit your Vercel URL
https://your-project-name.vercel.app

# Check for any 404 or API errors
# Open browser DevTools → Network tab
```

### Backend Health Check
```bash
# Test API endpoint
curl https://your-backend-url/api/v1/health

# Should return: {"status": "healthy", "timestamp": "..."}
```

### Database Connection Test
```bash
# From your backend logs, verify no database connection errors
# Check Railway/Render logs dashboard
```

---

## Part 7: Troubleshooting

### Frontend won't build
- Check Node version matches `package.json` requirement (>=18.0.0)
- Verify environment variables are set in Vercel dashboard
- Check build logs in Vercel deployment page

### Backend won't start
- Verify `DATABASE_URL` is correct and accessible
- Check Python version is 3.11+
- Review Railway/Render logs for specific errors
- Ensure all required dependencies in `pyproject.toml`

### CORS errors when frontend calls backend
- Verify backend `ALLOWED_ORIGINS` includes your Vercel URL
- Check browser console for specific blocked origin
- Add frontend URL to CORS configuration and redeploy backend

### Database connection timeout
- Verify database is running and accessible
- Check connection string format
- Ensure network/firewall allows Railway/Render to connect
- Test with `psql` or similar tool locally first

---

## Part 8: Continuous Deployment

Both Vercel and Railway/Render support automatic deployments:

### Automatic Deploys
1. **Vercel**: Automatically deploys on push to `main` branch
2. **Railway**: Automatically deploys on GitHub push (configurable)
3. **Render**: Automatically deploys on GitHub push (configurable)

### Manual Deployments
- **Vercel**: Dashboard → Select deployment → Redeploy button
- **Railway**: Dashboard → Manual Deploy option
- **Render**: Dashboard → Manual Deploy option

---

## Part 9: Monitoring & Logs

### Vercel Logs
- Dashboard → Select project → Deployments tab → View logs
- Check build logs, function logs, and runtime errors

### Railway/Render Logs
- Dashboard → Select service → Logs tab
- Real-time log streaming with search/filter

---

## Quick Links

| Service | Link |
|---------|------|
| Vercel Dashboard | https://vercel.com/dashboard |
| Railway Dashboard | https://railway.app/dashboard |
| Render Dashboard | https://dashboard.render.com |
| Neon Database | https://console.neon.tech |
| GitHub Repository | https://github.com/ahad1987/Hackathon-2-Phase-II-The-Evolution-of-Todo- |

---

## Support

For deployment issues:
- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com/deployment/concepts/
