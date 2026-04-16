# Marketing Service

AI Digital Marketing Automation

## Architecture

Hexagonal (Ports & Adapters) with Python/FastAPI, mirroring the enquiry-service pattern.

```
app/api/          → Inbound adapters (WhatsApp webhook, REST API, cron triggers)
app/core/         → Domain (models, services, outbound ports)
app/infra/        → Outbound adapters (Claude, Gemini, WhatsApp, Instagram, PostgreSQL)
app/config/       → Configuration, database, logging
playbooks/        → Sector-specific marketing playbooks (JSON)
prompts/          → AI system prompts per intelligence layer
```

## Quick Start

```bash
cp .env.example .env
# Fill in API keys in .env

pip install -r requirements.txt

# Create database + schema
psql -c "CREATE DATABASE marketing;"
alembic upgrade head

# Run
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
pytest
```

## Docker

```bash
docker build -t marketing-service .
docker run -p 8000:8000 --env-file .env marketing-service
```

## API Docs

- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/marketing-service/health
# dm-service

