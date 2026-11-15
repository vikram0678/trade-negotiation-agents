
from fastapi.testclient import TestClient

import main
from core.models import (
    NegotiationOutcome,
    NegotiationResult,
    RoundRecord,
    Proposal,
)


client = TestClient(main.app)


def create_mock_result():
    """Create a deterministic result without calling an LLM."""

    return NegotiationResult(
        topic="Equipment purchase agreement",
        party_a_name="Buyer",
        party_b_name="Supplier",
        rounds=[
            RoundRecord(
                round_number=1,
                party_a_proposal=Proposal(
                    party_name="Buyer",
                    terms={
                        "price": 90000,
                        "delivery_days": 25,
                    },
                    explanation="Initial proposal.",
                ),
                party_b_response=Proposal(
                    party_name="Supplier",
                    terms={
                        "price": 90000,
                        "delivery_days": 25,
                    },
                    explanation="Proposal accepted.",
                ),
                party_a_accepted=True,
                party_b_accepted=True,
                party_a_accepted_terms={
                    "price": 90000,
                    "delivery_days": 25,
                },
                party_b_accepted_terms={
                    "price": 90000,
                    "delivery_days": 25,
                },
                notes=["Both parties accepted the exact terms."],
            )
        ],
        outcome=NegotiationOutcome(
            agreement_reached=True,
            final_terms={
                "price": 90000,
                "delivery_days": 25,
            },
            unresolved_issues=[],
            evaluation_summary="Verified agreement.",
        ),
    )


def create_request():
    return {
        "party_a": {
            "name": "Buyer",
            "role": "Equipment purchaser",
            "priorities": {
                "price": 0.8,
                "delivery_days": 0.2,
            },
            "constraints": [],
            "constraint_rules": [
                {
                    "issue": "price",
                    "operator": "le",
                    "value": 100000,
                    "hard": True,
                }
            ],
            "background": "A buyer seeking affordable equipment.",
        },
        "party_b": {
            "name": "Supplier",
            "role": "Equipment supplier",
            "priorities": {
                "price": 0.7,
                "delivery_days": 0.3,
            },
            "constraints": [],
            "constraint_rules": [
                {
                    "issue": "price",
                    "operator": "ge",
                    "value": 80000,
                    "hard": True,
                }
            ],
            "background": "A supplier seeking a profitable contract.",
        },
        "topic": "Equipment purchase agreement",
        "issues": [
            {
                "name": "price",
                "description": "Total purchase price",
                "unit": "INR",
            },
            {
                "name": "delivery_days",
                "description": "Delivery period",
                "unit": "days",
            },
        ],
        "max_rounds": 5,
    }


def test_negotiation_endpoint_success(monkeypatch):
    """The API returns a successful result from the engine."""

    async def fake_run(request):
        assert request.topic == "Equipment purchase agreement"
        return create_mock_result()

    monkeypatch.setattr(main.engine, "run", fake_run)

    response = client.post(
        "/negotiate",
        json=create_request(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["topic"] == "Equipment purchase agreement"
    assert len(data["rounds"]) == 1
    assert data["outcome"]["agreement_reached"] is True
    assert data["outcome"]["final_terms"]["price"] == 90000


def test_negotiation_endpoint_rejects_invalid_request():
    """The API rejects requests that fail schema validation."""

    invalid_request = create_request()
    del invalid_request["party_a"]["name"]

    response = client.post(
        "/negotiate",
        json=invalid_request,
    )

    assert response.status_code == 422


def test_negotiation_endpoint_handles_engine_error(monkeypatch):
    """The API handles negotiation errors without exposing internals."""

    async def fake_run(request):
        raise ValueError("Invalid negotiation terms.")

    monkeypatch.setattr(main.engine, "run", fake_run)

    response = client.post(
        "/negotiate",
        json=create_request(),
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid negotiation terms."


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
