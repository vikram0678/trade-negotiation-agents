
from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """
    Common interface for all LLM providers.

    Every provider must implement the generate() method.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text using the configured language model.

        Args:
            prompt: The user's or agent's input prompt.
            system_prompt: Optional instructions for the model.
            temperature: Controls the randomness of the response.

        Returns:
            Generated text as a string.
        """
        raise NotImplementedError
