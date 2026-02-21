from datetime import datetime, timedelta, timezone


def test_engagement_events_logged_and_summarized(authenticated_client):
    from_ts = datetime.now(timezone.utc) - timedelta(minutes=5)
    to_ts = datetime.now(timezone.utc) + timedelta(minutes=5)

    response = authenticated_client.post(
        "/v1/shops/test/engagement/recommendations",
        json={
            "placement": "pdp",
            "event_type": "click",
            "recommended_sku": "sku-1",
            "context_skus": ["sku-2", "sku-3"],
            "session_id": "session-1",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["placement"] == "pdp"
    assert payload["event_type"] == "click"
    assert payload["context_skus"] == ["sku-2", "sku-3"]

    response = authenticated_client.post(
        "/v1/shops/test/engagement/recommendations",
        json={
            "placement": "cart",
            "event_type": "add_to_cart",
            "recommended_sku": "sku-4",
            "context_skus": ["sku-1"],
            "customer_id": 42,
            "request_id": "req-123",
        },
    )
    assert response.status_code == 200

    summary = authenticated_client.get(
        "/v1/shops/test/engagement/recommendations/summary",
        params={"from": from_ts.isoformat(), "to": to_ts.isoformat()},
    )
    assert summary.status_code == 200
    summary_payload = summary.json()
    counts = {
        (item["placement"], item["event_type"]): item["count"]
        for item in summary_payload["results"]
    }
    assert counts[("pdp", "click")] == 1
    assert counts[("cart", "add_to_cart")] == 1

    filtered = authenticated_client.get(
        "/v1/shops/test/engagement/recommendations/summary",
        params={
            "from": from_ts.isoformat(),
            "to": to_ts.isoformat(),
            "placement": "pdp",
        },
    )
    assert filtered.status_code == 200
    filtered_payload = filtered.json()
    assert len(filtered_payload["results"]) == 1
    assert filtered_payload["results"][0]["placement"] == "pdp"
