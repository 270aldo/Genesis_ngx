"""Tests para el agente ATLAS."""

from __future__ import annotations

from agents.atlas.agent import (
    atlas,
    root_agent,
    get_status,
    generate_routine,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuracion del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert atlas is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert atlas.name == "atlas"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash (no Pro)."""
        assert "flash" in atlas.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert atlas.tools is not None
        assert len(atlas.tools) > 0

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert atlas.instruction is not None
        assert len(atlas.instruction) > 100

    def test_root_agent_is_atlas(self):
        """root_agent debe ser atlas."""
        assert root_agent is atlas


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
        assert AGENT_CARD["specialty"] == "mobility_flexibility"

    def test_agent_card_has_assess_mobility_method(self):
        """Agent Card debe exponer metodo assess_mobility."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "assess_mobility" in method_names

    def test_agent_card_has_generate_routine_method(self):
        """Agent Card debe exponer metodo generate_routine."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "generate_routine" in method_names

    def test_agent_card_limits(self):
        """Agent Card debe tener limites apropiados para Flash."""
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
        assert AGENT_CONFIG["specialty"] == "mobility_flexibility"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "mobility_assessment",
            "flexibility_routines",
            "movement_patterns",
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
        """get_status debe incluir numero de ejercicios."""
        status = get_status()
        assert "exercises_available" in status
        assert status["exercises_available"] > 0

    def test_get_status_includes_routines(self):
        """get_status debe incluir rutinas disponibles."""
        status = get_status()
        assert "routines_available" in status
        assert len(status["routines_available"]) > 0


class TestGenerateRoutine:
    """Tests para generate_routine."""

    def test_generate_basic_routine(self):
        """Debe generar una rutina basica."""
        routine = generate_routine(
            focus="full_body",
            duration_minutes=15,
        )
        assert routine["focus"] == "full_body"
        assert "exercises" in routine
        assert len(routine["exercises"]) > 0

    def test_generate_hip_focus_routine(self):
        """Debe generar rutina enfocada en cadera."""
        routine = generate_routine(
            focus="hip_focus",
            duration_minutes=15,
        )
        assert routine["focus"] == "hip_focus"
        # Debe incluir ejercicios de cadera
        joints = [ex["joint"] for ex in routine["exercises"]]
        assert "hip" in joints

    def test_generate_shoulder_focus_routine(self):
        """Debe generar rutina enfocada en hombro."""
        routine = generate_routine(
            focus="shoulder_focus",
            duration_minutes=12,
        )
        assert routine["focus"] == "shoulder_focus"
        # Debe incluir ejercicios de hombro
        joints = [ex["joint"] for ex in routine["exercises"]]
        assert "shoulder" in joints

    def test_routine_includes_notes(self):
        """Rutina debe incluir notas de ejecucion."""
        routine = generate_routine(
            focus="full_body",
            duration_minutes=15,
        )
        assert "notes" in routine
        assert len(routine["notes"]) > 0

    def test_routine_includes_estimated_duration(self):
        """Rutina debe incluir duracion estimada."""
        routine = generate_routine(
            focus="full_body",
            duration_minutes=15,
        )
        assert "estimated_duration_minutes" in routine
        assert routine["estimated_duration_minutes"] > 0
