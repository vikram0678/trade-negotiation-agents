
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class ConstraintRule(BaseModel):
    """A machine-readable constraint on a negotiation term."""

    model_config = ConfigDict(extra="forbid")

    issue: str = Field(min_length=1, max_length=150)

    operator: Literal["eq", "le", "ge", "in"]

    value: Any

    hard: bool = True

    @model_validator(mode="after")
    def validate_rule_value(self):
        if self.operator == "in" and not isinstance(self.value, list):
            raise ValueError(
                "The value for the 'in' operator must be a list."
            )

        if self.operator != "in" and isinstance(
            self.value, (list, dict, set)
        ):
            raise ValueError(
                "This operator requires a single comparison value."
            )

        return self


class PartyProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)

    role: str = Field(min_length=1, max_length=150)

    priorities: dict[str, float] = Field(default_factory=dict)

    # Existing human-readable constraints are preserved.
    constraints: list[str] = Field(default_factory=list)

    # New machine-readable constraints.
    constraint_rules: list[ConstraintRule] = Field(
        default_factory=list
    )

    background: str = ""


class NegotiationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=150)

    description: str = ""

    unit: str | None = None


class NegotiationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    party_a: PartyProfile

    party_b: PartyProfile

    topic: str = Field(min_length=1, max_length=300)

    issues: list[NegotiationIssue] = Field(min_length=1)

    max_rounds: int = Field(default=5, ge=1, le=50)

    # provider: Literal["ollama"] = "ollama"

    # model: str = "llama3"

    @model_validator(mode="after")
    def validate_parties(self):
        if (
            self.party_a.name.strip().casefold()
            == self.party_b.name.strip().casefold()
        ):
            raise ValueError(
                "Party A and Party B must have different names."
            )

        return self


class Proposal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    party_name: str

    terms: dict[str, Any]

    explanation: str = ""


class RoundRecord(BaseModel):
    round_number: int = Field(ge=1)

    party_a_proposal: Proposal | None = None

    party_b_response: Proposal | None = None

    party_a_accepted: bool = False

    party_b_accepted: bool = False

    # Exact terms explicitly accepted by each party.
    party_a_accepted_terms: dict[str, Any] | None = None

    party_b_accepted_terms: dict[str, Any] | None = None

    notes: list[str] = Field(default_factory=list)


class NegotiationOutcome(BaseModel):
    agreement_reached: bool = False

    final_terms: dict[str, Any] = Field(default_factory=dict)

    unresolved_issues: list[str] = Field(default_factory=list)

    evaluation_summary: str = ""


class NegotiationResult(BaseModel):
    topic: str

    party_a_name: str

    party_b_name: str

    rounds: list[RoundRecord] = Field(default_factory=list)

    outcome: NegotiationOutcome = Field(
        default_factory=NegotiationOutcome
    )
