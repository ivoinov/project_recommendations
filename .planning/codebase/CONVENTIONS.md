# Coding Conventions

**Analysis Date:** 2026-02-16

## Naming Patterns

**Files:**
- Use `snake_case` for Python modules (e.g., `app/services/product_service.py`, `app/repositories/token_repository.py`).

**Functions:**
- Use `snake_case` for functions and methods (e.g., `create_or_update` in `app/services/order_service.py`).

**Variables:**
- Use `snake_case` for locals and instance attributes (e.g., `existing_increment_ids` in `app/services/order_service.py`).
- Use `UPPER_SNAKE_CASE` for module constants (e.g., `TRAIN_TEST_SPLIT_RATIO` in `celery_app/background_tasks/train_upsell_model.py`).

**Types:**
- Use `PascalCase` for classes (e.g., `ProductService` in `app/services/product_service.py`, `UserSignUp` in `app/routers/schemas.py`).

## Code Style

**Formatting:**
- Tool used: `black` (dependency in `requirements.txt`).
- Key settings: Not detected (no config file found).

**Linting:**
- Tool used: `flake8` (dependency in `requirements.txt`).
- Key rules: Not detected (no config file found).

## Import Organization

**Order:**
1. Standard library imports (e.g., `datetime` in `app/routers/auth.py`).
2. Third-party imports (e.g., `fastapi` in `app/routers/auth.py`).
3. Local application imports (e.g., `app.repositories` in `app/routers/auth.py`).

**Path Aliases:**
- Not detected (imports use `app.*` package paths).

## Error Handling

**Patterns:**
- In repository methods, wrap DB operations in `try/except`, rollback on failure, log, then re-raise (e.g., `app/repositories/product_repository.py`, `app/repositories/token_repository.py`).
- In service methods, catch exceptions, log via `settings.logger`, and either re-raise or return `None` depending on the method contract (e.g., `app/services/order_service.py`, `app/services/product_service.py`).

## Logging

**Framework:** `logging` via `settings.logger` configured in `app/config.py`.

**Patterns:**
- Use `settings.logger.error`/`exception` in repositories and services (e.g., `app/repositories/user_repository.py`, `app/services/order_service.py`).
- Background task scripts sometimes use `print` for per-row failures; use `settings.logger` for persistent application logs (e.g., `celery_app/background_tasks/products_processing.py`).

## Comments

**When to Comment:**
- Use inline comments for procedural steps or TODOs in long-running tasks (e.g., `celery_app/background_tasks/train_similar_model.py`).

**JSDoc/TSDoc:**
- Not applicable (Python codebase).

## Function Design

**Size:**
- Small to medium functions; background tasks can be longer but remain procedural (e.g., `celery_app/background_tasks/orders_processing.py`).

**Parameters:**
- Prefer explicit parameters and basic types; use `dict` for data payloads where shapes are dynamic (e.g., `create_or_update_product` in `app/services/product_service.py`).

**Return Values:**
- Repository methods return ORM instances or lists; service methods may return `None` on failure after logging (e.g., `app/services/product_service.py`).

## Module Design

**Exports:**
- Use package `__init__.py` files as barrel exports for domain objects (e.g., `app/models/__init__.py`, `app/services/__init__.py`, `app/repositories/__init__.py`).

**Barrel Files:**
- Present and used for imports like `from app.services import TokenService` (e.g., `app/routers/auth.py`).

---

*Convention analysis: 2026-02-16*
