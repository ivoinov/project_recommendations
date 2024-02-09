from fastapi.testclient import TestClient
import pytest
from main import app
client = TestClient(app)


def test_upselling_recommendations():
    valid_token = "invalid_token"
    valid_product_id = 1
    # check not valid token
    response = client.get(
        f"/upselling-recommendations/{valid_product_id}",
        headers={"Authorization": f"Bearer {valid_token}"},
    )

    assert response.status_code == 401

    # Test with an empty token
    empty_token = ""
    response = client.get(
        f"/upselling-recommendations/{valid_product_id}",
        headers={"Authorization": f"Bearer {empty_token}"},
    )
    assert response.status_code == 401
