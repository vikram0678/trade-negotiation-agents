
import asyncio
import os

import pytest

from core.engine import NegotiationEngine
from core.models import (
    ConstraintRule,
    NegotiationIssue,
    NegotiationRequest,
    PartyProfile,
)


def test_real_ollama_negotiation():
    if os.getenv("RUN_REAL_LLM_TESTS") != "1":
        pytest.skip(
            "Set RUN_REAL_LLM_TESTS=1 to run real Ollama integration."
        )

    async def run_negotiation():
        buyer = PartyProfile(
            name="Buyer",
            role="Purchaser",
            constraint_rules=[
                ConstraintRule(
                    issue="price",
                    operator="le",
                    value=100000,
                )
            ],
        )

        seller = PartyProfile(
            name="Seller",
            role="Supplier",
            constraint_rules=[
                ConstraintRule(
                    issue="price",
                    operator="ge",
                    value=80000,
                )
            ],
        )

        request = NegotiationRequest(
            party_a=buyer,
            party_b=seller,
            topic="Product purchase negotiation",
            issues=[
                NegotiationIssue(
                    name="price",
                    description="Agreed purchase price",
                    unit="INR",
                ),
                NegotiationIssue(
                    name="delivery_days",
                    description="Number of days for delivery",
                    unit="days",
                ),
            ],
        max_rounds=3,
        )

        # Uses the default provider factory, which selects Ollama
        # through LLM_PROVIDER in the environment.
        engine = NegotiationEngine()

        result = await engine.run(request)

        assert result.rounds, "Negotiation produced no rounds."
        assert result.outcome is not None
        assert isinstance(
            result.outcome.agreement_reached,
            bool,
        )

        print("\nReal Ollama negotiation completed.")
        print("Rounds:", len(result.rounds))

        for index, round_result in enumerate(result.rounds, start=1):
            print(f"\n========== ROUND {index} ==========")
            print("Round details:", repr(round_result))

        print("\n========== FINAL OUTCOME ==========")
        print("Agreement reached:", result.outcome.agreement_reached)
        print("Final terms:", result.outcome.final_terms)
        print("Outcome details:", repr(result.outcome))

    asyncio.run(run_negotiation())
