# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /code

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

COPY --from=builder /opt/venv /opt/venv
COPY app/ ./app
COPY playbooks/ ./playbooks
COPY prompts/ ./prompts
COPY migrations/ ./migrations
COPY alembic.ini .

ENV PATH="/opt/venv/bin:$PATH"
USER appuser

EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--workers", "4", "--bind", "0.0.0.0:8000", "--timeout", "200"]
