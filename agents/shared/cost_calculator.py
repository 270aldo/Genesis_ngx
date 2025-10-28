"""Utilidades para calcular costos de Cloud Run y Gemini 2.5."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CostCalculator:
    """Calculadora simple de costos (Octubre 2025)."""

    # Cloud Run (us-central1) precios on-demand
    CLOUD_RUN_VCPU_HOUR: float = 0.0864
    CLOUD_RUN_GIB_HOUR: float = 0.009

    GEMINI_PRICES = {
        "pro": {"input": 1.25, "input_cached": 0.125, "output": 10.0},
        "flash": {"input": 0.30, "input_cached": 0.030, "output": 2.50},
        "flash-lite": {"input": 0.10, "input_cached": 0.010, "output": 0.40},
    }

    def calculate_cloud_run_cost(self, vcpu_hours: float, gib_hours: float) -> float:
        cpu_cost = vcpu_hours * self.CLOUD_RUN_VCPU_HOUR
        mem_cost = gib_hours * self.CLOUD_RUN_GIB_HOUR
        return round(cpu_cost + mem_cost, 4)

    def calculate_gemini_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> float:
        if model not in self.GEMINI_PRICES:
            raise ValueError(f"Modelo no soportado: {model}")

        prices = self.GEMINI_PRICES[model]
        uncached = max(input_tokens - cached_tokens, 0)

        cost = (
            (cached_tokens / 1_000_000) * prices["input_cached"]
            + (uncached / 1_000_000) * prices["input"]
            + (output_tokens / 1_000_000) * prices["output"]
        )
        return round(cost, 6)

    @staticmethod
    def estimate_output_tokens(input_tokens: int, ratio: float = 0.4) -> int:
        return int(input_tokens * ratio)
