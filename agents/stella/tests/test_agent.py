"""Tests para el agente STELLA."""

from __future__ import annotations

from agents.stella.agent import (
    stella,
    root_agent,
    get_status,
    analyze_user_progress,
    generate_user_report,
    AGENT_CARD,
    AGENT_CONFIG,
)


class TestAgentConfiguration:
    """Tests para la configuracion del agente."""

    def test_agent_exists(self):
        """El agente debe existir."""
        assert stella is not None

    def test_agent_name(self):
        """El agente debe tener el nombre correcto."""
        assert stella.name == "stella"

    def test_agent_model_is_flash(self):
        """El agente debe usar modelo Flash (no Pro)."""
        assert "flash" in stella.model.lower()

    def test_agent_has_tools(self):
        """El agente debe tener tools definidas."""
        assert stella.tools is not None
        assert len(stella.tools) > 0

    def test_agent_has_instruction(self):
        """El agente debe tener instruction (system prompt)."""
        assert stella.instruction is not None
        assert len(stella.instruction) > 100

    def test_root_agent_is_stella(self):
        """root_agent debe ser stella."""
        assert root_agent is stella


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
        """Agent Card debe indicar dominio analytics."""
        assert AGENT_CARD["domain"] == "analytics"
        assert AGENT_CARD["specialty"] == "data_visualization"

    def test_agent_card_has_analyze_progress_method(self):
        """Agent Card debe exponer metodo analyze_progress."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "analyze_progress" in method_names

    def test_agent_card_has_calculate_trends_method(self):
        """Agent Card debe exponer metodo calculate_trends."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "calculate_trends" in method_names

    def test_agent_card_has_check_goal_status_method(self):
        """Agent Card debe exponer metodo check_goal_status."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "check_goal_status" in method_names

    def test_agent_card_has_interpret_biomarkers_method(self):
        """Agent Card debe exponer metodo interpret_biomarkers."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "interpret_biomarkers" in method_names

    def test_agent_card_has_generate_report_method(self):
        """Agent Card debe exponer metodo generate_report."""
        method_names = [m["name"] for m in AGENT_CARD["methods"]]
        assert "generate_report" in method_names

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
        """AGENT_CONFIG debe tener domain=analytics."""
        assert AGENT_CONFIG["domain"] == "analytics"

    def test_agent_config_specialty(self):
        """AGENT_CONFIG debe tener specialty correcta."""
        assert AGENT_CONFIG["specialty"] == "data_visualization"

    def test_agent_config_capabilities(self):
        """AGENT_CONFIG debe tener capabilities requeridas."""
        required_capabilities = [
            "progress_tracking",
            "trend_analysis",
            "goal_monitoring",
            "biomarker_interpretation",
            "report_generation",
        ]
        for cap in required_capabilities:
            assert cap in AGENT_CONFIG["capabilities"]


class TestGetStatus:
    """Tests para get_status."""

    def test_get_status_returns_healthy(self):
        """get_status debe retornar status=healthy."""
        status = get_status()
        assert status["status"] == "healthy"

    def test_get_status_includes_metric_categories(self):
        """get_status debe incluir categorias de metricas."""
        status = get_status()
        assert "metric_categories" in status
        assert len(status["metric_categories"]) > 0

    def test_get_status_includes_biomarkers(self):
        """get_status debe incluir biomarcadores soportados."""
        status = get_status()
        assert "biomarkers_supported" in status
        assert len(status["biomarkers_supported"]) > 0

    def test_get_status_includes_goal_templates(self):
        """get_status debe incluir templates de metas."""
        status = get_status()
        assert "goal_templates" in status
        assert len(status["goal_templates"]) > 0


class TestAnalyzeUserProgress:
    """Tests para analyze_user_progress."""

    def test_analyze_basic_progress(self):
        """Debe analizar progreso basico."""
        result = analyze_user_progress(
            metric_values=[80.0, 79.5, 79.0, 78.5, 78.0],
            metric_name="weight_kg",
            period_days=30,
        )
        assert result["metric_name"] == "weight_kg"
        assert result["status"] == "analyzed"
        assert "change" in result

    def test_analyze_progress_with_goal(self):
        """Debe analizar progreso con meta."""
        result = analyze_user_progress(
            metric_values=[100.0, 120.0, 140.0],
            metric_name="1rm_squat",
            goal_value=150.0,
        )
        assert result["goal_analysis"] is not None
        assert "progress_percent" in result["goal_analysis"]

    def test_analyze_progress_insufficient_data(self):
        """Debe manejar datos insuficientes."""
        result = analyze_user_progress(
            metric_values=[80.0],
            metric_name="weight_kg",
        )
        assert result["status"] == "insufficient_data"


class TestGenerateUserReport:
    """Tests para generate_user_report."""

    def test_generate_weekly_report(self):
        """Debe generar reporte semanal."""
        result = generate_user_report(
            report_type="weekly",
            metrics_data={"weight_kg": [80.0, 79.5, 79.0]},
            user_name="Test User",
        )
        assert result["report_type"] == "weekly"
        assert result["user_name"] == "Test User"
        assert "executive_summary" in result

    def test_generate_monthly_report(self):
        """Debe generar reporte mensual."""
        result = generate_user_report(
            report_type="monthly",
            metrics_data={"weight_kg": [80.0, 79.0, 78.0, 77.0]},
        )
        assert result["report_type"] == "monthly"
        assert "period" in result

    def test_report_includes_metrics_summary(self):
        """Reporte debe incluir resumen de metricas."""
        result = generate_user_report(
            report_type="weekly",
            metrics_data={"weight_kg": [80.0, 79.0], "body_fat_pct": [20.0, 19.5]},
        )
        assert "metrics_summary" in result
        assert result["metrics_summary"]["total_tracked"] == 2

    def test_report_includes_action_items(self):
        """Reporte debe incluir items de accion."""
        result = generate_user_report(report_type="weekly")
        assert "action_items" in result
        assert len(result["action_items"]) > 0
