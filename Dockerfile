# Production Multi-Stage Dockerfile for AI Customer Support Resolution Agent
FROM python:3.11-slim as backend

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY knowledge_base/ ./knowledge_base/
COPY scripts/ ./scripts/
COPY evaluation/ ./evaluation/

ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql+psycopg2://support_user:support_password@postgres:5432/support_db

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
