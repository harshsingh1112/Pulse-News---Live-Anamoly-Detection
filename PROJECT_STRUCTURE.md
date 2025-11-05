# Project Structure

## Monorepo Layout

```
pulsewatch/
├── apps/
│   ├── backend/              # FastAPI backend
│   │   ├── src/
│   │   │   ├── main.py       # FastAPI app entry point
│   │   │   ├── api/          # API route handlers
│   │   │   ├── core/         # Config, DB, schemas, logging
│   │   │   ├── ingest/       # RSS/Reddit ingestion
│   │   │   ├── analytics/    # Anomaly detection & aggregation
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   └── utils/        # Utility functions
│   │   ├── config/           # Source configs, topic rules
│   │   ├── tests/            # Unit tests
│   │   ├── scripts/          # Dev scripts (seed data)
│   │   └── requirements.txt
│   └── frontend/             # Next.js frontend
│       ├── app/              # Next.js App Router
│       │   ├── page.tsx      # Dashboard
│       │   ├── anomalies/    # Anomalies page
│       │   ├── feed/         # News feed page
│       │   ├── components/  # React components
│       │   └── lib/          # API client, utils
│       ├── package.json
│       └── ...
├── packages/
│   └── shared/               # Shared TypeScript types
└── docker-compose.yml        # Local development setup
```

## Key Components

### Backend

- **main.py**: FastAPI application with lifespan management, scheduler setup
- **api/**: REST endpoints for news, aggregates, anomalies, sources, SSE stream
- **ingest/**: RSS and Reddit fetchers, topic classifier, pipeline orchestration
- **analytics/**: Time-series bucketing, anomaly detection (MAD/Z-score)
- **models/**: Database models (Article, Count, Anomaly, Source)
- **core/**: Configuration, database session, Pydantic schemas

### Frontend

- **app/page.tsx**: Main dashboard with charts, filters, live feed
- **app/anomalies/page.tsx**: Anomalies table view
- **app/feed/page.tsx**: News article feed with search/filters
- **app/lib/api.ts**: API client functions
- **app/components/**: Reusable UI components

## Data Flow

1. **Ingestion**: Scheduler triggers pipeline every minute
2. **Fetch**: RSS feeds and Reddit fetched in parallel
3. **Classify**: Articles classified into topics (environment/politics/humanity)
4. **Store**: Articles inserted into database (deduplicated by URL)
5. **Aggregate**: Counts bucketed by time (1m, 5m, 60m)
6. **Detect**: Anomalies detected using MAD/Z-score
7. **Publish**: SSE events sent for real-time updates
8. **Serve**: Frontend queries API and displays data

## Configuration

- **sources.yaml**: RSS feeds and Reddit sources to monitor
- **topic_rules.json**: Keyword rules for topic classification
- **.env**: Environment variables (database, Reddit credentials, etc.)

## Testing

- **tests/**: Unit tests for anomaly detection, deduplication, classification
- Run with: `pytest tests/`

## Deployment

- **Backend**: Render (web service + PostgreSQL)
- **Frontend**: Vercel
- See `DEPLOYMENT.md` for detailed instructions

