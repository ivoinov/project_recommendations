# Codebase Structure

**Analysis Date:** 2026-02-16

## Directory Layout

```
project_recommendation/
├── app/                     # FastAPI application code
├── celery_app/              # Celery worker and background tasks
├── alembic/                 # Database migrations
├── tests/                   # Pytest suite
├── var/                     # Local data inputs and logs
├── static/                  # Static assets (favicon)
├── main.py                  # FastAPI entry point
├── requirements.txt         # Python dependencies
├── alembic.ini              # Alembic configuration
├── docker-compose.yml       # Multi-service local deployment
├── Dockerfile               # API container build
└── Dockerfile_celery        # Celery worker container build
```

## Directory Purposes

**app/:**
- Purpose: Core application code (API, domain, persistence, config).
- Contains: Routers, services, repositories, ORM models.
- Key files: `app/config.py`, `app/routers/`, `app/services/`, `app/repositories/`, `app/models/`.

**celery_app/:**
- Purpose: Background task execution and Celery configuration.
- Contains: Worker setup, task dispatcher, task implementations.
- Key files: `celery_app/celery_worker.py`, `celery_app/tasks.py`, `celery_app/background_tasks/`.

**alembic/:**
- Purpose: Database migrations.
- Contains: Alembic env and versioned migrations.
- Key files: `alembic/env.py`, `alembic/versions/`.

**tests/:**
- Purpose: Test suite (model tests).
- Contains: Pytest tests under `tests/models/`.
- Key files: `tests/models/test_product.py`, `tests/models/test_token.py`.

**var/:**
- Purpose: Local runtime data inputs for background jobs and logs.
- Contains: CSV data and log output.
- Key files: `var/orders_data.csv`, `var/products_data.csv`.

## Key File Locations

**Entry Points:**
- `main.py`: FastAPI app creation, router registration, and startup lifecycle.
- `celery_app/celery_worker.py`: Celery app setup and autodiscovery.

**Configuration:**
- `app/config.py`: Settings, logger setup, and DB session generator.
- `alembic.ini`: Alembic CLI configuration.

**Core Logic:**
- `app/routers/`: HTTP endpoints and dependencies.
- `app/services/`: Business logic services.
- `app/repositories/`: SQLAlchemy persistence layer.
- `app/models/`: ORM models and base class.

**Testing:**
- `tests/models/`: Model table and field assertions.

## Naming Conventions

**Files:**
- snake_case module names (e.g., `app/repositories/product_repository.py`, `celery_app/background_tasks/train_similar_model.py`).

**Directories:**
- Lowercase with underscores when needed (e.g., `celery_app/background_tasks/`).

## Where to Add New Code

**New Feature:**
- Primary code: `app/routers/`, `app/services/`, `app/repositories/`
- Tests: `tests/`

**New Component/Module:**
- API endpoints: `app/routers/`
- Business logic: `app/services/`
- Persistence: `app/repositories/`
- Data models: `app/models/`

**Utilities:**
- Shared helpers: `app/` (add a new module and import from routers/services as needed).

## Special Directories

**alembic/versions/:**
- Purpose: Migration scripts.
- Generated: Yes (via Alembic).
- Committed: Yes.

**var/:**
- Purpose: Local input CSVs and log output.
- Generated: Mixed (CSV inputs are external; logs are generated).
- Committed: Yes (current CSV inputs are present).

---

*Structure analysis: 2026-02-16*
