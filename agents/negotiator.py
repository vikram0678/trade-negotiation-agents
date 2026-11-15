
from typing import Any

from core.models import PartyProfile
from providers.base import BaseLLMProvider
from providers.factory import create_provider


class Negotiator:
    def __init__(
        self,
        country: str | PartyProfile,
        positions: dict[str, Any] | None = None,
        *,
        provider: BaseLLMProvider | None = None,
    ):
        if isinstance(country, PartyProfile):
            self.profile = country
            self.country = country.name

            self.positions = {
                "priorities": country.priorities,
                "constraints": country.constraints,
                "constraint_rules": country.constraint_rules,
                "role": country.role,
                "background": country.background,
            }
        else:
            self.country = country
            self.positions = positions or {}
            self.profile = None

        # Provider configuration comes exclusively from .env.
        self.provider = provider or create_provider()

    async def generate_response(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response through the configured LLM provider."""
        return await self.provider.generate(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        )

    async def make_proposal(
        self,
        issue: str,
        history: list,
    ) -> str:
        """Generate a structured JSON proposal."""

        priorities = self.positions.get("priorities", {})
        constraints = self.positions.get("constraints", [])
        constraint_rules = self.positions.get("constraint_rules", [])
        role = self.positions.get("role", "Negotiating party")
        background = self.positions.get("background", "")

        system_prompt = (
            f"You are the negotiation representative for {self.country}. "
            "Return valid JSON only. Do not use Markdown fences."
        )

        prompt = f"""
You are preparing a negotiation proposal.

PARTY: {self.country}
ROLE: {role}
BACKGROUND: {background}

YOUR PRIVATE PRIORITIES: {priorities}
YOUR PRIVATE CONSTRAINTS: {constraints}
YOUR PRIVATE STRUCTURED CONSTRAINTS: {constraint_rules}

NEGOTIATION ISSUE:
{issue}

PUBLIC NEGOTIATION HISTORY:
{history}

Instructions:
1. Protect your party's interests.
2. Respect your private constraints.
3. Consider previous proposals and responses.
4. Use action "propose" for a new proposal.
5. Return specific, measurable terms in JSON.
6. Do not reveal private priorities or constraints.
7. Do not claim the other party has accepted your proposal.
8. Include all requested negotiation issues.

Return exactly this JSON structure:

{{
    "action": "propose",
    "terms": {{
        "price": 90,
        "delivery_days": 30
    }},
    "explanation": "Brief explanation of the proposal."
}}

Use the actual negotiation issues and values.
Do not blindly copy the example values.
"""

        return await self.generate_response(
            prompt,
            system_prompt=system_prompt,
            temperature=0.3,
        )
