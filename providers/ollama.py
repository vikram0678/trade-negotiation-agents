import os

import httpx

from providers.base import BaseLLMProvider

# from dotenv import load_dotenv
# load_dotenv()

# OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
# OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", 180))


class OllamaProviderError(Exception):
    """Raised when an Ollama request fails."""


class OllamaProvider(BaseLLMProvider):
    """LLM provider that generates text using a local Ollama server."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "llama3",
        timeout: float = 180.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.transport = transport

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Send a prompt to Ollama and return the generated response."""

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0.")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                transport=self.transport,
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )

                response.raise_for_status()
                data = response.json()

        except httpx.HTTPError as exc:
            raise OllamaProviderError(
                f"Could not communicate with Ollama: {exc}"
            ) from exc

        except ValueError as exc:
            raise OllamaProviderError(
                "Ollama returned an invalid JSON response."
            ) from exc

        if not isinstance(data, dict):
            raise OllamaProviderError(
                "Ollama returned an unexpected response format."
            )

        generated_text = data.get("response")

        if not isinstance(generated_text, str) or not generated_text.strip():
            raise OllamaProviderError(
                "Ollama returned an empty or invalid response."
            )

        return generated_text.strip()
