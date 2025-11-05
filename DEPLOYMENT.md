# Deployment Guide

## Backend on Render

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Configure the service**:
   - **Build Command**: `cd apps/backend && pip install -r requirements.txt`
   - **Start Command**: `cd apps/backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

4. **Add PostgreSQL database**:
   - Click "Add Database" → PostgreSQL
   - Note the connection string

5. **Set Environment Variables**:
   ```
   DATABASE_URL=<from database connection string>
   REDDIT_CLIENT_ID=<your_reddit_client_id>
   REDDIT_CLIENT_SECRET=<your_reddit_secret>
   REDDIT_USER_AGENT=pulsewatch/1.0
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ENABLE_SCHEDULER=true
   INGEST_MIN_INTERVAL_SECONDS=60
   DEFAULT_TIMEZONE=Asia/Kolkata
   LOG_LEVEL=INFO
   ```

6. **Deploy** - Render will automatically build and deploy

7. **For scheduled jobs** (optional):
   - Option A: Use Render's Cron Jobs feature to hit `/api/admin/run-ingest` every minute
   - Option B: Keep `ENABLE_SCHEDULER=true` (default) to run APScheduler inside the web service

## Frontend on Vercel

1. **Import your GitHub repository** to Vercel

2. **Configure the project**:
   - **Root Directory**: `apps/frontend`
   - **Framework Preset**: Next.js
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

3. **Set Environment Variables**:
   ```
   NEXT_PUBLIC_API_BASE=https://your-render-backend.onrender.com
   NEXT_PUBLIC_DEFAULT_TZ=Asia/Kolkata
   ```

4. **Deploy** - Vercel will automatically build and deploy

5. **Update CORS** in backend:
   - Update `ALLOWED_ORIGINS` in Render to include your Vercel URL

## Post-Deployment

1. **Initialize the database**:
   - The backend will automatically create tables on first startup
   - Sources will be loaded from `config/sources.yaml`

2. **Verify**:
   - Backend health: `https://your-backend.onrender.com/healthz`
   - Frontend: `https://your-frontend.vercel.app`

3. **Seed test data** (optional):
   - SSH into Render or use Render Shell
   - Run: `python scripts/dev_seed.py`

## Troubleshooting

- **Database connection issues**: Check DATABASE_URL format
- **CORS errors**: Verify ALLOWED_ORIGINS includes your frontend URL
- **No data**: Wait 1-2 minutes for first ingestion cycle, or trigger manually via `/api/admin/run-ingest`
- **Reddit errors**: Verify Reddit credentials are correct

