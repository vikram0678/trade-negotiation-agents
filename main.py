
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from core.engine import NegotiationEngine
from core.models import NegotiationRequest
from providers.factory import ProviderConfigurationError

app = FastAPI(
    title="Universal Multi-Agent Negotiation API",
    description="Configurable multi-party negotiation engine",
    version="1.0.0",
)

engine = NegotiationEngine()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Universal Negotiation API",
    }


@app.post("/negotiate")
async def negotiate(request: NegotiationRequest):
    try:
        result = await engine.run(request)
        return result.model_dump(mode="json")

    except ProviderConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Negotiation could not be completed.",
        ) from exc
