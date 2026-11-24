# =============================================================================
# Stage 1: Compile Frontend SPA (Node 18 Alpine)
# =============================================================================
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci --prefer-offline --no-audit

COPY frontend/ ./
RUN npm run build

# =============================================================================
# Stage 2: Production Python Runtime (Python 3.11 Slim)
# =============================================================================
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production

WORKDIR /app

# Install system dependencies (curl for Docker healthchecks)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged system user for hardened container runtime
RUN groupadd -g 1000 appgroup \
    && useradd -u 1000 -g appgroup -s /bin/bash -m appuser

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY .env.example .env.example
COPY pytest.ini pytest.ini

# Copy compiled frontend assets from Stage 1 into app/static
COPY --from=frontend-builder /app/app/static ./app/static

# Create uploads storage directory and configure unprivileged user ownership
RUN mkdir -p /app/uploads \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Docker liveness health probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Launch ASGI production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
