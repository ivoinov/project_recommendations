# Technology Stack

**Analysis Date:** 2026-02-16

## Languages

**Primary:**
- Python 3.8 - API, background jobs, and ML tasks in `main.py`, `app/`, `celery_app/` (runtime pinned in `Dockerfile`)

**Secondary:**
- SQL (PostgreSQL 13, Magento export queries) - data access and export scripts in `magento_get_product_data.sql`, `magento_get_orders_stats.sql`, `docker-compose.yml`

## Runtime

**Environment:**
- Python 3.8 (container runtime in `Dockerfile`, `Dockerfile_celery`)

**Package Manager:**
- pip (dependency list in `requirements.txt`)
- Lockfile: missing

## Frameworks

**Core:**
- FastAPI 0.110.0 - HTTP API in `main.py`, `app/routers/`
- SQLAlchemy 2.0.27 - ORM and DB access in `app/models/`, `app/repositories/`, `app/config.py`
- Celery 5.3.6 - background task processing in `celery_app/celery_worker.py`, `celery_app/tasks.py`

**Testing:**
- pytest 8.0.2 - test runner in `tests/` and `app/tests/`
- pytest-asyncio 0.23.5 - async tests in `tests/` (dependency in `requirements.txt`)

**Build/Dev:**
- Uvicorn 0.27.1 - ASGI server in `main.py` and `Dockerfile`
- Alembic (config present) - migrations in `alembic/`, `alembic.ini`
- Black 24.3.0 / Flake8 7.0.0 - formatting/linting dependencies in `requirements.txt`

## Key Dependencies

**Critical:**
- `fastapi` 0.110.0 - API framework used in `main.py`, `app/routers/`
- `sqlalchemy` 2.0.27 - ORM and DB session management in `app/config.py`, `app/models/`
- `pydantic` 2.6.2 / `pydantic-settings` 2.2.1 - settings and schemas in `app/config.py`, `app/routers/schemas.py`
- `celery` 5.3.6 - background job runner in `celery_app/celery_worker.py`, `celery_app/tasks.py`
- `pandas` 2.2.1 / `scikit-learn` 1.5.0 / `numpy` 1.26.4 - ML pipelines in `celery_app/background_tasks/train_similar_model.py`, `celery_app/background_tasks/train_upsell_model.py`
- `python-jose` 3.3.0 / `passlib` 1.7.4 - JWT and password hashing in `app/services/token_service.py`, `app/repositories/user_repository.py`

**Infrastructure:**
- `psycopg2-binary` 2.9.9 - PostgreSQL driver used via SQLAlchemy in `app/config.py`
- `redis` 5.0.1 - Celery broker dependency in `celery_app/celery_worker.py`

## Configuration

**Environment:**
- dotenv-based settings loaded in `app/config.py`
- Sample env vars in `.env.sample` (`DATABASE_URL`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `CELERY_BROKER_URL`)
- Container env placeholders in `Dockerfile`, `Dockerfile_celery`

**Build:**
- Docker images in `Dockerfile`, `Dockerfile_celery`
- Compose orchestration in `docker-compose.yml`
- Alembic config in `alembic.ini`, `alembic/env.py`

## Platform Requirements

**Development:**
- Python 3.8+ with pip (runtime in `Dockerfile`)
- PostgreSQL and Redis locally or via `docker-compose.yml`

**Production:**
- Dockerized deployment with Uvicorn (`Dockerfile`) and Celery worker (`Dockerfile_celery`)
- PostgreSQL 13 and Redis (containers defined in `docker-compose.yml`)

---

*Stack analysis: 2026-02-16*
