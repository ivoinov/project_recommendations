# Codebase Concerns

**Analysis Date:** 2026-02-16

## Tech Debt

**Token expiry handling split across layers:**
- Issue: Token creation sets expiry on the class and model default uses seconds with a static timestamp
- Files: `app/services/token_service.py`, `app/models/token.py`, `app/repositories/token_repository.py`
- Impact: Tokens can expire immediately, never expire, or get inconsistent expiry values
- Fix approach: Set `token.expires_at` per instance, use a callable default in the model, and standardize expiry units

**Session lifecycle managed inside repositories:**
- Issue: Repository methods close the shared DB session in `finally` blocks
- Files: `app/repositories/user_repository.py`, `app/repositories/token_repository.py`, `app/repositories/order_repository.py`, `app/repositories/product_repository.py`
- Impact: Dependency-injected sessions can be closed early, causing downstream failures or hidden transaction boundaries
- Fix approach: Move session close responsibility to the FastAPI dependency in `app/config.py`

**Model artifacts stored without versioning or invalidation:**
- Issue: TF-IDF matrices and KNN model files are written to the working directory with no versioning or recalc strategy
- Files: `celery_app/background_tasks/train_similar_model.py`, `celery_app/background_tasks/train_upsell_model.py`
- Impact: Stale recommendations and hard-to-debug model drift across deployments
- Fix approach: Store artifacts with versioned filenames and persist metadata in a DB table or manifest file

## Known Bugs

**Login token creation returns `None`:**
- Symptoms: On first login, `access_token` is `None` in the response
- Files: `app/routers/auth.py`
- Trigger: User logs in without an existing token record
- Workaround: None implemented

**Order update never persists:**
- Symptoms: Updates do not modify existing rows; new `Order()` is never attached to the session
- Files: `app/repositories/order_repository.py`
- Trigger: Calling `OrderRepository.update`
- Workaround: None implemented

**Aggregated order query closes the session before use:**
- Symptoms: Returned SQLAlchemy query fails when executed due to closed session
- Files: `app/services/order_service.py`
- Trigger: Calling `OrderService.get_order_aggregated_data_query`
- Workaround: Query not used in current flow

## Security Considerations

**Background task endpoint accepts any bearer token:**
- Risk: Any token value grants access to enqueue background jobs
- Files: `app/routers/background.py`
- Current mitigation: OAuth2 scheme present, no verification
- Recommendations: Reuse `verify_token` from `app/routers/recommendations.py` or validate via `TokenService.verify_token`

**Potential secret exposure in repo:**
- Risk: `.env` file is present in the repository and may contain secrets
- Files: `.env`
- Current mitigation: None detected
- Recommendations: Remove secrets from repo and rely on `.env.sample` for template values

**JWT signature not validated on request:**
- Risk: Token validity relies on DB lookup only, no JWT decode/validation
- Files: `app/routers/recommendations.py`, `app/services/token_service.py`, `app/repositories/token_repository.py`
- Current mitigation: Token stored in DB with expiry check
- Recommendations: Decode and validate JWT claims before DB lookup to prevent malformed tokens

## Performance Bottlenecks

**N+1 DB queries in similarity recommendations:**
- Problem: `_get_recommendations` calls `search_by_attribute` for each index
- Files: `app/routers/recommendations.py`
- Cause: Each recommendation triggers a DB query for the same category
- Improvement path: Fetch category products once and index in memory

**Full-table product scan per request:**
- Problem: ProductService builds SKU maps by loading all products on construction
- Files: `app/services/product_service.py`, `app/repositories/product_repository.py`
- Cause: `get_skus_to_ids` executes `get_all()` and builds maps every instance creation
- Improvement path: Cache maps with a TTL or query by SKU when needed

## Fragile Areas

**Stale SKU/id mapping causes incorrect recommendations:**
- Files: `app/services/product_service.py`, `celery_app/background_tasks/train_upsell_model.py`
- Why fragile: Maps are computed once and never refreshed after inserts/updates
- Safe modification: Rebuild maps after bulk updates or query by SKU directly
- Test coverage: No tests for mapping freshness in `tests/`

**Order ingestion relies on cached increment IDs:**
- Files: `app/services/order_service.py`, `celery_app/background_tasks/orders_processing.py`
- Why fragile: `existing_increment_ids` is loaded once and never updated during batch ingestion
- Safe modification: Recompute or query existence per batch and update the in-memory set
- Test coverage: No ingestion tests in `tests/`

**Mutable globals used for ML matrices:**
- Files: `app/config.py`, `celery_app/background_tasks/train_similar_model.py`, `app/routers/recommendations.py`
- Why fragile: Globals are mutated across requests and background tasks without synchronization
- Safe modification: Isolate cache per process with explicit reload and locking
- Test coverage: No concurrency tests in `tests/`

## Scaling Limits

**CSV ingestion loads entire orders file into memory:**
- Current capacity: Entire file must fit into RAM
- Limit: Large `var/orders_data.csv` fails or stalls processing
- Scaling path: Stream rows or chunked reads with `pandas.read_csv(..., chunksize=...)`

**Model training loads full datasets in memory:**
- Current capacity: All products/orders must fit into memory
- Limit: Large product/order tables cause OOM during training
- Scaling path: Sample data, stream features, or train on pre-aggregated tables

## Dependencies at Risk

**Not detected:**
- Risk: No dependency risk flagged in code
- Impact: Not applicable
- Migration plan: Not applicable

## Missing Critical Features

**Authenticated user info endpoint:**
- Problem: Auth service lacks `/me` endpoint for token validation
- Blocks: Client-side user identity retrieval
- Files: `app/routers/auth.py`

**Model recalc/version tracking:**
- Problem: Similarity matrices lack recalc/version metadata
- Blocks: Safe rollbacks and reproducible recommendations
- Files: `celery_app/background_tasks/train_similar_model.py`

## Test Coverage Gaps

**Service and router logic untested:**
- What's not tested: Auth flows, recommendation endpoints, and background tasks
- Files: `app/routers/auth.py`, `app/routers/recommendations.py`, `app/routers/background.py`, `celery_app/tasks.py`
- Risk: Core API behavior can regress unnoticed
- Priority: High

**Repository behavior untested:**
- What's not tested: CRUD operations and session lifecycle
- Files: `app/repositories/product_repository.py`, `app/repositories/order_repository.py`, `app/repositories/token_repository.py`, `app/repositories/user_repository.py`
- Risk: Data persistence bugs remain hidden
- Priority: Medium

---

*Concerns audit: 2026-02-16*
