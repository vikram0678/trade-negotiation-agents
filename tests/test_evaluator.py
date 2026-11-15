
from core.evaluator import AgreementEvaluator


def test_agreement_when_both_parties_accept_identical_terms():
    terms = {
        "price_inr": 85000,
        "delivery_days": 25,
        "warranty_months": 12,
    }

    result = AgreementEvaluator.evaluate(
        party_a_accepted=True,
        party_b_accepted=True,
        party_a_terms=terms,
        party_b_terms=terms.copy(),
        constraints_satisfied=True,
    )

    assert result.agreement_reached is True
    assert result.final_terms == terms
    assert result.unresolved_issues == []


def test_no_agreement_when_party_a_does_not_accept():
    terms = {"price_inr": 85000}

    result = AgreementEvaluator.evaluate(
        party_a_accepted=False,
        party_b_accepted=True,
        party_a_terms=None,
        party_b_terms=terms,
        constraints_satisfied=True,
    )

    assert result.agreement_reached is False
    assert result.final_terms == {}


def test_no_agreement_when_party_b_does_not_accept():
    terms = {"price_inr": 85000}

    result = AgreementEvaluator.evaluate(
        party_a_accepted=True,
        party_b_accepted=False,
        party_a_terms=terms,
        party_b_terms=None,
        constraints_satisfied=True,
    )

    assert result.agreement_reached is False
    assert result.final_terms == {}


def test_no_agreement_when_accepted_terms_differ():
    party_a_terms = {"price_inr": 85000}
    party_b_terms = {"price_inr": 90000}

    result = AgreementEvaluator.evaluate(
        party_a_accepted=True,
        party_b_accepted=True,
        party_a_terms=party_a_terms,
        party_b_terms=party_b_terms,
        constraints_satisfied=True,
    )

    assert result.agreement_reached is False
    assert result.final_terms == {}


def test_no_agreement_when_acceptance_evidence_is_missing():
    result = AgreementEvaluator.evaluate(
        party_a_accepted=True,
        party_b_accepted=True,
        party_a_terms=None,
        party_b_terms=None,
        constraints_satisfied=True,
    )

    assert result.agreement_reached is False
    assert result.final_terms == {}


def test_no_agreement_when_hard_constraints_fail():
    terms = {"price_inr": 95000}

    result = AgreementEvaluator.evaluate(
        party_a_accepted=True,
        party_b_accepted=True,
        party_a_terms=terms,
        party_b_terms=terms.copy(),
        constraints_satisfied=False,
    )

    assert result.agreement_reached is False
    assert result.final_terms == {}
