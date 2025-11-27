"""Tests para el agente BLAZE."""

from __future__ import annotations

from agents.blaze.agent import (
    blaze,
    root_agent,
    get_status,
    generate_workout,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuración del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert blaze is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert blaze.name == "blaze"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash (no Pro)."""
        assert "flash" in blaze.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert blaze.tools is not None
        assert len(blaze.tools) > 0

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert blaze.instruction is not None
        assert len(blaze.instruction) > 100

    def test_root_agent_is_blaze(self):
        """root_agent debe ser blaze."""
        assert root_agent is blaze


class TestAgentCard:
    """Tests para el Agent Card (A2A)."""

    def test_agent_card_has_required_fields(self):
        """Agent Card debe tener campos requeridos."""
        required_fields = ["name", "description", "version", "protocol", "capabilities", "methods", "limits"]
        for field in required_fields:
            assert field in AGENT_CARD, f"Campo {field} faltante en AGENT_CARD"

    def test_agent_card_protocol(self):
        """Agent Card debe usar protocolo A2A v0.3."""
        assert AGENT_CARD["protocol"] == "a2a/0.3"

    def test_agent_card_has_domain(self):
        """Agent Card debe indicar dominio fitness."""
        assert AGENT_CARD["domain"] == "fitness"
        assert AGENT_CARD["specialty"] == "strength_hypertrophy"

    def test_agent_card_has_generate_workout_method(self):
        """Agent Card debe exponer método generate_workout."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "generate_workout" in method_names

    def test_agent_card_limits(self):
        """Agent Card debe tener límites apropiados para Flash."""
        limits = AGENT_CARD["limits"]
        assert limits["max_latency_ms"] == 2000
        assert limits["max_cost_per_invoke"] == 0.01

    def test_agent_card_privacy(self):
        """Agent Card debe indicar que NO maneja PHI/PII."""
        privacy = AGENT_CARD["privacy"]
        assert privacy["pii"] is False
        assert privacy["phi"] is False


class TestAgentConfig:
    """Tests para AGENT_CONFIG."""

    def test_agent_config_domain(self):
        """AGENT_CONFIG debe tener domain=fitness."""
        assert AGENT_CONFIG["domain"] == "fitness"

    def test_agent_config_specialty(self):
        """AGENT_CONFIG debe tener specialty correcta."""
        assert AGENT_CONFIG["specialty"] == "strength_hypertrophy"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "workout_generation",
            "exercise_selection",
            "progressive_overload",
        ]
        for cap in required_capabilities:
            assert cap in AGENT_CONFIG["capabilities"]


class TestGetStatus:
    """Tests para get_status."""

    def test_get_status_returns_healthy(self):
        """get_status debe retornar status=healthy."""
        status = get_status()
        assert status["status"] == "healthy"

    def test_get_status_includes_exercises(self):
        """get_status debe incluir número de ejercicios."""
        status = get_status()
        assert "exercises_available" in status
        assert status["exercises_available"] > 0

    def test_get_status_includes_splits(self):
        """get_status debe incluir splits disponibles."""
        status = get_status()
        assert "splits_available" in status
        assert len(status["splits_available"]) > 0


class TestGenerateWorkout:
    """Tests para generate_workout."""

    def test_generate_basic_workout(self):
        """Debe generar un workout básico."""
        workout = generate_workout(
            user_id="test-user",
            workout_type="hypertrophy",
            muscle_groups=["chest", "triceps"],
        )
        assert workout["user_id"] == "test-user"
        assert workout["workout_type"] == "hypertrophy"
        assert "exercises" in workout
        assert "warmup" in workout
        assert "cooldown" in workout

    def test_generate_strength_workout(self):
        """Debe generar workout de fuerza con parámetros correctos."""
        workout = generate_workout(
            user_id="test-user",
            workout_type="strength",
            muscle_groups=["back"],
        )
        # Strength workouts tienen menos reps
        for ex in workout["exercises"]:
            if "reps" in ex and isinstance(ex["reps"], str):
                assert "3-5" in ex["reps"] or "5" in ex["reps"]

    def test_workout_includes_warmup(self):
        """Workout debe incluir calentamiento."""
        workout = generate_workout(
            user_id="test-user",
            workout_type="hypertrophy",
            muscle_groups=["quadriceps"],
        )
        assert workout["warmup"]["duration_minutes"] >= 5
        assert len(workout["warmup"]["components"]) > 0

    def test_workout_includes_phase_config(self):
        """Workout debe incluir configuración de fase."""
        phase_config = {"volume": "high", "intensity_range": [65, 75]}
        workout = generate_workout(
            user_id="test-user",
            workout_type="hypertrophy",
            muscle_groups=["shoulders"],
            phase_config=phase_config,
        )
        assert workout["phase_config"] == phase_config
