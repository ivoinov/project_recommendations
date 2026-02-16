# External Integrations

**Analysis Date:** 2026-02-16

## APIs & External Services

**Commerce Data (Magento exports):**
- Magento database export queries - source for product/order data in `magento_get_product_data.sql`, `magento_get_orders_stats.sql`
  - SDK/Client: Not applicable (SQL scripts)
  - Auth: Not applicable (database credentials handled externally)

## Data Storage

**Databases:**
- PostgreSQL 13 (container) - primary app database in `docker-compose.yml`
  - Connection: `DATABASE_URL` in `.env.sample`, `app/config.py`
  - Client: SQLAlchemy in `app/config.py`, `app/repositories/`

**File Storage:**
- Local filesystem only - CSV inputs and model artifacts in `var/` referenced by `celery_app/background_tasks/orders_processing.py`, `celery_app/background_tasks/products_processing.py`, `celery_app/background_tasks/train_similar_model.py`

**Caching:**
- Redis - Celery broker configured in `celery_app/celery_worker.py` and `docker-compose.yml`

## Authentication & Identity

**Auth Provider:**
- Custom JWT - implemented in `app/services/token_service.py` and `app/routers/auth.py`
  - Implementation: `python-jose` JWT encoding in `app/services/token_service.py` with bcrypt hashing in `app/repositories/user_repository.py`

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- Rotating file logger to `var/app.log` in `app/config.py`

## CI/CD & Deployment

**Hosting:**
- Docker containers via `Dockerfile`, `Dockerfile_celery`, `docker-compose.yml`

**CI Pipeline:**
- None detected

## Environment Configuration

**Required env vars:**
- `DATABASE_URL` in `.env.sample`, `app/config.py`
- `SECRET_KEY` in `.env.sample`, `app/config.py`
- `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env.sample`, `app/config.py`
- `CELERY_BROKER_URL` in `.env.sample`, `celery_app/celery_worker.py`

**Secrets location:**
- Loaded from `.env` via dotenv in `app/config.py` (sample provided in `.env.sample`)

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

---

*Integration audit: 2026-02-16*
