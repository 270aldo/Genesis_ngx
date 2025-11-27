"""Tests para el agente LOGOS."""

from __future__ import annotations

from agents.logos.agent import (
    logos,
    root_agent,
    get_status,
    quick_explain,
    quick_debunk,
    quick_quiz,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuración del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert logos is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert logos.name == "logos"

    def test_agent_model_is_pro(self):
        """El agente debe usar modelo Pro (NO Flash)."""
        assert "pro" in logos.model.lower()
        assert "flash" not in logos.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert logos.tools is not None
        assert len(logos.tools) > 0

    def test_agent_has_5_tools(self):
        """El agente debe tener exactamente 5 tools."""
        assert len(logos.tools) == 5

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert logos.instruction is not None
        assert len(logos.instruction) > 100

    def test_root_agent_is_logos(self):
        """root_agent debe ser logos."""
        assert root_agent is logos

    def test_agent_output_key(self):
        """El agente debe tener output_key definido."""
        assert logos.output_key == "logos_response"

    def test_agent_description_mentions_education(self):
        """La descripción debe mencionar educación."""
        desc_lower = logos.description.lower()
        assert "educa" in desc_lower or "explica" in desc_lower


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
        """Agent Card debe indicar dominio education."""
        assert AGENT_CARD["domain"] == "education"
        assert AGENT_CARD["specialty"] == "learning_knowledge"

    def test_agent_card_has_explain_concept_method(self):
        """Agent Card debe exponer método explain_concept."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "explain_concept" in method_names

    def test_agent_card_has_present_evidence_method(self):
        """Agent Card debe exponer método present_evidence."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "present_evidence" in method_names

    def test_agent_card_has_debunk_myth_method(self):
        """Agent Card debe exponer método debunk_myth."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "debunk_myth" in method_names

    def test_agent_card_has_create_deep_dive_method(self):
        """Agent Card debe exponer método create_deep_dive."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "create_deep_dive" in method_names

    def test_agent_card_has_generate_quiz_method(self):
        """Agent Card debe exponer método generate_quiz."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "generate_quiz" in method_names

    def test_agent_card_has_5_methods(self):
        """Agent Card debe exponer exactamente 5 métodos."""
        assert len(AGENT_CARD["methods"]) == 5

    def test_agent_card_limits_are_pro_tier(self):
        """Agent Card debe tener límites de tier Pro (mayores que Flash)."""
        limits = AGENT_CARD["limits"]
        # Pro tiene límites más altos que Flash
        assert limits["max_latency_ms"] == 6000  # Flash es 2000
        assert limits["max_cost_per_invoke"] == 0.05  # Flash es 0.01
        assert limits["max_input_tokens"] == 50000  # Flash es ~20000
        assert limits["max_output_tokens"] == 4000  # Flash es ~2000

    def test_agent_card_privacy(self):
        """Agent Card debe indicar que NO maneja PHI/PII."""
        privacy = AGENT_CARD["privacy"]
        assert privacy["pii"] is False
        assert privacy["phi"] is False

    def test_agent_card_auth(self):
        """Agent Card debe tener auth configurado."""
        auth = AGENT_CARD["auth"]
        assert auth["method"] == "bearer"
        assert auth["audience"] == "genesis-ngx"


class TestAgentConfig:
    """Tests para AGENT_CONFIG."""

    def test_agent_config_domain(self):
        """AGENT_CONFIG debe tener domain=education."""
        assert AGENT_CONFIG["domain"] == "education"

    def test_agent_config_specialty(self):
        """AGENT_CONFIG debe tener specialty correcta."""
        assert AGENT_CONFIG["specialty"] == "learning_knowledge"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "concept_explanation",
            "evidence_presentation",
            "myth_debunking",
            "deep_dives",
            "quiz_generation",
        ]
        for cap in required_capabilities:
            assert cap in AGENT_CONFIG["capabilities"]

    def test_agent_config_model_tier_is_pro(self):
        """AGENT_CONFIG debe indicar model_tier=pro."""
        assert AGENT_CONFIG["model_tier"] == "pro"

    def test_agent_config_thinking_level_is_high(self):
        """AGENT_CONFIG debe indicar thinking_level=high."""
        assert AGENT_CONFIG["thinking_level"] == "high"

    def test_agent_config_has_personality(self):
        """AGENT_CONFIG debe tener personalidad socrática."""
        personality = AGENT_CONFIG["personality"]
        assert "socrático" in personality["style"].lower() or "socrat" in personality["style"].lower()


class TestGetStatus:
    """Tests para get_status."""

    def test_get_status_returns_healthy(self):
        """get_status debe retornar status=healthy."""
        status = get_status()
        assert status["status"] == "healthy"

    def test_get_status_includes_agent(self):
        """get_status debe indicar agente logos."""
        status = get_status()
        assert status["agent"] == "logos"

    def test_get_status_includes_version(self):
        """get_status debe incluir versión."""
        status = get_status()
        assert "version" in status
        assert status["version"] == AGENT_CARD["version"]

    def test_get_status_indicates_pro_model(self):
        """get_status debe indicar modelo Pro."""
        status = get_status()
        assert "model" in status
        assert "pro" in status["model"].lower()

    def test_get_status_indicates_pro_tier(self):
        """get_status debe indicar tier Pro."""
        status = get_status()
        assert status["model_tier"] == "pro"

    def test_get_status_indicates_high_thinking(self):
        """get_status debe indicar thinking_level high."""
        status = get_status()
        assert status["thinking_level"] == "high"

    def test_get_status_includes_capabilities(self):
        """get_status debe incluir capacidades."""
        status = get_status()
        assert "capabilities" in status
        assert len(status["capabilities"]) == 5

    def test_get_status_includes_content_stats(self):
        """get_status debe incluir estadísticas de contenido."""
        status = get_status()
        assert "content_stats" in status
        stats = status["content_stats"]
        assert stats["concepts"] > 0
        assert stats["evidence_topics"] > 0
        assert stats["myths"] > 0
        assert stats["learning_levels"] == 3

    def test_get_status_includes_domains_covered(self):
        """get_status debe incluir dominios cubiertos."""
        status = get_status()
        assert "domains_covered" in status
        assert len(status["domains_covered"]) >= 4  # fitness, nutrition, behavior, recovery, womens_health


class TestQuickExplain:
    """Tests para quick_explain helper."""

    def test_quick_explain_basic(self):
        """Debe explicar un concepto básico."""
        result = quick_explain(concept="progressive_overload")
        assert result["status"] == "explained"
        assert "definition" in result

    def test_quick_explain_with_level(self):
        """Debe respetar nivel de usuario."""
        result = quick_explain(concept="hypertrophy", level="beginner")
        assert result["status"] == "explained"
        assert result["user_level"] == "beginner"

    def test_quick_explain_not_found(self):
        """Debe manejar concepto no encontrado."""
        result = quick_explain(concept="concepto_inventado_xyz")
        assert result["status"] == "not_found"


class TestQuickDebunk:
    """Tests para quick_debunk helper."""

    def test_quick_debunk_basic(self):
        """Debe desmentir un mito básico."""
        result = quick_debunk(myth="spot_reduction")
        assert result["status"] == "debunked"
        assert "truth" in result

    def test_quick_debunk_not_found(self):
        """Debe manejar mito no encontrado."""
        result = quick_debunk(myth="mito_inventado_xyz")
        assert result["status"] == "not_found"


class TestQuickQuiz:
    """Tests para quick_quiz helper."""

    def test_quick_quiz_basic(self):
        """Debe generar un quiz básico."""
        result = quick_quiz(topic="nutrition_basics")
        assert result["status"] == "generated"
        assert "quiz" in result

    def test_quick_quiz_with_num_questions(self):
        """Debe respetar número de preguntas."""
        result = quick_quiz(topic="training_fundamentals", num_questions=2)
        assert result["status"] == "generated"
        assert result["num_questions"] <= 2


class TestAgentIntegration:
    """Tests de integración para verificar coherencia del agente."""

    def test_agent_card_methods_match_tools(self):
        """Los métodos del Agent Card deben corresponder a las tools."""
        method_names = {m["name"] for m in AGENT_CARD["methods"]}
        expected_methods = {
            "explain_concept",
            "present_evidence",
            "debunk_myth",
            "create_deep_dive",
            "generate_quiz",
        }
        assert method_names == expected_methods

    def test_agent_config_capabilities_count(self):
        """AGENT_CONFIG debe tener 5 capabilities."""
        assert len(AGENT_CONFIG["capabilities"]) == 5

    def test_agent_description_mentions_key_functions(self):
        """La descripción del agente debe mencionar funciones clave."""
        desc_lower = logos.description.lower()
        # Debe mencionar al menos 2 de las funciones principales
        keywords = ["explica", "concepto", "evidencia", "mito", "educa"]
        matches = sum(1 for kw in keywords if kw in desc_lower)
        assert matches >= 2

    def test_get_status_consistency(self):
        """get_status debe ser consistente con AGENT_CARD."""
        status = get_status()
        assert status["version"] == AGENT_CARD["version"]
        assert set(status["capabilities"]) == set(AGENT_CONFIG["capabilities"])

    def test_pro_vs_flash_distinction(self):
        """LOGOS debe ser claramente distinto de agentes Flash."""
        # Verificar que los límites son de Pro, no Flash
        limits = AGENT_CARD["limits"]

        # Flash limits son: 2000ms latency, $0.01 cost
        # Pro limits son: 6000ms latency, $0.05 cost
        assert limits["max_latency_ms"] > 2000, "LOGOS debe tener latency de Pro"
        assert limits["max_cost_per_invoke"] > 0.01, "LOGOS debe tener cost de Pro"

        # Verificar modelo
        assert "pro" in logos.model.lower(), "LOGOS debe usar modelo Pro"
        assert AGENT_CONFIG["model_tier"] == "pro"
        assert AGENT_CONFIG["thinking_level"] == "high"
