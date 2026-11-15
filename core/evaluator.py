
from typing import Any

from core.models import NegotiationOutcome


class AgreementEvaluator:
    """
    Determines whether two parties have reached an agreement.

    Agreement requires:
    1. Explicit acceptance from Party A.
    2. Explicit acceptance from Party B.
    3. Recorded acceptance terms from both parties.
    4. Identical accepted terms.
    5. Verified satisfaction of applicable hard constraints.
    """

    @staticmethod
    def evaluate(
        *,
        party_a_accepted: bool,
        party_b_accepted: bool,
        party_a_terms: dict[str, Any] | None,
        party_b_terms: dict[str, Any] | None,
        constraints_satisfied: bool,
        unresolved_issues: list[str] | None = None,
    ) -> NegotiationOutcome:

        unresolved = list(unresolved_issues or [])

        # Both parties must explicitly accept.
        both_accepted = (
            party_a_accepted and party_b_accepted
        )

        # Both parties must provide recorded acceptance evidence.
        evidence_present = (
            party_a_terms is not None
            and party_b_terms is not None
            and bool(party_a_terms)
            and bool(party_b_terms)
        )

        # Compare the exact terms accepted by each party.
        same_terms = (
            evidence_present
            and party_a_terms == party_b_terms
        )

        # Every condition must pass.
        agreement_reached = (
            both_accepted
            and evidence_present
            and same_terms
            and constraints_satisfied
        )

        if agreement_reached:
            return NegotiationOutcome(
                agreement_reached=True,
                final_terms=party_a_terms,
                unresolved_issues=[],
                evaluation_summary=(
                    "Both parties explicitly accepted the same recorded "
                    "terms, and all applicable hard constraints "
                    "were verified."
                ),
            )

        reasons = []

        if not party_a_accepted:
            reasons.append(
                "Party A has not explicitly accepted."
            )

        if not party_b_accepted:
            reasons.append(
                "Party B has not explicitly accepted."
            )

        if not evidence_present:
            reasons.append(
                "Recorded acceptance evidence is missing."
            )
        elif not same_terms:
            reasons.append(
                "The parties' explicitly accepted terms do not match."
            )

        if not constraints_satisfied:
            reasons.append(
                "Hard constraints have not been verified as satisfied."
            )

        for reason in reasons:
            if reason not in unresolved:
                unresolved.append(reason)

        return NegotiationOutcome(
            agreement_reached=False,
            final_terms={},
            unresolved_issues=unresolved,
            evaluation_summary=(
                "No agreement was established. "
                + " ".join(reasons)
            ),
        )
