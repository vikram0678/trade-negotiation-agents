
import os

from dotenv import load_dotenv

from providers.base import BaseLLMProvider
from providers.ollama import OllamaProvider


# Load .env for local execution.
# Existing environment variables take precedence.
load_dotenv()


class ProviderConfigurationError(ValueError):
    """Raised when the selected LLM provider is not configured."""


def create_provider() -> BaseLLMProvider:
    provider_name = os.getenv(
        "LLM_PROVIDER", "ollama"
    ).strip().lower()

    if provider_name == "ollama":
        base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://127.0.0.1:11434",
        ).strip()

        model = os.getenv(
            "OLLAMA_MODEL", "llama3:latest"
        ).strip()

        try:
            timeout = float(
                os.getenv("OLLAMA_TIMEOUT", "180")
            )
        except ValueError as exc:
            raise ProviderConfigurationError(
                "OLLAMA_TIMEOUT must be a valid number."
            ) from exc

        if not base_url.startswith(("http://", "https://")):
            raise ProviderConfigurationError(
                "OLLAMA_BASE_URL must be a valid HTTP or HTTPS URL."
            )

        if not model:
            raise ProviderConfigurationError(
                "OLLAMA_MODEL cannot be empty."
            )

        if timeout <= 0:
            raise ProviderConfigurationError(
                "OLLAMA_TIMEOUT must be greater than zero."
            )

        return OllamaProvider(
            base_url=base_url,
            model=model,
            timeout=timeout,
        )

    if provider_name == "openai_compatible":
        raise ProviderConfigurationError(
            "The OpenAI-compatible provider has not been implemented yet."
        )

    if provider_name == "host_agent":
        raise ProviderConfigurationError(
            "The host-agent adapter has not been implemented yet."
        )

    raise ProviderConfigurationError(
        f"Unsupported LLM_PROVIDER: {provider_name}"
    )
