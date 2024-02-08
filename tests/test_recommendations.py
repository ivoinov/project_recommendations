from fastapi.testclient import TestClient
from main import (
    app,
)  # assuming your FastAPI app is named app and is in the main.py file
import pytest

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
