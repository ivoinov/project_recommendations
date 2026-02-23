import json

from app.cache.recommendation_cache import (
    build_cache_key,
    get_cached_candidates,
    set_cached_candidates,
)
from app.config import settings
from app.repositories import (
    RecommendationCandidateRepository,
    RecommendationPublishRepository,
)
from app.services.baseline_recommendation_service import filter_candidates

PDP_LIMIT = 20
CART_LIMIT = 50
CANDIDATE_TYPES = ("co_purchase", "content_based", "merged")


def get_pdp_recommendations(shop_id, seed_sku, db, product_repository):
    return _get_precomputed_recommendations(
        placement="pdp",
        shop_id=shop_id,
        seed_skus=[seed_sku],
        db=db,
        product_repository=product_repository,
        exclude_skus=[],
        limit=PDP_LIMIT,
    )


def get_cart_recommendations(
    shop_id,
    seed_skus,
    db,
    product_repository,
    exclude_skus=None,
    limit=None,
):
    normalized_limit = min(limit or PDP_LIMIT, CART_LIMIT)
    return _get_precomputed_recommendations(
        placement="cart",
        shop_id=shop_id,
        seed_skus=seed_skus,
        db=db,
        product_repository=product_repository,
        exclude_skus=exclude_skus or [],
        limit=normalized_limit,
    )


def _get_precomputed_recommendations(
    placement,
    shop_id,
    seed_skus,
    db,
    product_repository,
    exclude_skus,
    limit,
):
    try:
        seed_skus = [sku for sku in (seed_skus or []) if sku]
        if not seed_skus:
            return _empty_response(placement, seed_skus)

        publish_repo = RecommendationPublishRepository(db)
        version = _get_current_version(publish_repo, placement)
        if not version:
            return _empty_response(placement, seed_skus)

        candidate_repo = RecommendationCandidateRepository(db)
        seed_candidates = []
        for seed_sku in seed_skus:
            seed_candidates.append(
                _get_seed_candidates(
                    shop_id, placement, seed_sku, version, candidate_repo
                )
            )

        if len(seed_skus) == 1:
            co_purchase_raw = _skus_from_scored(
                seed_candidates[0].get("co_purchase", [])
            )
            content_raw = _skus_from_scored(seed_candidates[0].get("content_based", []))
            merged_raw = _skus_from_scored(seed_candidates[0].get("merged", []))
        else:
            co_purchase_raw = _merge_scored_candidates(
                seed_candidates, "co_purchase", limit
            )
            content_raw = _merge_scored_candidates(
                seed_candidates, "content_based", limit
            )
            merged_raw = _merge_scored_candidates(seed_candidates, "merged", limit)

        candidate_limit = max(limit * 2, limit)
        co_purchase = filter_candidates(
            co_purchase_raw,
            seed_skus,
            exclude_skus,
            product_repository,
            limit=candidate_limit,
        )
        content_based = filter_candidates(
            content_raw,
            seed_skus,
            exclude_skus,
            product_repository,
            limit=candidate_limit,
        )
        recommendations = filter_candidates(
            merged_raw,
            seed_skus,
            exclude_skus,
            product_repository,
            limit=limit,
        )

        if not co_purchase:
            co_purchase = list(recommendations)
        if not content_based:
            content_based = list(recommendations)

        return {
            "placement": placement,
            "seed_skus": seed_skus,
            "co_purchase": co_purchase,
            "content_based": content_based,
            "recommendations": recommendations,
        }
    except Exception as exc:
        settings.logger.exception(
            "Error serving precomputed recommendations for %s: %s", placement, exc
        )
        raise


def _get_current_version(publish_repo, placement):
    state = publish_repo.get_state(placement)
    if not state:
        return None
    return state.current_version


def _get_seed_candidates(shop_id, placement, seed_sku, version, candidate_repo):
    cache_key = build_cache_key(shop_id, placement, seed_sku, version)
    cached = get_cached_candidates(cache_key)
    if cached:
        parsed = _parse_cache_payload(cached)
        if parsed is not None:
            return parsed

    candidates = {}
    for candidate_type in CANDIDATE_TYPES:
        rows = candidate_repo.get_candidates(
            seed_sku=seed_sku,
            placement=placement,
            candidate_type=candidate_type,
            version=version,
        )
        candidates[candidate_type] = [
            (row.candidate_sku, float(row.score)) for row in rows if row.candidate_sku
        ]

    payload = {
        "placement": placement,
        "seed_skus": [seed_sku],
        "co_purchase": _skus_from_scored(candidates.get("co_purchase", [])),
        "content_based": _skus_from_scored(candidates.get("content_based", [])),
        "recommendations": _skus_from_scored(candidates.get("merged", [])),
    }
    set_cached_candidates(cache_key, json.dumps(payload))
    return candidates


def _parse_cache_payload(cached_payload):
    try:
        payload = json.loads(cached_payload)
    except (TypeError, ValueError):
        return None

    if not isinstance(payload, dict):
        return None

    co_purchase = payload.get("co_purchase") or []
    content_based = payload.get("content_based") or []
    merged = payload.get("recommendations") or payload.get("merged") or []

    return {
        "co_purchase": _scores_from_ranked_list(co_purchase),
        "content_based": _scores_from_ranked_list(content_based),
        "merged": _scores_from_ranked_list(merged),
    }


def _scores_from_ranked_list(candidates):
    scored = []
    if not candidates:
        return scored
    count = len(candidates)
    for idx, sku in enumerate(candidates):
        if not sku:
            continue
        scored.append((sku, float(count - idx)))
    return scored


def _skus_from_scored(scored_candidates):
    if not scored_candidates:
        return []
    sorted_candidates = sorted(
        scored_candidates, key=lambda item: (-float(item[1]), item[0])
    )
    return [sku for sku, _score in sorted_candidates]


def _merge_scored_candidates(seed_candidates, candidate_type, limit):
    combined_scores = {}
    for seed_candidate in seed_candidates:
        for sku, score in seed_candidate.get(candidate_type, []):
            if not sku:
                continue
            existing = combined_scores.get(sku)
            if existing is None or score > existing:
                combined_scores[sku] = score
    sorted_items = sorted(
        combined_scores.items(), key=lambda item: (-float(item[1]), item[0])
    )
    if limit:
        sorted_items = sorted_items[:limit]
    return [sku for sku, _score in sorted_items]


def _empty_response(placement, seed_skus):
    return {
        "placement": placement,
        "seed_skus": seed_skus,
        "co_purchase": [],
        "content_based": [],
        "recommendations": [],
    }
