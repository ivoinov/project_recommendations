# Architecture

**Analysis Date:** 2026-02-16

## Pattern Overview

**Overall:** Layered FastAPI service with repository/service separation and background task processing via Celery.

**Key Characteristics:**
- HTTP API endpoints defined in routers under `app/routers/` and mounted in `main.py`.
- Domain logic in service classes under `app/services/` that orchestrate repositories and in-memory model artifacts.
- Persistence access in repository classes under `app/repositories/` using SQLAlchemy models from `app/models/`.

## Layers

**API Layer (Routers):**
- Purpose: Define HTTP endpoints, request validation, auth dependencies, and response models.
- Location: `app/routers/`
- Contains: `APIRouter` modules and Pydantic schemas in `app/routers/schemas.py`.
- Depends on: `app/services/`, `app/repositories/`, `app.config`.
- Used by: FastAPI app in `main.py`.

**Service Layer:**
- Purpose: Encapsulate business logic and orchestration.
- Location: `app/services/`
- Contains: `TokenService`, `ProductService`, `OrderService`.
- Depends on: `app/repositories/`, `app.models`, `app.config`.
- Used by: Routers in `app/routers/*.py`, background tasks in `celery_app/background_tasks/*.py`.

**Repository Layer:**
- Purpose: Encapsulate SQLAlchemy queries and persistence operations.
- Location: `app/repositories/`
- Contains: CRUD logic for `User`, `Token`, `Product`, `Order`.
- Depends on: `app.models`, `app.config`.
- Used by: Services (`app/services/*.py`) and routers (`app/routers/auth.py`, `app/routers/recommendations.py`).

**Domain Models (DB):**
- Purpose: SQLAlchemy ORM models representing tables.
- Location: `app/models/`
- Contains: `User`, `Token`, `Product`, `Order`, and `Base`.
- Depends on: SQLAlchemy, `app.config` (for `Token` default expiration).
- Used by: Repositories and Alembic migrations (`alembic/env.py`).

**Background Processing:**
- Purpose: Asynchronous jobs for CSV ingestion and ML model training.
- Location: `celery_app/` and `celery_app/background_tasks/`
- Contains: Celery worker setup (`celery_app/celery_worker.py`), task dispatcher (`celery_app/tasks.py`), and task implementations.
- Depends on: `app/services/`, `app/repositories/`, `app.config`.
- Used by: API background endpoint in `app/routers/background.py` and Celery worker process.

## Data Flow

**Authentication Flow:**

1. Request hits auth router in `app/routers/auth.py`.
2. Repository access via `UserRepository`/`TokenRepository` in `app/repositories/`.
3. Token creation/validation via `TokenService` in `app/services/token_service.py`.
4. Response serialized via `TokenResponse` in `app/routers/schemas.py`.

**Recommendations Flow (API):**

1. Request hits `app/routers/recommendations.py` with OAuth2 dependency.
2. Token validation via `TokenService.verify_token` using `TokenRepository`.
3. Product lookup via `ProductRepository` and feature data from in-memory settings in `app/config.py`.
4. Similarity computed in router functions; response returned as `ProductRecommendation` from `app/models/productRecommendation.py`.

**Background Job Flow (Celery):**

1. API endpoint in `app/routers/background.py` enqueues `process_task`.
2. Celery worker in `celery_app/celery_worker.py` executes task in `celery_app/tasks.py`.
3. Task dispatches to background task module in `celery_app/background_tasks/`.
4. Task logic reads CSV from `var/` and writes to DB via services/repositories.

**State Management:**
- Request-scoped DB sessions are provided by `db_settings.get_db` in `app/config.py`.
- In-memory ML artifacts are cached in `settings.description_tfidf_matrices` and `settings.price_vectors` in `app/config.py` and (re)loaded in `main.py` lifespan or `app/routers/recommendations.py`.

## Key Abstractions

**Repository Classes:**
- Purpose: Provide persistence access and encapsulate SQLAlchemy usage.
- Examples: `app/repositories/user_repository.py`, `app/repositories/product_repository.py`.
- Pattern: Class-per-aggregate with explicit `create/update/search` methods.

**Service Classes:**
- Purpose: Orchestrate repository actions and business logic.
- Examples: `app/services/token_service.py`, `app/services/product_service.py`.
- Pattern: Thin services with repository dependencies injected per request/task.

**Background Tasks:**
- Purpose: Long-running tasks decoupled from request/response lifecycle.
- Examples: `celery_app/background_tasks/products_processing.py`, `celery_app/background_tasks/train_similar_model.py`.
- Pattern: Function-based tasks invoked from `celery_app/tasks.py` dispatcher.

## Entry Points

**FastAPI App:**
- Location: `main.py`
- Triggers: `uvicorn main:app` (HTTP server)
- Responsibilities: App creation, router registration, CORS, and startup loading of ML artifacts.

**Celery Worker:**
- Location: `celery_app/celery_worker.py`
- Triggers: `celery -A celery_app.celery_worker worker`
- Responsibilities: Broker connection and task discovery.

**Migrations:**
- Location: `alembic/env.py`
- Triggers: Alembic CLI (`alembic upgrade head`)
- Responsibilities: Database migration configuration with `Base.metadata`.

## Error Handling

**Strategy:** Exceptions are caught in repositories/services, logged via `settings.logger`, and either re-raised or return `None`.

**Patterns:**
- Repository-level try/except with `session.rollback()` and `settings.logger.exception` in `app/repositories/*.py`.
- Service-level try/except with `settings.logger.error` in `app/services/*.py`.

## Cross-Cutting Concerns

**Logging:** `settings.logger` configured in `app/config.py` using a rotating file handler to `var/app.log`.
**Validation:** Pydantic request/response models in `app/routers/schemas.py`.
**Authentication:** OAuth2 Bearer token scheme in `app/routers/recommendations.py` and token verification in `app/services/token_service.py`.

---

*Architecture analysis: 2026-02-16*
