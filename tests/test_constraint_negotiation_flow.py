
import asyncio
import json

from core.engine import NegotiationEngine
from core.models import (
    ConstraintRule,
    NegotiationIssue,
    NegotiationRequest,
    PartyProfile,
)


class FakeProvider:
    def __init__(self, responses):
        self.responses = list(responses)

    async def generate(
        self,
        prompt,
        *,
        system_prompt=None,
        temperature=0.7,
    ):
        if not self.responses:
            raise AssertionError("No fake responses remaining.")

        return json.dumps(self.responses.pop(0))


def make_request(buyer, seller):
    return NegotiationRequest(
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
        max_rounds=1,
    )


def make_engine(a_responses, b_responses):
    def provider_factory(request, party):
        if party.name == "Buyer":
            return FakeProvider(a_responses)
        return FakeProvider(b_responses)

    return NegotiationEngine(
        provider_factory=provider_factory,
    )


def accepted_response(terms):
    return {
        "action": "accept",
        "terms": terms,
        "explanation": "I accept these exact terms.",
    }


def proposal_response(terms):
    return {
        "action": "propose",
        "terms": terms,
        "explanation": "Initial proposal.",
    }


async def run_valid_agreement():
    buyer = PartyProfile(
        name="Buyer",
        role="Purchaser",
        constraint_rules=[
            ConstraintRule(
                issue="price",
                operator="le",
                value=100,
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
                value=80,
            )
        ],
    )

    terms = {"price": 90, "delivery_days": 30}

    engine = make_engine(
        [proposal_response(terms), accepted_response(terms)],
        [accepted_response(terms)],
    )

    result = await engine.run(make_request(buyer, seller))

    assert result.outcome.agreement_reached is True
    assert result.outcome.final_terms == terms

    print("PASS: Valid agreement accepted.")


async def run_accepted_terms_violating_hard_constraint():
    buyer = PartyProfile(
        name="Buyer",
        role="Purchaser",
        constraint_rules=[
            ConstraintRule(
                issue="price",
                operator="le",
                value=100,
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
                value=80,
            )
        ],
    )

    terms = {"price": 110, "delivery_days": 30}

    engine = make_engine(
        [proposal_response(terms), accepted_response(terms)],
        [accepted_response(terms)],
    )

    result = await engine.run(make_request(buyer, seller))

    assert result.rounds[0].party_a_accepted is True
    assert result.rounds[0].party_b_accepted is True
    assert result.outcome.agreement_reached is False
    assert result.outcome.final_terms == {}

    assert any(
        "Constraint violation" in note
        for note in result.rounds[0].notes
    )

    print("PASS: Hard constraint prevented agreement.")


async def run_soft_constraint_warning():
    buyer = PartyProfile(
        name="Buyer",
        role="Purchaser",
        constraint_rules=[
            ConstraintRule(
                issue="delivery_days",
                operator="le",
                value=30,
                hard=False,
            )
        ],
    )

    seller = PartyProfile(
        name="Seller",
        role="Supplier",
    )

    terms = {"price": 90, "delivery_days": 45}

    engine = make_engine(
        [proposal_response(terms), accepted_response(terms)],
        [accepted_response(terms)],
    )

    result = await engine.run(make_request(buyer, seller))

    assert result.outcome.agreement_reached is True

    assert any(
        "Constraint warning" in note
        for note in result.rounds[0].notes
    )

    print("PASS: Soft constraint warning recorded.")



async def run_counteroffer_is_not_agreement():
    buyer = PartyProfile(
        name="Buyer",
        role="Purchaser",
    )

    seller = PartyProfile(
        name="Seller",
        role="Supplier",
    )

    proposed_terms = {"price": 90, "delivery_days": 30}
    counter_terms = {"price": 85, "delivery_days": 30}

    engine = make_engine(
        [
            proposal_response(proposed_terms),
            {
                "action": "reject",
                "terms": counter_terms,
                "explanation": "I reject the counteroffer.",
            },
        ],
        [
            {
                "action": "counteroffer",
                "terms": counter_terms,
                "explanation": "I propose a lower price.",
            }
        ],
    )

    result = await engine.run(make_request(buyer, seller))

    assert result.outcome.agreement_reached is False
    assert result.rounds[0].party_a_accepted is False
    assert result.rounds[0].party_b_accepted is False

    print("PASS: Rejected counteroffer did not create an agreement.")





async def run_accepted_counteroffer():
    buyer = PartyProfile(
        name="Buyer",
        role="Purchaser",
    )

    seller = PartyProfile(
        name="Seller",
        role="Supplier",
    )

    original_terms = {"price": 90, "delivery_days": 30}
    counter_terms = {"price": 85, "delivery_days": 30}

    engine = make_engine(
        [
            proposal_response(original_terms),
            accepted_response(counter_terms),
        ],
        [
            {
                "action": "counteroffer",
                "terms": counter_terms,
                "explanation": "I propose a lower price.",
            },
            accepted_response(counter_terms),
        ],
    )

    result = await engine.run(make_request(buyer, seller))

    assert result.outcome.agreement_reached is True
    assert result.outcome.final_terms == counter_terms
    assert result.rounds[0].party_a_accepted is True
    assert result.rounds[0].party_b_accepted is True

    print("PASS: Accepted counteroffer successfully finalized.")


async def run_repeated_counteroffers():
    buyer = PartyProfile(
        name="Buyer",
        role="Purchaser",
    )

    seller = PartyProfile(
        name="Seller",
        role="Supplier",
    )

    original_terms = {"price": 90, "delivery_days": 30}
    seller_counter = {"price": 85, "delivery_days": 30}
    buyer_counter = {"price": 88, "delivery_days": 30}

    engine = make_engine(
        [
            proposal_response(original_terms),
            {
                "action": "counteroffer",
                "terms": buyer_counter,
                "explanation": "I propose a different price.",
            },
        ],
        [
            {
                "action": "counteroffer",
                "terms": seller_counter,
                "explanation": "I propose a lower price.",
            },
        ],
    )

    result = await engine.run(make_request(buyer, seller))

    assert result.outcome.agreement_reached is False
    assert result.outcome.final_terms == {}

    print("PASS: Repeated counteroffers did not create a false agreement.")


async def run_maximum_rounds_exhausted():
    buyer = PartyProfile(
        name="Buyer",
        role="Purchaser",
    )

    seller = PartyProfile(
        name="Seller",
        role="Supplier",
    )

    first_terms = {"price": 90, "delivery_days": 30}
    second_terms = {"price": 85, "delivery_days": 30}

    engine = make_engine(
        [
            # Round 1: Buyer submits initial proposal.
            proposal_response(first_terms),

            # Round 1: Buyer evaluates Seller's counteroffer.
            {
                "action": "counteroffer",
                "terms": {"price": 88, "delivery_days": 30},
                "explanation": "I propose a different price.",
            },

            # Round 2: Buyer submits another proposal.
            proposal_response(
                {"price": 87, "delivery_days": 30}
            ),

            # Round 2: Buyer evaluates Seller's next counteroffer.
            {
                "action": "counteroffer",
                "terms": {"price": 87, "delivery_days": 30},
                "explanation": "I maintain my proposed price.",
            },
        ],
        [
            # Round 1: Seller counteroffers.
            {
                "action": "counteroffer",
                "terms": second_terms,
                "explanation": "I propose a lower price.",
            },

            # Round 2: Seller counteroffers again.
            {
                "action": "counteroffer",
                "terms": {"price": 86, "delivery_days": 30},
                "explanation": "I propose another price.",
            },
        ],
    )


    request = make_request(buyer, seller)
    request.max_rounds = 2

    result = await engine.run(request)

    assert len(result.rounds) == 2
    assert result.rounds[-1].round_number == 2
    assert result.outcome.agreement_reached is False
    assert result.outcome.final_terms == {}
    assert (
        "Maximum negotiation rounds completed"
        in result.outcome.evaluation_summary
    )

    print("PASS: Negotiation stopped after maximum rounds.")


async def run_incomplete_proposal_rejected():
    buyer = PartyProfile(
        name="Buyer",
        role="Purchaser",
    )

    seller = PartyProfile(
        name="Seller",
        role="Supplier",
    )

    # Missing delivery_days.
    incomplete_terms = {
        "price": 90,
    }

    engine = make_engine(
        [proposal_response(incomplete_terms)],
        [],
    )

    try:
        await engine.run(make_request(buyer, seller))

    except ValueError as exc:
        assert "delivery_days" in str(exc)
        print("PASS: Incomplete proposal rejected before Party B responds.")

    else:
        raise AssertionError(
            "Engine incorrectly accepted an incomplete proposal."
        )

def test_complete_negotiation_flows():
    asyncio.run(run_valid_agreement())
    asyncio.run(run_accepted_terms_violating_hard_constraint())
    asyncio.run(run_soft_constraint_warning())
    asyncio.run(run_counteroffer_is_not_agreement())
    asyncio.run(run_accepted_counteroffer())
    asyncio.run(run_repeated_counteroffers())
    asyncio.run(run_incomplete_proposal_rejected())
    asyncio.run(run_maximum_rounds_exhausted())