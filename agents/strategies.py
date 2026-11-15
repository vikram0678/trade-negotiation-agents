
from enum import Enum


class StrategyAction(str, Enum):
    """Actions a negotiating party can take."""

    ACCEPT = "accept"
    REJECT = "reject"
    COUNTEROFFER = "counteroffer"
    COMPROMISE = "compromise"


class NegotiationStrategy:
    """
    Selects a negotiation action and provides instructions for that action.

    This class does not call an LLM or independently verify contract terms.
    The caller must evaluate whether a proposal is acceptable.
    """

    @staticmethod
    def choose_action(
        *,
        proposal_acceptable: bool,
        compromise_possible: bool = False,
        final_round: bool = False,
    ) -> StrategyAction:
        """
        Select an action based on the proposal evaluation.

        proposal_acceptable must only be True after the caller has
        checked the relevant acceptance conditions and constraints.
        """

        if proposal_acceptable:
            return StrategyAction.ACCEPT

        if final_round:
            return StrategyAction.REJECT

        if compromise_possible:
            return StrategyAction.COMPROMISE

        return StrategyAction.COUNTEROFFER

    @staticmethod
    def build_instruction(action: StrategyAction) -> str:
        """Return guidance for the negotiator's selected action."""

        instructions = {
            StrategyAction.ACCEPT: (
                "Accept the proposal. Clearly identify the terms "
                "being accepted. Do not add new conditions."
            ),
            StrategyAction.REJECT: (
                "Reject the proposal respectfully. Explain the main "
                "reason and identify any unresolved issues."
            ),
            StrategyAction.COUNTEROFFER: (
                "Present a specific counteroffer that protects your "
                "party's priorities and respects its constraints."
            ),
            StrategyAction.COMPROMISE: (
                "Explore a reasonable middle ground. Explain which "
                "terms could be adjusted and which must be protected."
            ),
        }

        return instructions[action]
