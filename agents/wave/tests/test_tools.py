"""Tests para las tools de WAVE."""

from __future__ import annotations

from agents.wave.tools import (
    assess_recovery_status,
    generate_recovery_protocol,
    recommend_deload,
    calculate_sleep_needs,
    RECOVERY_TECHNIQUES,
    DELOAD_PROTOCOLS,
)


class TestAssessRecoveryStatus:
    """Tests para assess_recovery_status."""

    def test_excellent_recovery(self):
        """Debe detectar excelente recuperacion."""
        result = assess_recovery_status(
            sleep_quality=5,
            sleep_hours=8.0,
            muscle_soreness=1,
            energy_level=5,
            motivation=5,
        )
        assert result["fatigue_level"] == "low"
        assert result["ready_to_train"] is True

    def test_poor_recovery(self):
        """Debe detectar pobre recuperacion."""
        result = assess_recovery_status(
            sleep_quality=2,
            sleep_hours=5.0,
            muscle_soreness=5,
            energy_level=2,
            motivation=2,
        )
        assert result["fatigue_level"] in ["high", "severe"]
        assert result["ready_to_train"] is False

    def test_moderate_recovery(self):
        """Debe detectar recuperacion moderada."""
        result = assess_recovery_status(
            sleep_quality=3,
            sleep_hours=7.0,
            muscle_soreness=3,
            energy_level=3,
            motivation=3,
        )
        assert result["fatigue_level"] == "moderate"
        assert result["ready_to_train"] is True

    def test_elevated_hr_affects_score(self):
        """FC elevada debe afectar el score."""
        normal = assess_recovery_status(
            sleep_quality=4,
            sleep_hours=7.5,
            muscle_soreness=2,
            energy_level=4,
            motivation=4,
            resting_hr_elevated=False,
        )
        elevated = assess_recovery_status(
            sleep_quality=4,
            sleep_hours=7.5,
            muscle_soreness=2,
            energy_level=4,
            motivation=4,
            resting_hr_elevated=True,
        )
        assert elevated["overall_score"] < normal["overall_score"]

    def test_includes_assessments(self):
        """Debe incluir assessments detallados."""
        result = assess_recovery_status(
            sleep_quality=3,
            sleep_hours=7.0,
            muscle_soreness=3,
            energy_level=3,
            motivation=3,
        )
        assert "assessments" in result
        assert len(result["assessments"]) >= 4

    def test_includes_recommendations(self):
        """Debe incluir recomendaciones."""
        result = assess_recovery_status(
            sleep_quality=2,
            sleep_hours=5.0,
            muscle_soreness=4,
            energy_level=2,
            motivation=2,
        )
        assert "main_recommendation" in result
        assert "specific_recommendations" in result


class TestGenerateRecoveryProtocol:
    """Tests para generate_recovery_protocol."""

    def test_generate_low_fatigue_protocol(self):
        """Debe generar protocolo para fatiga baja."""
        result = generate_recovery_protocol(fatigue_level="low")
        assert result["fatigue_level"] == "low"
        assert "protocol_techniques" in result

    def test_generate_high_fatigue_protocol(self):
        """Debe generar protocolo para fatiga alta."""
        result = generate_recovery_protocol(fatigue_level="high")
        assert result["fatigue_level"] == "high"
        # Alta fatiga debe priorizar sueno
        technique_ids = [t["technique_id"] for t in result["protocol_techniques"]]
        assert "sleep_optimization" in technique_ids or "hydration_protocol" in technique_ids

    def test_generate_severe_fatigue_protocol(self):
        """Debe generar protocolo para fatiga severa."""
        result = generate_recovery_protocol(fatigue_level="severe")
        assert result["fatigue_level"] == "severe"

    def test_respects_time_available(self):
        """Debe respetar tiempo disponible."""
        result = generate_recovery_protocol(
            fatigue_level="moderate",
            time_available_minutes=20,
        )
        assert result["total_duration_minutes"] <= 20

    def test_respects_equipment(self):
        """Debe respetar disponibilidad de equipo."""
        with_equipment = generate_recovery_protocol(
            fatigue_level="moderate",
            has_equipment=True,
        )
        without_equipment = generate_recovery_protocol(
            fatigue_level="moderate",
            has_equipment=False,
        )
        # Sin equipo no debe incluir foam rolling
        tech_ids_without = [t["technique_id"] for t in without_equipment["protocol_techniques"]]
        assert "foam_rolling" not in tech_ids_without

    def test_includes_sleep_recommendations(self):
        """Debe incluir recomendaciones de sueno."""
        result = generate_recovery_protocol(fatigue_level="moderate")
        assert "sleep_recommendations" in result
        assert len(result["sleep_recommendations"]) > 0


class TestRecommendDeload:
    """Tests para recommend_deload."""

    def test_no_deload_needed_early(self):
        """No debe recomendar deload si pocas semanas."""
        result = recommend_deload(
            weeks_training=3,
            current_fatigue="low",
        )
        assert result["needs_deload"] is False

    def test_deload_after_6_weeks(self):
        """Debe recomendar deload despues de 6 semanas."""
        result = recommend_deload(
            weeks_training=7,
            current_fatigue="moderate",
        )
        assert result["needs_deload"] is True

    def test_deload_for_high_fatigue(self):
        """Debe recomendar deload para fatiga alta."""
        result = recommend_deload(
            weeks_training=4,
            current_fatigue="high",
        )
        assert result["needs_deload"] is True

    def test_deload_for_severe_fatigue(self):
        """Debe recomendar descanso activo para fatiga severa."""
        result = recommend_deload(
            weeks_training=4,
            current_fatigue="severe",
        )
        assert result["needs_deload"] is True
        assert result["recommended_protocol"] == "active_rest"

    def test_deload_protocol_details(self):
        """Debe incluir detalles del protocolo."""
        result = recommend_deload(
            weeks_training=7,
            current_fatigue="moderate",
        )
        assert "protocol_details" in result
        assert "name" in result["protocol_details"]
        assert "duration_weeks" in result["protocol_details"]

    def test_includes_post_deload_tips(self):
        """Debe incluir consejos post-deload."""
        result = recommend_deload(
            weeks_training=7,
            current_fatigue="moderate",
        )
        assert "post_deload_tips" in result


class TestCalculateSleepNeeds:
    """Tests para calculate_sleep_needs."""

    def test_younger_needs_more_sleep(self):
        """Jovenes necesitan mas sueno."""
        young = calculate_sleep_needs(age=25)
        old = calculate_sleep_needs(age=55)
        assert young["recommended_sleep"]["optimal_hours"] > old["recommended_sleep"]["optimal_hours"]

    def test_high_training_volume_needs_more_sleep(self):
        """Alto volumen de entrenamiento necesita mas sueno."""
        low = calculate_sleep_needs(age=35, training_volume="low")
        high = calculate_sleep_needs(age=35, training_volume="high")
        assert high["recommended_sleep"]["optimal_hours"] > low["recommended_sleep"]["optimal_hours"]

    def test_high_stress_needs_more_sleep(self):
        """Alto estres necesita mas sueno."""
        low = calculate_sleep_needs(age=35, stress_level="low")
        high = calculate_sleep_needs(age=35, stress_level="high")
        assert high["recommended_sleep"]["optimal_hours"] > low["recommended_sleep"]["optimal_hours"]

    def test_muscle_building_needs_more_sleep(self):
        """Construccion muscular necesita mas sueno."""
        general = calculate_sleep_needs(age=35, goals="general_fitness")
        muscle = calculate_sleep_needs(age=35, goals="muscle_building")
        assert muscle["recommended_sleep"]["optimal_hours"] > general["recommended_sleep"]["optimal_hours"]

    def test_includes_schedule_examples(self):
        """Debe incluir ejemplos de horarios."""
        result = calculate_sleep_needs(age=35)
        assert "schedule_examples" in result
        assert len(result["schedule_examples"]) > 0
        for example in result["schedule_examples"]:
            assert "wake_time" in example
            assert "bed_time" in example

    def test_includes_quality_tips(self):
        """Debe incluir consejos de calidad."""
        result = calculate_sleep_needs(age=35)
        assert "quality_tips" in result
        assert len(result["quality_tips"]) > 0

    def test_includes_poor_sleep_signs(self):
        """Debe incluir senales de mal sueno."""
        result = calculate_sleep_needs(age=35)
        assert "signs_of_poor_sleep" in result
        assert len(result["signs_of_poor_sleep"]) > 0


class TestRecoveryTechniquesIntegrity:
    """Tests para integridad de las tecnicas de recuperacion."""

    def test_all_techniques_have_required_fields(self):
        """Todas las tecnicas deben tener campos requeridos."""
        required_fields = ["name_es", "type", "frequency", "techniques"]
        for tech_id, tech_data in RECOVERY_TECHNIQUES.items():
            for field in required_fields:
                assert field in tech_data, f"Tecnica {tech_id} falta campo {field}"

    def test_valid_types(self):
        """Todos los tipos deben ser validos."""
        valid_types = {"sleep", "active_recovery", "passive_recovery", "nutrition"}
        for tech_id, tech_data in RECOVERY_TECHNIQUES.items():
            assert tech_data["type"] in valid_types, f"Tipo invalido en {tech_id}"

    def test_techniques_have_details(self):
        """Todas las tecnicas deben tener detalles."""
        for tech_id, tech_data in RECOVERY_TECHNIQUES.items():
            assert len(tech_data["techniques"]) > 0, f"Tecnica {tech_id} sin detalles"


class TestDeloadProtocolsIntegrity:
    """Tests para integridad de los protocolos de deload."""

    def test_all_protocols_have_required_fields(self):
        """Todos los protocolos deben tener campos requeridos."""
        required_fields = ["name_es", "description", "duration_weeks", "best_for"]
        for protocol_id, protocol_data in DELOAD_PROTOCOLS.items():
            for field in required_fields:
                assert field in protocol_data, f"Protocolo {protocol_id} falta campo {field}"

    def test_valid_durations(self):
        """Todas las duraciones deben ser validas."""
        for protocol_id, protocol_data in DELOAD_PROTOCOLS.items():
            assert protocol_data["duration_weeks"] > 0, f"Duracion invalida en {protocol_id}"
            assert protocol_data["duration_weeks"] <= 2, f"Duracion muy larga en {protocol_id}"
