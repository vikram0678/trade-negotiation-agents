import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.constraint_validator import ConstraintValidator
from core.evaluator import AgreementEvaluator
from core.issue_validator import IssueValidator
from core.models import NegotiationRequest, NegotiationResult


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_negotiation(request, result):
    report = {
        "topic": request.topic,
        "rounds_completed": len(result.rounds),
        "agreement_reached": False,
        "verified": False,
        "final_terms": {},
        "constraint_violations": [],
        "constraint_warnings": [],
        "unresolved_issues": [],
    }

    if (
        result.topic != request.topic
        or result.party_a_name != request.party_a.name
        or result.party_b_name != request.party_b.name
    ):
        raise ValueError(
            "Negotiation result does not match the supplied request."
        )

    if not result.outcome.agreement_reached:
        report["unresolved_issues"] = (
            result.outcome.unresolved_issues
        )
        report["evaluation_summary"] = (
            "No agreement was reported by the negotiation engine."
        )
        return report

    # Find a round in which both parties explicitly accepted.
    accepted_rounds = [
        round_record
        for round_record in result.rounds
        if (
            round_record.party_a_accepted
            and round_record.party_b_accepted
        )
    ]

    if not accepted_rounds:
        raise ValueError(
            "Agreement was reported, but no round records "
            "show explicit acceptance by both parties."
        )

    final_round = accepted_rounds[-1]

    if (
        final_round.party_a_proposal is None
        or final_round.party_b_response is None
    ):
        raise ValueError(
            "The accepted round is missing proposal information."
        )

    # Party B's response contains the candidate final terms.
    # final_terms = final_round.party_b_response.terms
    # Retrieve the exact terms explicitly accepted by each party.
    party_a_accepted_terms = final_round.party_a_accepted_terms
    party_b_accepted_terms = final_round.party_b_accepted_terms

    # Both parties must have recorded acceptance evidence.
    if not party_a_accepted_terms or not party_b_accepted_terms:
        raise ValueError(
            "Agreement was reported, but exact acceptance terms "
            "are missing from the round record."
        )

    # Independently verify that both parties accepted identical terms.
    if party_a_accepted_terms != party_b_accepted_terms:
        raise ValueError(
            "Agreement was reported, but the parties' accepted terms differ."
        )

    final_terms = party_a_accepted_terms
    # Free-text constraints cannot be independently verified here.
    if request.party_a.constraints or request.party_b.constraints:
        raise ValueError(
            "Cannot independently verify free-text constraints. "
            "A configured custom constraint checker is required."
        )

    issue_validation = IssueValidator().validate(
        final_terms,
        request.issues,
    )

    if not issue_validation.valid:
        raise ValueError(
            "Final terms do not match the requested issues. "
            f"Missing: {issue_validation.missing_issues}. "
            f"Unexpected: {issue_validation.unexpected_issues}."
        )

    constraint_validation = ConstraintValidator().validate(
        final_terms,
        request.party_a,
        request.party_b,
    )

    report["constraint_violations"] = (
        constraint_validation.violations
    )
    report["constraint_warnings"] = (
        constraint_validation.warnings
    )

    evaluation = AgreementEvaluator.evaluate(
        party_a_accepted=final_round.party_a_accepted,
        party_b_accepted=final_round.party_b_accepted,
        party_a_terms=party_a_accepted_terms,
        party_b_terms=party_b_accepted_terms,
        constraints_satisfied=constraint_validation.valid,
    )

    if not evaluation.agreement_reached:
        report["unresolved_issues"] = (
            evaluation.unresolved_issues
        )
        report["evaluation_summary"] = (
            evaluation.evaluation_summary
        )
        return report

    if result.outcome.final_terms != evaluation.final_terms:
        raise ValueError(
            "The engine's final terms do not match the "
            "independently verified terms."
        )

    report.update({
        "agreement_reached": True,
        "verified": True,
        "final_terms": evaluation.final_terms,
        "evaluation_summary": evaluation.evaluation_summary,
    })

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Independently evaluate a negotiation result."
    )

    parser.add_argument(
        "--request",
        required=True,
        help="Path to the original negotiation request JSON.",
    )

    parser.add_argument(
        "--result",
        required=True,
        help="Path to the negotiation result JSON.",
    )

    args = parser.parse_args()

    try:
        request_data = load_json(Path(args.request))
        result_data = load_json(Path(args.result))

        request = NegotiationRequest.model_validate(request_data)
        result = NegotiationResult.model_validate(result_data)

        report = evaluate_negotiation(request, result)

        print(json.dumps(report, indent=2))

        if not report["verified"]:
            sys.exit(1)

    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
