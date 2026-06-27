# scoring.py

# Words that suggest someone is giving ground / compromising.
# This list is the "signal" we search for in each round's text.
CONCESSION_KEYWORDS = [
    "agree", "accept", "lower", "reduce", "compromise",
    "willing", "concede", "flexible", "open to",
]


def calculate_compromise(history: list, positions: dict) -> float:
    """
    Heuristic scoring (no LLM needed):
    Looks through the negotiation history and counts how many
    concession-style keywords appear. More keywords -> higher score.

    Returns a float between 0.0 and 1.0.
    """
    if not history:
        return 0.0

    # Combine every round's text into one big lowercase string to search through
    full_text = " ".join(str(round_data) for round_data in history).lower()

    # Count how many times any concession keyword appears
    concession_count = sum(
        full_text.count(keyword) for keyword in CONCESSION_KEYWORDS
    )

    # Turn the raw count into a 0.0-1.0 score.
    # We assume ~10 concession mentions = "fully compromised" (score 1.0).
    # This cap number (10) is a tunable assumption you can adjust later.
    max_expected_concessions = 5
    score = concession_count / max_expected_concessions

    # Make sure the score never goes above 1.0
    return min(score, 1.0)