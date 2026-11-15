
from core.engine import NegotiationEngine
from core.models import (
    NegotiationRequest,
    PartyProfile,
)
from providers.ollama import OllamaProvider


def create_request():
    return NegotiationRequest(
        party_a=PartyProfile(
            name="Buyer",
            role="Buyer",
        ),
        party_b=PartyProfile(
            name="Seller",
            role="Seller",
        ),
        topic="Equipment purchase",
        issues=[
            {
                "name": "price",
                "description": "Purchase price",
            }
        ],
    )


def test_engine_uses_ollama_environment_configuration(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv(
        "OLLAMA_BASE_URL",
        "http://test-ollama:11434",
    )
    monkeypatch.setenv("OLLAMA_MODEL", "llama3")

    engine = NegotiationEngine()
    request = create_request()

    provider = engine._default_provider_factory(
        request,
        request.party_a,
    )

    assert isinstance(provider, OllamaProvider)
    assert provider.base_url == "http://test-ollama:11434"
    assert provider.model == "llama3"


def test_engine_uses_custom_model_from_environment(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "custom-model")

    request = create_request()
    engine = NegotiationEngine()

    provider = engine._default_provider_factory(
        request,
        request.party_a,
    )

    assert provider.model == "custom-model"
