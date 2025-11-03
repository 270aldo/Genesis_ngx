"""Tests para cost_calculator."""

import pytest

from agents.shared.cost_calculator import CostCalculator


@pytest.fixture
def calculator():
    """Fixture para CostCalculator."""
    return CostCalculator()


class TestCostCalculator:
    """Tests para CostCalculator."""

    def test_calculate_cloud_run_cost(self, calculator):
        """Test cálculo de costo de Cloud Run."""
        # 1 vCPU-hour + 1 GiB-hour
        cost = calculator.calculate_cloud_run_cost(vcpu_hours=1.0, gib_hours=1.0)
        expected = (1.0 * 0.0864) + (1.0 * 0.009)
        assert cost == pytest.approx(expected, abs=0.0001)

    def test_calculate_gemini_cost_pro(self, calculator):
        """Test cálculo de costo de Gemini Pro."""
        cost = calculator.calculate_gemini_cost(
            model="pro",
            input_tokens=1_000_000,  # 1M input
            output_tokens=1_000_000,  # 1M output
            cached_tokens=0,
        )
        # Pro: $1.25 input + $10.00 output = $11.25
        assert cost == pytest.approx(11.25, abs=0.01)

    def test_calculate_gemini_cost_flash(self, calculator):
        """Test cálculo de costo de Gemini Flash."""
        cost = calculator.calculate_gemini_cost(
            model="flash",
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            cached_tokens=0,
        )
        # Flash: $0.30 input + $2.50 output = $2.80
        assert cost == pytest.approx(2.80, abs=0.01)

    def test_calculate_gemini_cost_with_caching(self, calculator):
        """Test cálculo con caching."""
        cost = calculator.calculate_gemini_cost(
            model="flash",
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            cached_tokens=500_000,  # 50% cached
        )
        # 500k cached @ $0.030 + 500k normal @ $0.30 + 1M output @ $2.50
        # = $0.015 + $0.15 + $2.50 = $2.665
        assert cost == pytest.approx(2.665, abs=0.01)

    def test_calculate_gemini_cost_flash_lite(self, calculator):
        """Test cálculo de Gemini Flash-Lite."""
        cost = calculator.calculate_gemini_cost(
            model="flash-lite",
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            cached_tokens=0,
        )
        # Flash-Lite: $0.10 input + $0.40 output = $0.50
        assert cost == pytest.approx(0.50, abs=0.01)

    def test_calculate_gemini_cost_invalid_model(self, calculator):
        """Test con modelo inválido."""
        with pytest.raises(ValueError, match="Modelo no soportado"):
            calculator.calculate_gemini_cost(
                model="invalid",
                input_tokens=1000,
                output_tokens=1000,
            )

    def test_estimate_output_tokens(self):
        """Test estimación de tokens de salida."""
        estimated = CostCalculator.estimate_output_tokens(input_tokens=1000)
        assert estimated == 400  # 40% por defecto

        estimated = CostCalculator.estimate_output_tokens(input_tokens=1000, ratio=0.5)
        assert estimated == 500

    def test_calculate_gemini_cost_zero_tokens(self, calculator):
        """Test con zero tokens."""
        cost = calculator.calculate_gemini_cost(
            model="flash",
            input_tokens=0,
            output_tokens=0,
            cached_tokens=0,
        )
        assert cost == 0.0

    def test_calculate_gemini_cost_100_percent_cached(self, calculator):
        """Test con 100% de tokens cacheados."""
        cost = calculator.calculate_gemini_cost(
            model="flash",
            input_tokens=1_000_000,
            output_tokens=0,
            cached_tokens=1_000_000,
        )
        # Solo costo de cached: 1M @ $0.030 = $0.03
        assert cost == pytest.approx(0.03, abs=0.001)
