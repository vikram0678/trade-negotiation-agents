
from dataclasses import dataclass, field
from typing import Any

from core.models import NegotiationIssue


@dataclass
class IssueValidationResult:
    valid: bool = True
    missing_issues: list[str] = field(default_factory=list)
    unexpected_issues: list[str] = field(default_factory=list)


class IssueValidator:
    """Validates whether proposal terms cover requested issues."""

    @staticmethod
    def validate(
        terms: dict[str, Any],
        issues: list[NegotiationIssue],
    ) -> IssueValidationResult:

        expected = {
            issue.name.casefold(): issue.name
            for issue in issues
        }

        provided = {
            key.casefold(): key
            for key in terms
        }

        missing = [
            original_name
            for normalized, original_name in expected.items()
            if normalized not in provided
        ]

        unexpected = [
            original_name
            for normalized, original_name in provided.items()
            if normalized not in expected
        ]

        return IssueValidationResult(
            valid=not missing and not unexpected,
            missing_issues=missing,
            unexpected_issues=unexpected,
        )
