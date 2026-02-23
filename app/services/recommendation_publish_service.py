import json
from datetime import datetime, timezone

from sqlalchemy import text

from app.cache.recommendation_cache import (
    build_cache_key,
    delete_cache_keys,
    set_cached_candidates,
)
from app.config import settings
from app.models import RecommendationCandidate, RecommendationPublishState
from app.repositories import (
    RecommendationCandidateRepository,
    RecommendationPublishRepository,
    OrderRepository,
    ProductRepository,
)
from app.services.baseline_recommendation_service import build_precompute_candidates
from app.services.db_routing import get_shop_session
from app.services.shop_db import normalize_shop_id, shop_schema_name

PLACEMENT_LIMITS = {"pdp": 20, "cart": 50}
CANDIDATE_TYPES = ("co_purchase", "content_based", "merged")


def publish_shop_candidates(shop_id: str, run_date=None):
    normalized_shop_id = normalize_shop_id(shop_id)
    schema_name = shop_schema_name(normalized_shop_id)
    db = get_shop_session(normalized_shop_id)
    lock_acquired = _try_advisory_lock(db, schema_name)
    if not lock_acquired:
        settings.logger.info(
            "Publish skipped: advisory lock not acquired for shop %s",
            normalized_shop_id,
        )
        db.close()
        return {"status": "skipped", "message": "lock_not_acquired"}

    publish_repo = RecommendationPublishRepository(db)
    product_repo = ProductRepository(db)
    order_repo = OrderRepository(db)
    run_date = run_date or datetime.now(timezone.utc).date()
    placement_versions = {}
    placement_cache_payloads = {}

    try:
        existing_run = publish_repo.get_run_for_date(run_date)
        if existing_run:
            settings.logger.info(
                "Publish skipped: run already exists for shop %s on %s",
                normalized_shop_id,
                run_date,
            )
            return {"status": "skipped", "message": "run_exists"}

        product_count = product_repo.count_products()
        order_count = order_repo.count_orders()
        latest_run = publish_repo.get_latest_run()
        if (
            latest_run
            and latest_run.product_count == product_count
            and latest_run.order_count == order_count
        ):
            publish_repo.create_run(
                run_date,
                status="skipped",
                product_count=product_count,
                order_count=order_count,
                message="No data changes since last run",
            )
            settings.logger.info(
                "Publish skipped: counts unchanged for shop %s",
                normalized_shop_id,
            )
            return {"status": "skipped", "message": "counts_unchanged"}

        seed_skus = product_repo.list_all_skus()
        if not seed_skus:
            publish_repo.create_run(
                run_date,
                status="skipped",
                product_count=product_count,
                order_count=order_count,
                message="No products available for publish",
            )
            settings.logger.info(
                "Publish skipped: no products for shop %s",
                normalized_shop_id,
            )
            return {"status": "skipped", "message": "no_products"}

        for placement, limit in PLACEMENT_LIMITS.items():
            placement_candidates = {}
            placement_payloads = {}
            for seed_sku in seed_skus:
                precomputed = build_precompute_candidates(
                    seed_skus=[seed_sku],
                    order_repository=order_repo,
                    product_repository=product_repo,
                    limit=limit,
                )
                candidate_lists = {
                    "co_purchase": precomputed["co_purchase"],
                    "content_based": precomputed["content_based"],
                    "merged": precomputed["merged"],
                }
                all_candidates = set()
                for candidates in candidate_lists.values():
                    all_candidates.update(candidates)
                popularity = order_repo.get_sku_popularity(list(all_candidates))

                candidates_by_type = {}
                cache_lists = {}
                for candidate_type in CANDIDATE_TYPES:
                    candidates = candidate_lists[candidate_type]
                    scores = _rank_scores(candidates)
                    sorted_candidates = _sort_candidates(
                        candidates, scores, popularity, limit
                    )
                    candidates_by_type[candidate_type] = sorted_candidates
                    cache_lists[candidate_type] = [
                        sku for sku, _score in sorted_candidates
                    ]

                placement_candidates[seed_sku] = candidates_by_type
                placement_payloads[seed_sku] = {
                    "placement": placement,
                    "seed_skus": [seed_sku],
                    "co_purchase": cache_lists["co_purchase"],
                    "content_based": cache_lists["content_based"],
                    "recommendations": cache_lists["merged"],
                }

            state = (
                db.query(RecommendationPublishState)
                .filter(RecommendationPublishState.placement == placement)
                .first()
            )
            previous_version = state.current_version if state else None
            previous_previous_version = state.previous_version if state else None
            new_version = (state.current_version or 0) + 1 if state else 1

            with db.begin():
                for seed_sku, candidates_by_type in placement_candidates.items():
                    _insert_candidates(
                        db,
                        seed_sku,
                        placement,
                        new_version,
                        candidates_by_type,
                    )
                if state:
                    state.current_version = new_version
                    state.previous_version = previous_version
                else:
                    db.add(
                        RecommendationPublishState(
                            placement=placement,
                            current_version=new_version,
                            previous_version=previous_version,
                        )
                    )

            RecommendationCandidateRepository(db).delete_versions_older_than(
                placement, keep_versions=2
            )
            placement_versions[placement] = {
                "new_version": new_version,
                "previous_version": previous_version,
                "previous_previous_version": previous_previous_version,
            }
            placement_cache_payloads[placement] = placement_payloads

        publish_repo.create_run(
            run_date,
            status="success",
            product_count=product_count,
            order_count=order_count,
        )

        _invalidate_and_warm_cache(
            normalized_shop_id, placement_cache_payloads, placement_versions
        )
        settings.logger.info(
            "Publish succeeded for shop %s on %s",
            normalized_shop_id,
            run_date,
        )
        return {
            "status": "success",
            "message": "published",
            "shop_id": normalized_shop_id,
        }
    except Exception as exc:
        db.rollback()
        if placement_versions:
            _rollback_versions(db, placement_versions)
        try:
            publish_repo.create_run(
                run_date,
                status="failed",
                product_count=product_count if "product_count" in locals() else None,
                order_count=order_count if "order_count" in locals() else None,
                message=str(exc),
            )
        except Exception:
            db.rollback()
            settings.logger.exception("Error recording failed publish run")
        settings.logger.exception(
            "Error publishing shop candidates for %s",
            normalized_shop_id,
        )
        return {
            "status": "failed",
            "message": "publish_failed",
            "shop_id": normalized_shop_id,
        }
    finally:
        _release_advisory_lock(db, schema_name)
        db.close()


def _try_advisory_lock(db, schema_name):
    result = db.execute(
        text("SELECT pg_try_advisory_lock(hashtext(:schema_name))"),
        {"schema_name": schema_name},
    ).fetchone()
    return bool(result[0]) if result else False


def _release_advisory_lock(db, schema_name):
    try:
        db.execute(
            text("SELECT pg_advisory_unlock(hashtext(:schema_name))"),
            {"schema_name": schema_name},
        )
    except Exception:
        settings.logger.exception("Error releasing advisory lock")


def _rank_scores(candidates):
    return {
        sku: float(len(candidates) - idx) for idx, sku in enumerate(candidates) if sku
    }


def _sort_candidates(candidates, scores, popularity_map, limit):
    if not candidates:
        return []
    unique_candidates = []
    seen = set()
    for sku in candidates:
        if not sku or sku in seen:
            continue
        seen.add(sku)
        unique_candidates.append(sku)
    scored = [
        (
            sku,
            float(scores.get(sku, 0.0)),
            int(popularity_map.get(sku, 0)),
        )
        for sku in unique_candidates
    ]
    scored.sort(key=lambda item: (-item[1], -item[2], item[0]))
    if limit:
        scored = scored[:limit]
    return [(sku, score) for sku, score, _popularity in scored]


def _insert_candidates(db, seed_sku, placement, version, candidates_by_type):
    for candidate_type, candidates in candidates_by_type.items():
        if not candidates:
            continue
        rows = [
            RecommendationCandidate(
                seed_sku=seed_sku,
                placement=placement,
                candidate_type=candidate_type,
                candidate_sku=candidate_sku,
                score=score,
                version=version,
            )
            for candidate_sku, score in candidates
        ]
        db.add_all(rows)


def _invalidate_and_warm_cache(shop_id, placement_cache_payloads, placement_versions):
    for placement, payloads in placement_cache_payloads.items():
        versions = placement_versions.get(placement, {})
        previous_version = versions.get("previous_version")
        new_version = versions.get("new_version")
        cache_keys = []
        for seed_sku in payloads.keys():
            if previous_version:
                cache_keys.append(
                    build_cache_key(shop_id, placement, seed_sku, previous_version)
                )
            if new_version:
                cache_keys.append(
                    build_cache_key(shop_id, placement, seed_sku, new_version)
                )
        delete_cache_keys(cache_keys)
        for seed_sku, payload in payloads.items():
            if not new_version:
                continue
            cache_key = build_cache_key(shop_id, placement, seed_sku, new_version)
            set_cached_candidates(cache_key, json.dumps(payload))


def _rollback_versions(db, placement_versions):
    try:
        with db.begin():
            for placement, versions in placement_versions.items():
                new_version = versions.get("new_version")
                previous_version = versions.get("previous_version")
                previous_previous_version = versions.get("previous_previous_version")
                if new_version:
                    db.query(RecommendationCandidate).filter(
                        RecommendationCandidate.placement == placement,
                        RecommendationCandidate.version == new_version,
                    ).delete(synchronize_session=False)
                state = (
                    db.query(RecommendationPublishState)
                    .filter(RecommendationPublishState.placement == placement)
                    .first()
                )
                if not state:
                    continue
                if previous_version is None:
                    db.delete(state)
                else:
                    state.current_version = previous_version
                    state.previous_version = previous_previous_version
        settings.logger.info("Rollback completed for failed publish")
    except Exception:
        db.rollback()
        settings.logger.exception("Failed to rollback publish state")
