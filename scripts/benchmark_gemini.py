"""Benchmark simple para medir costo real y cache hit rate."""

from __future__ import annotations

import asyncio
import random
from typing import List

from vertexai.generative_models import GenerativeModel

from agents.shared.cost_calculator import CostCalculator


async def run_benchmark(iterations: int = 1000) -> None:
    model = GenerativeModel("gemini-2.5-flash")
    calc = CostCalculator()

    cache_hits: List[int] = []
    costs: List[float] = []

    for i in range(iterations):
        prompt = f"Provide a brief wellness tip number {i}: {random.randint(1, 1000)}"
        response = await model.generate_content_async(
            prompt,
            generation_config={"cache_config": {"ttl": "3600s"}},
        )

        usage = response.usage_metadata
        cached_tokens = usage.cached_content_token_count or 0
        prompt_tokens = usage.prompt_token_count or 0
        output_tokens = usage.candidates_token_count or 0

        cost = calc.calculate_gemini_cost(
            "flash",
            prompt_tokens,
            output_tokens,
            cached_tokens,
        )

        cache_hits.append(1 if cached_tokens > 0 else 0)
        costs.append(cost)

    hit_rate = sum(cache_hits) / len(cache_hits)
    avg_cost = sum(costs) / len(costs)

    print(f"Cache hit rate: {hit_rate:.2%}")
    print(f"Costo promedio por request: ${avg_cost:.6f}")


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(run_benchmark())
