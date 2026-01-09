# Railway Deployment Guide

Since the Railway CLI requires interactive browser login, here's how to deploy your backend manually through the Railway Dashboard.

## ⚠️ SECURITY ALERT

Your Railway token has been exposed in this deployment attempt. **PLEASE:**

1. Go to https://railway.app/account/tokens
2. Find your token: `7588159c-2dbd-4b91-a164-3af6a709fa70`
3. Click the trash icon to **DELETE IT**
4. Create a new token for future use

---

## 🚀 Manual Deployment Steps

### Step 1: Create Railway Project

1. Go to **https://railway.app/dashboard**
2. Click **"New Project"**
3. Select **"Deploy from GitHub"**
4. Click **"Configure GitHub App"** (if not already done)
5. Select your repository: `Hackathon-2-Phase-II-The-Evolution-of-Todo-`
6. Click **"Deploy"**

### Step 2: Configure Backend Service

Railway should auto-detect your monorepo structure. If not:

1. Click **"New Service"**
2. Select **"GitHub Repo"**
3. Choose your repo
4. In the settings:
   - **Root Directory**: `backend/`
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Start Command**: Leave empty (Railway will detect from Dockerfile)

### Step 3: Add Environment Variables

1. In Railway dashboard, click **"Variables"** tab
2. Click **"New Variable"** and add these KEY → VALUE pairs:

```
DATABASE_URL = postgresql://neondb_owner:npg_0Awe9yqaNmrc@ep-old-sunset-ahewj02h-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

BETTER_AUTH_SECRET = your-very-long-secret-key-at-least-32-characters-for-jwt-signing-phase-ii-todo

JWT_EXPIRY = 86400

JWT_ALGORITHM = HS256

CORS_ORIGINS = https://your-vercel-frontend-url.vercel.app

DEBUG = False

ENVIRONMENT = production

PORT = 8000
```

**Important**: Replace `https://your-vercel-frontend-url.vercel.app` with your actual Vercel URL after deploying frontend.

### Step 4: Deploy

1. Click **"Deploy"** button
2. Watch the logs for build progress
3. Wait for "Deployment successful" message
4. Copy your Railway URL from the dashboard

### Step 5: Get Your Backend URL

Your backend URL will be something like:
```
https://xxx-prod-xxxx.railway.app
```

You'll see it in:
- Railway Dashboard → Your Service → Deployments tab
- In the logs when deployment completes

---

## ✅ Verify Deployment

Test your deployed backend:

```bash
# Replace with your actual Railway URL
curl https://xxx-prod-xxxx.railway.app/api/v1/health

# Should return:
# {"status":"healthy","timestamp":"2024-01-09T..."}
```

---

## 📝 Next Steps

1. **Copy your Railway URL** (e.g., `https://xxx-prod-xxxx.railway.app`)
2. **Update Frontend Environment Variables** in Vercel:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Update:
     ```
     NEXT_PUBLIC_API_URL = https://xxx-prod-xxxx.railway.app
     NEXT_PUBLIC_BACKEND_URL = https://xxx-prod-xxxx.railway.app
     ```
   - Click **"Redeploy"** to apply changes

3. **Test the Full Stack**:
   - Visit your Vercel frontend URL
   - Try logging in or creating a todo
   - Check browser console for API errors

---

## 🆘 Troubleshooting

### Deployment fails with "Port already in use"
- Railway automatically assigns ports
- Remove any hardcoded port `8000` in your code
- Use environment variable `$PORT` instead

### Database connection timeout
- Verify `DATABASE_URL` is correct
- Check Neon database is running: https://console.neon.tech
- Test connection locally first

### CORS errors in browser
- Update `CORS_ORIGINS` in Railway with your Vercel frontend URL
- Make sure it's the full domain: `https://yourapp.vercel.app`
- Redeploy backend after changing CORS

### 502 Bad Gateway
- Check Railway logs for errors
- Verify `uvicorn` is running correctly
- Check environment variables are set
- Verify database connection works

---

## 🔗 Useful Links

- **Railway Dashboard**: https://railway.app/dashboard
- **Your Repo**: https://github.com/ahad1987/Hackathon-2-Phase-II-The-Evolution-of-Todo-
- **Neon Database**: https://console.neon.tech
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Railway Docs**: https://docs.railway.app

---

## 💾 Environment Variables Reference

| Variable | Value | Notes |
|----------|-------|-------|
| DATABASE_URL | PostgreSQL connection string | From Neon |
| BETTER_AUTH_SECRET | 32+ character secret | Use same as frontend |
| JWT_EXPIRY | 86400 | Seconds (24 hours) |
| JWT_ALGORITHM | HS256 | Standard JWT algorithm |
| CORS_ORIGINS | Frontend Vercel URL | Update after deploying frontend |
| DEBUG | False | Never True in production |
| ENVIRONMENT | production | Or "development" |
| PORT | 8000 | Railway auto-assigns, use $PORT |
