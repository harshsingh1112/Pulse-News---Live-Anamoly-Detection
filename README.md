# Breaking News Anomaly Detection System

A full-stack system that aggregates breaking news from environmental, political, and humanity-focused sources (RSS feeds + Reddit) and detects anomalies (spikes) in news volume over time.

## Features

- **Continuous Ingestion**: Automatically fetches news from RSS feeds and Reddit subreddits/users every minute
- **Anomaly Detection**: Uses Median Absolute Deviation (MAD) and Z-score to detect spikes in news volume
- **Real-time Dashboard**: Live feed with time-series charts, spike annotations, and source filtering
- **REST API + SSE**: RESTful endpoints for historical data and Server-Sent Events for live updates
- **Modern Frontend**: Next.js 14 with TailwindCSS, shadcn/ui, and Recharts

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL (or use Docker Compose)

### Local Development

1. **Clone and setup**:
   ```bash
   cd pulsewatch
   cp .env.example .env
   # Edit .env with your Reddit credentials (see below)
   ```

2. **Start with Docker Compose**:
   ```bash
   docker compose up
   ```
   
   This will start:
   - PostgreSQL on `localhost:5432`
   - Backend API on `http://localhost:8000`
   - Frontend on `http://localhost:3000`

3. **Or run manually**:
   ```bash
   # Backend
   cd apps/backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn src.main:app --reload --port 8000
   
   # Frontend (new terminal)
   cd apps/frontend
   npm install
   npm run dev
   ```

### Getting Reddit Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app" or "create app"
3. Choose "script" as the app type
4. Fill in name and redirect URI (can be `http://localhost:8000`)
5. Copy the client ID (under the app name) and secret
6. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_secret_here
   REDDIT_USER_AGENT=pulsewatch/1.0
   ```

### Adding a New Source

1. Edit `apps/backend/config/sources.yaml`:
   ```yaml
   - name: "New Source Name"
     type: rss
     url_or_id: "https://example.com/feed.xml"
     topic: environment  # or politics, humanity
     enabled: true
   ```

2. Restart the backend service

### Seeding Sample Data

To test with synthetic data:
```bash
cd apps/backend
python scripts/dev_seed.py
```

This creates 48 hours of data with controlled spikes for demonstration.

## Project Structure

```
pulsewatch/
├── apps/
│   ├── backend/          # FastAPI backend
│   │   ├── src/
│   │   │   ├── api/      # API routes
│   │   │   ├── core/     # Config, DB, schemas
│   │   │   ├── ingest/   # RSS/Reddit ingestion
│   │   │   ├── analytics/ # Anomaly detection
│   │   │   ├── models/   # SQLAlchemy models
│   │   │   └── utils/    # Utilities
│   │   ├── config/       # Source configs, topic rules
│   │   ├── tests/        # Unit tests
│   │   └── requirements.txt
│   └── frontend/         # Next.js frontend
│       ├── app/          # App Router pages
│       ├── components/   # React components
│       └── lib/          # Utilities
├── packages/
│   └── shared/           # Shared TypeScript types
└── docker-compose.yml
```

## API Endpoints

- `GET /api/news?topic=&source=&since=&limit=` - Latest news items
- `GET /api/aggregate?bucket_size=1m|5m|60m&topic=&since=&source=` - Time-series counts
- `GET /api/anomalies?topic=&since=&bucket_size=` - Detected anomalies
- `GET /api/sources` - List of configured sources
- `GET /api/stream` - SSE stream for live updates
- `GET /healthz` - Health check

## Deployment

### Backend on Render

1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `cd apps/backend && pip install -r requirements.txt`
4. Set start command: `cd apps/backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example`
6. Add PostgreSQL database addon
7. For scheduled jobs, either:
   - Use Render's Cron Jobs feature to hit `/api/admin/run-ingest` every minute
   - Or set `ENABLE_SCHEDULER=true` to run APScheduler inside the web service

### Frontend on Vercel

1. Import your GitHub repository to Vercel
2. Set root directory to `apps/frontend`
3. Add environment variable: `NEXT_PUBLIC_API_BASE=https://your-render-backend.onrender.com`
4. Deploy

## Testing

```bash
# Backend tests
cd apps/backend
pytest

# Frontend tests
cd apps/frontend
npm test
```

## Configuration

See `.env.example` for all configuration options. Key settings:
- `DATABASE_URL`: PostgreSQL connection string
- `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`: Reddit API credentials
- `INGEST_MIN_INTERVAL_SECONDS`: How often to fetch news (default: 60)
- `DEFAULT_TIMEZONE`: Timezone for UI (default: Asia/Kolkata)

## License

MIT

