from datetime import date

from sqlalchemy import text

from app.models import (
    RecommendationCandidate,
    RecommendationPublishRun,
    RecommendationPublishState,
)
from app.services.shop_db import ensure_shop_schema


def seed_publish_state(db, shop_id="test"):
    ensure_shop_schema(db, shop_id)
    db.execute(text("DELETE FROM recommendation_publish_runs"))
    db.execute(text("DELETE FROM recommendation_publish_state"))
    db.add_all(
        [
            RecommendationPublishState(
                placement="pdp", current_version=2, previous_version=1
            ),
            RecommendationPublishState(
                placement="cart", current_version=3, previous_version=2
            ),
        ]
    )
    db.add(
        RecommendationPublishRun(
            run_date=date(2026, 2, 23),
            status="success",
            product_count=10,
            order_count=5,
            message="Published",
        )
    )
    db.commit()
    db.execute(text("SET search_path TO public"))


def seed_candidates_for_rollback(db, shop_id="test"):
    ensure_shop_schema(db, shop_id)
    db.execute(text("DELETE FROM recommendation_candidates"))
    db.execute(text("DELETE FROM recommendation_publish_state"))
    db.add_all(
        [
            RecommendationPublishState(
                placement="pdp", current_version=2, previous_version=1
            ),
            RecommendationCandidate(
                seed_sku="sku-1",
                placement="pdp",
                candidate_type="merged",
                candidate_sku="sku-7",
                score=5.0,
                version=1,
            ),
            RecommendationCandidate(
                seed_sku="sku-1",
                placement="pdp",
                candidate_type="merged",
                candidate_sku="sku-7",
                score=4.0,
                version=2,
            ),
        ]
    )
    db.commit()
    db.execute(text("SET search_path TO public"))


def test_publish_status_returns_versions_and_latest_run(authenticated_client, test_db):
    seed_publish_state(test_db)

    response = authenticated_client.get("/v1/shops/test/publishes/status")
    assert response.status_code == 200

    payload = response.json()
    assert payload["shop_id"] == "test"
    placements = {entry["placement"]: entry for entry in payload["placements"]}
    assert placements["pdp"]["current_version"] == 2
    assert placements["pdp"]["previous_version"] == 1
    assert placements["pdp"]["latest_run"]["status"] == "success"
    assert placements["pdp"]["latest_run"]["run_date"] == "2026-02-23"
    assert placements["cart"]["current_version"] == 3
    assert placements["cart"]["previous_version"] == 2


def test_publish_rollback_swaps_versions(authenticated_client, test_db):
    seed_candidates_for_rollback(test_db)

    response = authenticated_client.post(
        "/v1/shops/test/publishes/rollback", json={"placement": "pdp"}
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["rolled_back"] is True
    assert payload["current_version"] == 1
    assert payload["previous_version"] == 2

    test_db.execute(text("SET search_path TO shop_test"))
    state = (
        test_db.query(RecommendationPublishState)
        .filter(RecommendationPublishState.placement == "pdp")
        .first()
    )
    assert state.current_version == 1
    assert state.previous_version == 2
