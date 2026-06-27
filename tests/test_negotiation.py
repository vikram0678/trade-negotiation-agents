# tests/test_negotiation.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# Negotiation with rounds=3 completes and returns rounds array of length 3
def test_negotiation_endpoint_success():
    response = client.post("/negotiate", json={"issue": "Technology Tariffs", "rounds": 3})
    assert response.status_code == 200
    data = response.json()
    assert "rounds" in data
    assert "outcome" in data
    assert len(data["rounds"]) == 3
    assert "compromise_score" in data["outcome"]


# Agents reference their actual priorities from trade_positions.json
def test_agents_reference_their_priorities():
    response = client.post("/negotiate", json={"issue": "Technology Tariffs", "rounds": 3})
    data = response.json()

    all_usa_text = " ".join(
        r["usa_proposal"] for r in data["rounds"]
    ).lower()

    all_china_text = " ".join(
        r["china_response"] for r in data["rounds"]
    ).lower()

    assert any(
        word in all_usa_text
        for word in ["ip", "protection", "tariff", "technology"]
    )

    assert any(
        word in all_china_text
        for word in ["market", "agricultural", "transfer", "access"]
    )