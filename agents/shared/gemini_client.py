"""Cliente para Google Gemini 2.5 con soporte para caching y cost control.

Características:
- Soporte para Pro, Flash y Flash-Lite
- Caching automático de system prompts
- Tracking de costos
- Streaming de respuestas
- Reintentos automáticos
- Circuit breaker para presupuesto
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, AsyncGenerator, Optional

import vertexai
from google.cloud import aiplatform
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)
from vertexai.generative_models import (
    Content,
    GenerationConfig,
    GenerativeModel,
    Part,
)

from agents.shared.config import GeminiConfig, get_settings
from agents.shared.cost_calculator import CostCalculator


class GeminiModel(str, Enum):
    """Modelos Gemini disponibles."""

    PRO = "gemini-2.5-pro"
    FLASH = "gemini-2.0-flash-exp"
    FLASH_LITE = "gemini-2.5-flash-lite"


class GeminiError(RuntimeError):
    """Error base para operaciones con Gemini."""


class GeminiQuotaError(GeminiError):
    """Error cuando se excede la cuota o rate limit."""


class GeminiBudgetExceededError(GeminiError):
    """Error cuando se excede el presupuesto."""


@dataclass
class GenerationMetrics:
    """Métricas de una generación."""

    model: str
    prompt_tokens: int
    cached_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario para logging."""
        return {
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "cached_tokens": self.cached_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "latency_ms": round(self.latency_ms, 2),
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class GeminiClient:
    """Cliente asíncrono para Google Gemini."""

    config: GeminiConfig = field(default_factory=lambda: get_settings().gemini)
    cost_calculator: CostCalculator = field(default_factory=CostCalculator)
    _initialized: bool = field(default=False, init=False)
    _daily_cost: float = field(default=0.0, init=False)
    _last_reset: datetime = field(default_factory=datetime.utcnow, init=False)

    def __post_init__(self) -> None:
        """Inicializa Vertex AI."""
        # Verificar si estamos en modo mock
        if get_settings().mock_gemini:
            self._initialized = True
            return

        if not self._initialized:
            vertexai.init(
                project=self.config.project_id,
                location=self.config.location,
            )
            self._initialized = True

    def _check_daily_budget(self, estimated_cost: float) -> None:
        """Verifica si se excede el presupuesto diario."""
        # Reset diario
        now = datetime.utcnow()
        if now - self._last_reset > timedelta(days=1):
            self._daily_cost = 0.0
            self._last_reset = now

        if self._daily_cost + estimated_cost > self.config.daily_budget_usd:
            raise GeminiBudgetExceededError(
                f"Presupuesto diario excedido: ${self._daily_cost:.4f} + "
                f"${estimated_cost:.4f} > ${self.config.daily_budget_usd:.2f}"
            )

    def _get_model_instance(
        self,
        model_name: str,
        system_instruction: Optional[str] = None,
    ) -> GenerativeModel:
        """Crea instancia del modelo con configuración."""
        # En modo mock, no necesitamos el modelo real
        if get_settings().mock_gemini:
            return None  # type: ignore

        return GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
        )

    def _calculate_cost(
        self,
        model_name: str,
        prompt_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> float:
        """Calcula el costo de la generación."""
        # Mapear nombre del modelo a key del cost calculator
        model_key = "pro" if "pro" in model_name else "flash-lite" if "lite" in model_name else "flash"

        return self.cost_calculator.calculate_gemini_cost(
            model=model_key,
            input_tokens=prompt_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
        )

    def _extract_usage_metadata(self, response: Any) -> tuple[int, int, int]:
        """Extrae métricas de uso de la respuesta."""
        usage = getattr(response, "usage_metadata", None)
        if not usage:
            return 0, 0, 0

        prompt_tokens = getattr(usage, "prompt_token_count", 0)
        output_tokens = getattr(usage, "candidates_token_count", 0)
        cached_tokens = getattr(usage, "cached_content_token_count", 0)

        return prompt_tokens, output_tokens, cached_tokens

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(GeminiQuotaError),
        wait=wait_exponential_jitter(initial=2, max=30),
    )
    async def generate(
        self,
        prompt: str,
        model: GeminiModel = GeminiModel.FLASH,
        system_instruction: Optional[str] = None,
        max_output_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40,
        budget_usd: Optional[float] = None,
    ) -> tuple[str, GenerationMetrics]:
        """Genera texto con Gemini.

        Args:
            prompt: Prompt del usuario
            model: Modelo a usar
            system_instruction: Instrucción del sistema (se cachea si es posible)
            max_output_tokens: Máximo de tokens de salida
            temperature: Temperatura de generación
            top_p: Top-p sampling
            top_k: Top-k sampling
            budget_usd: Presupuesto máximo (usa config si es None)

        Returns:
            Tupla de (texto_generado, métricas)

        Raises:
            GeminiBudgetExceededError: Si se excede el presupuesto
            GeminiQuotaError: Si se excede la cuota de API
            GeminiError: Otros errores
        """
        start_time = time.time()

        # Mock Response
        if get_settings().mock_gemini:
            metrics = GenerationMetrics(
                model=model.value,
                prompt_tokens=10,
                cached_tokens=0,
                output_tokens=20,
                total_tokens=30,
                cost_usd=0.0001,
                latency_ms=100.0,
            )
            return f"[MOCK] Respuesta a: {prompt[:50]}...", metrics

        # Estimar costo
        estimated_tokens = len(prompt.split()) * 2  # Aproximación burda
        estimated_cost = self._calculate_cost(
            model_name=model.value,
            prompt_tokens=estimated_tokens,
            output_tokens=max_output_tokens,
        )

        # Verificar presupuesto
        max_budget = budget_usd or self.config.max_cost_per_request
        if estimated_cost > max_budget:
            raise GeminiBudgetExceededError(
                f"Costo estimado ${estimated_cost:.6f} excede presupuesto ${max_budget:.6f}"
            )

        self._check_daily_budget(estimated_cost)

        # Crear modelo
        model_instance = self._get_model_instance(
            model_name=model.value,
            system_instruction=system_instruction,
        )

        # Configuración de generación
        generation_config = GenerationConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
        )

        try:
            # Generar (ejecutar en thread pool ya que es sync)
            response = await asyncio.to_thread(
                model_instance.generate_content,
                prompt,
                generation_config=generation_config,
            )

            # Extraer texto
            text = response.text if hasattr(response, "text") else ""

            # Extraer métricas
            prompt_tokens, output_tokens, cached_tokens = self._extract_usage_metadata(
                response
            )

            # Calcular costo real
            actual_cost = self._calculate_cost(
                model_name=model.value,
                prompt_tokens=prompt_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
            )

            # Actualizar presupuesto diario
            self._daily_cost += actual_cost

            # Latencia
            latency_ms = (time.time() - start_time) * 1000

            metrics = GenerationMetrics(
                model=model.value,
                prompt_tokens=prompt_tokens,
                cached_tokens=cached_tokens,
                output_tokens=output_tokens,
                total_tokens=prompt_tokens + output_tokens,
                cost_usd=actual_cost,
                latency_ms=latency_ms,
            )

            return text, metrics

        except Exception as exc:
            # Clasificar errores
            error_msg = str(exc).lower()
            if "quota" in error_msg or "rate limit" in error_msg:
                raise GeminiQuotaError(f"Quota excedida: {exc}") from exc
            raise GeminiError(f"Error generando con Gemini: {exc}") from exc

    async def generate_stream(
        self,
        prompt: str,
        model: GeminiModel = GeminiModel.FLASH,
        system_instruction: Optional[str] = None,
        max_output_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40,
    ) -> AsyncGenerator[str, None]:
        """Genera texto con streaming.

        Args:
            prompt: Prompt del usuario
            model: Modelo a usar
            system_instruction: Instrucción del sistema
            max_output_tokens: Máximo de tokens de salida
            temperature: Temperatura
            top_p: Top-p sampling
            top_k: Top-k sampling

        Yields:
            Chunks de texto a medida que se generan
        """
        # Mock Stream
        if get_settings().mock_gemini:
            chunks = ["[MOCK] ", "Stream ", "Respuesta ", "a: ", prompt[:20] + "..."]
            for chunk in chunks:
                yield chunk
                await asyncio.sleep(0.1)
            return

        # Crear modelo
        model_instance = self._get_model_instance(
            model_name=model.value,
            system_instruction=system_instruction,
        )

        # Configuración
        generation_config = GenerationConfig(
            max_output_tokens=max_output_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
        )

        try:
            # Stream (ejecutar en thread pool)
            response_stream = await asyncio.to_thread(
                model_instance.generate_content,
                prompt,
                generation_config=generation_config,
                stream=True,
            )

            # Iterar sobre chunks
            for chunk in response_stream:
                if hasattr(chunk, "text") and chunk.text:
                    yield chunk.text

        except Exception as exc:
            error_msg = str(exc).lower()
            if "quota" in error_msg or "rate limit" in error_msg:
                raise GeminiQuotaError(f"Quota excedida: {exc}") from exc
            raise GeminiError(f"Error en streaming: {exc}") from exc

    async def classify_intent(
        self,
        message: str,
        possible_intents: list[str],
    ) -> tuple[str, float]:
        """Clasifica el intent de un mensaje usando Flash-Lite.

        Args:
            message: Mensaje del usuario
            possible_intents: Lista de intents posibles

        Returns:
            Tupla de (intent, confidence)
        """
        intents_str = ", ".join(possible_intents)
        prompt = f"""Clasifica el siguiente mensaje en uno de estos intents: {intents_str}

Mensaje: "{message}"

Responde SOLO con el nombre del intent y un score de confianza (0-1) en formato: intent|confidence
Ejemplo: check_in|0.95"""

        text, _ = await self.generate(
            prompt=prompt,
            model=GeminiModel.FLASH_LITE,
            max_output_tokens=50,
            temperature=0.1,  # Baja temperatura para clasificación
        )

        # Parse respuesta
        try:
            parts = text.strip().split("|")
            intent = parts[0].strip()
            confidence = float(parts[1].strip()) if len(parts) > 1 else 0.8
            return intent, confidence
        except Exception:
            # Fallback
            return possible_intents[0] if possible_intents else "unknown", 0.5


# Instancia global (lazy initialization)
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Obtiene la instancia global del cliente Gemini."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
