
from dataclasses import dataclass, field
from numbers import Real
from typing import Any

from core.models import ConstraintRule, PartyProfile


@dataclass
class ConstraintValidationResult:
    """Result of checking both parties' structured constraints."""

    valid: bool = True
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ConstraintValidator:
    """Validates proposed terms against both parties' constraint rules."""

    @staticmethod
    def _get_term(
        terms: dict[str, Any],
        issue: str,
    ) -> tuple[bool, Any]:
        """Find a term using a case-insensitive issue name."""
        for key, value in terms.items():
            if key.casefold() == issue.casefold():
                return True, value

        return False, None

    @staticmethod
    def _check_rule(
        actual_value: Any,
        rule: ConstraintRule,
    ) -> bool:
        """Return whether one constraint rule is satisfied."""

        if rule.operator == "eq":
            return actual_value == rule.value

        if rule.operator == "in":
            return actual_value in rule.value

        if rule.operator in {"le", "ge"}:
            # Numeric comparisons must use real numbers, not booleans.
            if (
                isinstance(actual_value, bool)
                or not isinstance(actual_value, Real)
                or isinstance(rule.value, bool)
                or not isinstance(rule.value, Real)
            ):
                return False

            if rule.operator == "le":
                return actual_value <= rule.value

            return actual_value >= rule.value

        return False

    def validate(
        self,
        terms: dict[str, Any],
        party_a: PartyProfile,
        party_b: PartyProfile,
    ) -> ConstraintValidationResult:
        """
        Validate terms against both parties' structured constraints.

        Hard-rule failures block an agreement.
        Soft-rule failures are recorded as warnings only.
        """
        result = ConstraintValidationResult()

        parties = [
            party_a,
            party_b,
        ]

        for party in parties:
            for rule in party.constraint_rules:
                exists, actual_value = self._get_term(
                    terms,
                    rule.issue,
                )

                if not exists:
                    message = (
                        f"{party.name}: Missing term '{rule.issue}'."
                    )
                    if rule.hard:
                        result.violations.append(message)
                    else:
                        result.warnings.append(message)
                    continue

                satisfied = self._check_rule(
                    actual_value,
                    rule,
                )

                if not satisfied:
                    message = (
                        f"{party.name}: Constraint failed for "
                        f"'{rule.issue}' "
                        f"({rule.operator} {rule.value}); "
                        f"received {actual_value}."
                    )

                    if rule.hard:
                        result.violations.append(message)
                    else:
                        result.warnings.append(message)

        result.valid = len(result.violations) == 0

        return result
