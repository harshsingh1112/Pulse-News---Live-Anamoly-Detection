# Backend API

FastAPI backend for the Breaking News Anomaly Detection System.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (see `.env.example`)

3. Initialize database:
```bash
python -c "from src.core.db import init_db; init_db()"
```

4. Load sources:
```bash
# Sources are automatically loaded from config/sources.yaml on startup
```

## Running

```bash
uvicorn src.main:app --reload
```

API will be available at `http://localhost:8000`

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Testing

```bash
pytest tests/
```

## Seeding Data

```bash
python scripts/dev_seed.py
```

This generates 48 hours of synthetic data with controlled spikes for testing.

