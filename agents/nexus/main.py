"""POC de NEXUS orquestador exponiendo API A2A."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict

from agents.shared.a2a_server import A2AServer


AGENT_CARD: Dict[str, Any] = {
    "id": "nexus-orchestrator",
    "version": "0.1.0",
    "capabilities": ["orchestration", "intent_classification", "consensus"],
    "limits": {
        "max_input_tokens": 50000,
        "max_output_tokens": 2000,
        "max_latency_ms": 6000,
        "max_cost_per_invoke": 0.05,
    },
    "privacy": {"pii": False, "phi": False, "data_retention_days": 90},
    "auth": {"method": "oidc", "audience": "nexus-orchestrator"},
}


class NexusAgent(A2AServer):
    def __init__(self) -> None:
        super().__init__(AGENT_CARD)

    async def negotiate_capabilities(self, request):
        missing = [cap for cap in request.capabilities if cap not in AGENT_CARD["capabilities"]]
        if missing:
            return {"accepted": False, "missing_capabilities": missing}
        return {"accepted": True, "limitations": {}}

    async def handle_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if method == "classify_intent":
            message = params.get("message", "")
            intent = "check_in" if "cómo" in message.lower() else "general_inquiry"
            return {"intent": intent, "confidence": 0.85}

        if method == "echo":
            return {"echo": params}

        return {"status": "unknown_method", "method": method}

    async def handle_stream(
        self, method: str, params: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        if method != "plan":
            yield "method_not_supported"
            return

        steps = params.get("steps", ["analyze", "recommend", "summarize"])
        for step in steps:
            yield f"processing:{step}"


agent = NexusAgent()
app = agent.app


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("agents.nexus.main:app", host="0.0.0.0", port=8080, reload=True)
