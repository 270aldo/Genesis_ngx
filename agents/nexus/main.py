"""NEXUS Orchestrator - Entry point.

Este módulo inicializa y ejecuta el agente NEXUS usando Google ADK
y lo expone mediante el protocolo A2A v0.3.
"""

from __future__ import annotations

from typing import Any, Dict

from agents.shared.config import get_settings

from .a2a_wrapper import A2AWrapper
from .agent import root_agent

# Configuración
settings = get_settings()

# Agent Card conforme a A2A v0.3
AGENT_CARD: Dict[str, Any] = {
    "id": "nexus-orchestrator",
    "version": "0.2.0",
    "description": "NEXUS orchestrator para sistema multi-agente de bienestar usando Google ADK",
    "capabilities": [
        "orchestration",
        "intent_classification",
        "consensus",
        "handoff",
        "planning",
        "adk_native",  # Indica que es un agente ADK nativo
    ],
    "limits": {
        "max_input_tokens": 50000,
        "max_output_tokens": 4000,
        "max_latency_ms": 8000,
        "max_cost_per_invoke": 0.05,
    },
    "privacy": {
        "pii": False,
        "phi": False,
        "data_retention_days": 90,
        "notes": "NEXUS no persiste PII/PHI directamente, solo metadata de orquestación",
    },
    "auth": {
        "method": "oidc",
        "audience": "nexus-orchestrator",
        "issuer": settings.auth.oidc_issuer,
    },
    "framework": {
        "name": "Google ADK",
        "version": "0.2.0",
        "model": "gemini-2.5-pro",  # NEXUS usa Pro para síntesis (ADR-004)
    },
}

# Crear wrapper A2A para el agente ADK
wrapper = A2AWrapper(
    agent=root_agent,
    agent_card=AGENT_CARD,
)

# Exponer app FastAPI
app = wrapper.app


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        "agents.nexus.main:app",
        host=settings.service.host,
        port=settings.service.port,
        reload=settings.service.reload,
        log_level=settings.logging.level.value.lower(),
    )
