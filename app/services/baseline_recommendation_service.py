import re
from collections import Counter

from app.config import settings

TOKEN_SPLIT_REGEX = re.compile(r"[,|\s]+")


def build_recommendations(
    seed_skus,
    order_repository,
    product_repository,
    exclude_skus=None,
    limit=20,
):
    try:
        seed_skus = [sku for sku in (seed_skus or []) if sku]
        exclude_skus = exclude_skus or []
        candidate_limit = max(limit * 2, limit)

        co_purchase_raw = build_co_purchase_candidates(
            order_repository, seed_skus, limit=candidate_limit
        )
        content_raw = build_content_based_candidates(
            product_repository, seed_skus, limit=candidate_limit
        )

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
        recommendations = merge_candidates(
            co_purchase,
            content_based,
            seed_skus,
            exclude_skus,
            product_repository,
            limit=limit,
        )

        return {
            "seed_skus": seed_skus,
            "co_purchase": co_purchase,
            "content_based": content_based,
            "recommendations": recommendations,
        }
    except Exception as e:
        settings.logger.error(f"Error building baseline recommendations: {e}")
        raise


def build_co_purchase_candidates(order_repository, seed_skus, limit=50):
    if not seed_skus:
        return []
    rows = order_repository.get_co_purchase_counts(seed_skus, limit=limit)
    return [sku for sku, _count in rows]


def build_content_based_candidates(product_repository, seed_skus, limit=50):
    if not seed_skus:
        return []

    seed_products = product_repository.get_by_skus(seed_skus)
    if not seed_products:
        return []

    categories = [
        product.parent_category for product in seed_products if product.parent_category
    ]
    primary_category = None
    if categories:
        counts = Counter(categories)
        max_count = max(counts.values())
        primary_category = sorted(
            [category for category, count in counts.items() if count == max_count]
        )[0]

    if primary_category:
        candidates = product_repository.get_by_parent_category(primary_category)
    else:
        candidates = product_repository.get_all()

    seed_tokens = set()
    seed_prices = []
    for product in seed_products:
        seed_tokens |= tokenize(product.tags)
        seed_tokens |= tokenize(product.categories_names)
        price_value = (
            product.current_price
            if product.current_price is not None
            else product.price
        )
        if price_value is not None:
            seed_prices.append(float(price_value))

    seed_avg_price = sum(seed_prices) / len(seed_prices) if seed_prices else None

    scored = []
    seed_sku_set = set(seed_skus)
    for product in candidates:
        if product.sku in seed_sku_set:
            continue
        product_tokens = tokenize(product.tags) | tokenize(product.categories_names)
        tag_overlap = len(product_tokens & seed_tokens) if seed_tokens else 0
        price_value = (
            product.current_price
            if product.current_price is not None
            else product.price
        )
        if seed_avg_price is None or price_value is None:
            price_diff = float("inf")
        else:
            price_diff = abs(float(price_value) - seed_avg_price)
        scored.append((product.sku, tag_overlap, price_diff))

    scored.sort(key=lambda item: (-item[1], item[2], item[0]))
    return [sku for sku, _tag_overlap, _price_diff in scored[:limit]]


def merge_candidates(
    co_purchase,
    content_based,
    seed_skus,
    exclude_skus,
    product_repository,
    limit=20,
):
    combined = list(co_purchase) + list(content_based)
    return filter_candidates(
        combined,
        seed_skus,
        exclude_skus,
        product_repository,
        limit=limit,
    )


def filter_candidates(
    candidate_skus,
    seed_skus,
    exclude_skus,
    product_repository,
    limit=None,
):
    if not candidate_skus:
        return []

    exclude_set = set(seed_skus or []) | set(exclude_skus or [])
    seen = set()
    filtered = []
    for sku in candidate_skus:
        if not sku or sku in exclude_set or sku in seen:
            continue
        seen.add(sku)
        filtered.append(sku)

    if not filtered:
        return []

    products = product_repository.get_by_skus(filtered)
    in_stock_skus = {
        product.sku for product in products if product.in_stock is not False
    }
    filtered = [sku for sku in filtered if sku in in_stock_skus]

    if limit:
        return filtered[:limit]
    return filtered


def tokenize(value):
    if not value:
        return set()
    tokens = [token.strip().lower() for token in TOKEN_SPLIT_REGEX.split(value)]
    return {token for token in tokens if token}
