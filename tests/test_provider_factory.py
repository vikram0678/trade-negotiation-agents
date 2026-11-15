
import pytest

from providers.factory import (
    create_provider,
    ProviderConfigurationError,
)
from providers.ollama import OllamaProvider


def test_default_provider_is_ollama(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("OLLAMA_MODEL", "custom-model")

    provider = create_provider()

    assert isinstance(provider, OllamaProvider)
    assert provider.model == "custom-model"


def test_ollama_uses_environment_configuration(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv(
        "OLLAMA_BASE_URL",
        "http://test-ollama:11434",
    )
    monkeypatch.setenv("OLLAMA_MODEL", "llama3")

    provider = create_provider()

    assert isinstance(provider, OllamaProvider)
    assert provider.base_url == "http://test-ollama:11434"
    assert provider.model == "llama3"


def test_ollama_model_comes_from_environment(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "custom-model")

    provider = create_provider()

    assert provider.model == "custom-model"


@pytest.mark.parametrize(
    "provider_name",
    ["openai_compatible", "host_agent"],
)
def test_unimplemented_providers_raise_clear_error(
    monkeypatch,
    provider_name,
):
    monkeypatch.setenv("LLM_PROVIDER", provider_name)

    with pytest.raises(ProviderConfigurationError):
        create_provider()


def test_unknown_provider_is_rejected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "unknown")

    with pytest.raises(ProviderConfigurationError):
        create_provider()
