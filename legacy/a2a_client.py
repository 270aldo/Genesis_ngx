"""Cliente A2A v0.3 con soporte para JSON-RPC y SSE."""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, Optional

import httpx
from tenacity import (RetryCallState, retry, retry_if_exception_type,
                      stop_after_attempt, wait_exponential_jitter)


class A2AError(RuntimeError):
    """Error genérico para fallas A2A."""


class A2ATimeoutError(A2AError):
    """Error para timeouts de invocación."""


class A2ABudgetExceededError(A2AError):
    """El agente reportó que el presupuesto disponible es insuficiente."""


class A2AValidationError(A2AError):
    """Solicitud JSON-RPC inválida."""


def _before_sleep_log(retry_state: RetryCallState) -> None:
    attempt = retry_state.attempt_number
    exc = retry_state.outcome.exception()
    if exc is not None:
        # Logging ligero; en producción conectar con Cloud Logging.
        print(f"[A2AClient] retry attempt {attempt} due to: {exc}")


@dataclass(slots=True)
class A2AClient:
    """Cliente para consumir agentes A2A."""

    base_url: str
    timeout: float = 30.0
    session: Optional[httpx.AsyncClient] = None

    def __post_init__(self) -> None:
        self._client = self.session or httpx.AsyncClient()

    async def close(self) -> None:
        await self._client.aclose()

    async def get_card(self) -> Dict[str, Any]:
        response = await self._client.get(f"{self.base_url}/card", timeout=5.0)
        response.raise_for_status()
        return response.json()

    async def negotiate(self, capabilities: list[str], budget_usd: float) -> Dict[str, Any]:
        payload = {"capabilities": capabilities, "budget_usd": budget_usd}
        response = await self._client.post(
            f"{self.base_url}/negotiate", json=payload, timeout=5.0
        )
        response.raise_for_status()
        return response.json()

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.HTTPError, A2AError)),
        wait=wait_exponential_jitter(initial=1, max=10),
        before_sleep=_before_sleep_log,
    )
    async def invoke(
        self,
        method: str,
        params: Dict[str, Any],
        request_id: Optional[str] = None,
        budget_usd: float = 0.01,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        rid = request_id or uuid.uuid4().hex
        jsonrpc_payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": rid}

        final_headers = {
            "X-Request-ID": rid,
            "X-Budget-USD": f"{budget_usd:.6f}",
            "Content-Type": "application/json",
        }
        if headers:
            final_headers.update(headers)

        try:
            response = await self._client.post(
                f"{self.base_url}/invoke",
                content=json.dumps(jsonrpc_payload),
                headers=final_headers,
                timeout=self.timeout,
            )
        except httpx.TimeoutException as exc:  # pragma: no cover - dependiente de red
            raise A2ATimeoutError("Invoke timeout") from exc

        if response.status_code == 408:
            raise A2ATimeoutError("Agent timed out")

        if response.status_code >= 500:
            raise A2AError(f"Server error {response.status_code}")

        data = response.json()

        if "error" in data:
            reason = data["error"].get("data", {}).get("reason")
            if reason == "BUDGET_EXCEEDED":
                raise A2ABudgetExceededError("Budget insufficient for invocation")
            if reason == "VALIDATION_ERROR":
                raise A2AValidationError(data["error"].get("message", "Invalid request"))
            raise A2AError(data["error"].get("message", "Unknown error"))

        return data

    async def invoke_stream(
        self,
        method: str,
        params: Dict[str, Any],
        request_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 60.0,
    ) -> AsyncGenerator[str, None]:
        rid = request_id or uuid.uuid4().hex
        jsonrpc_payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": rid}

        final_headers = {
            "X-Request-ID": rid,
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
        }
        if headers:
            final_headers.update(headers)

        try:
            async with self._client.stream(
                "POST",
                f"{self.base_url}/invoke/stream",
                content=json.dumps(jsonrpc_payload),
                headers=final_headers,
                timeout=timeout,
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith(":"):
                        continue  # comentarios SSE
                    if line.startswith("data: "):
                        yield line[6:]
        except httpx.TimeoutException as exc:  # pragma: no cover
            raise A2ATimeoutError("Stream timeout") from exc

    async def __aenter__(self) -> "A2AClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()


async def gather_with_concurrency(limit: int, *tasks: Any) -> list[Any]:
    """Ejecuta tareas con límite de concurrencia (útil para orquestación)."""

    semaphore = asyncio.Semaphore(limit)

    async def sem_task(coro: Any) -> Any:
        async with semaphore:
            return await coro

    return await asyncio.gather(*(sem_task(task) for task in tasks))
