# Vazi

Track how AI recommends your brand. Monitor mentions across ChatGPT, Gemini, Perplexity, and Google AI Overviews.

## What it does

- Monitors how AI systems talk about your brand across multiple providers
- Compares your visibility against up to 5 competitors
- Tracks which sources AI cites when discussing your category
- Analyzes sentiment — are you mentioned positively or negatively?
- Alerts you when something changes

## Architecture

```
dashboard/          React SPA (Vite + Tailwind)
api/                Python backend (FastAPI)
  ├── models/       SQLAlchemy database models
  ├── schemas/      Pydantic request/response schemas
  ├── api/          Route handlers
  ├── engine/       Monitoring engine
  │   └── providers/   AI provider integrations
  ├── worker/       Celery background tasks
  └── services/     Email, Slack, Paystack, Firebase
```

## Self-hosting

### Prerequisites

- Docker and Docker Compose
- API keys for at least one AI provider (OpenAI, Gemini, Perplexity, or SerpAPI)
- Firebase project for authentication

### Quick start

```bash
git clone https://github.com/vazi/vazi.git
cd vazi

# Configure environment
cp api/.env.example api/.env
# Edit api/.env with your API keys

# Start everything
docker compose up -d
```

That's it. Four containers start up:

| Service | Port | Description |
|---------|------|-------------|
| api     | 8000 | FastAPI server |
| worker  | —    | Celery worker + scheduler |
| db      | 5432 | PostgreSQL |
| redis   | 6379 | Task queue broker |

API is at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

### Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### Dashboard (optional for self-hosting)

```bash
cd dashboard
cp .env.example .env
# Edit .env with your Firebase config and API URL

npm install
npm run build
```

Serve the `dist/` folder with any static file server, or use Firebase Hosting.

## Configuration

All configuration is via environment variables. See `api/.env.example` for the full list.

### Required

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase service account JSON |
| `OPENAI_API_KEY` | OpenAI API key (also used for response parsing) |

### AI Providers (add the ones you want)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Monitors ChatGPT responses |
| `GEMINI_API_KEY` | Monitors Gemini responses |
| `PERPLEXITY_API_KEY` | Monitors Perplexity responses |
| `SERP_API_KEY` | Monitors Google AI Overviews |

You need at least one provider configured. The engine skips providers with no API key.

### Optional

| Variable | Description |
|----------|-------------|
| `RESEND_API_KEY` | Email alerts via Resend |

## API

Full API docs are auto-generated at `/docs` when the server is running.

Key endpoints:

```
POST   /api/auth/me              Get current user
GET    /api/projects              List projects
POST   /api/projects              Create project
GET    /api/projects/:id/overview Dashboard overview
GET    /api/projects/:id/mentions Per-query mention breakdown
GET    /api/projects/:id/competitors  Competitor comparison
GET    /api/projects/:id/trends   Visibility over time
GET    /api/projects/:id/sources  Cited sources
POST   /api/admin/run/:id         Trigger a monitoring run
```

## Development

### API

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start Postgres and Redis
docker compose up db redis -d

# Run the API
uvicorn main:app --reload

# Run the worker (separate terminal)
celery -A worker.celery worker --beat --loglevel=info
```

### Dashboard

```bash
cd dashboard
npm install
npm run dev
```

## How monitoring works

1. Celery Beat checks every hour for projects due for a scan (weekly)
2. For each due project, a monitoring task is queued
3. The task sends each tracked query to all configured AI providers concurrently
4. Raw responses are stored, then parsed by GPT-4o-mini to extract brand mentions, sentiment, and cited sources
5. Results are compared to the previous run — if anything changed, alerts are sent

## License

AGPL-3.0 — free to self-host and modify. If you run a modified version as a hosted service, you must open source your changes.
