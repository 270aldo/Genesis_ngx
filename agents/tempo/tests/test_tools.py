"""Tests para las tools de TEMPO."""

from __future__ import annotations

from agents.tempo.tools import (
    calculate_heart_rate_zones,
    generate_cardio_session,
    suggest_cardio_for_goals,
    calculate_calories_burned,
    SESSION_TEMPLATES,
    HR_ZONES,
)


class TestCalculateHeartRateZones:
    """Tests para calculate_heart_rate_zones."""

    def test_age_based_calculation(self):
        """Debe calcular zonas basadas en edad."""
        result = calculate_heart_rate_zones(age=35)
        assert "zones" in result
        assert len(result["zones"]) == 5
        assert "estimated_max_hr" in result

    def test_younger_has_higher_max_hr(self):
        """Persona joven debe tener max HR mas alto."""
        young = calculate_heart_rate_zones(age=25)
        old = calculate_heart_rate_zones(age=55)
        assert young["estimated_max_hr"] > old["estimated_max_hr"]

    def test_karvonen_method(self):
        """Debe soportar metodo Karvonen con HR en reposo."""
        result = calculate_heart_rate_zones(
            age=35,
            resting_hr=60,
            method="karvonen",
        )
        assert result["method"] == "karvonen"
        assert result["resting_hr"] == 60

    def test_zones_have_correct_structure(self):
        """Zonas deben tener estructura correcta."""
        result = calculate_heart_rate_zones(age=35)
        for zone_id, zone_data in result["zones"].items():
            assert "name" in zone_data
            assert "name_es" in zone_data
            assert "min_hr" in zone_data
            assert "max_hr" in zone_data
            assert "rpe" in zone_data
            assert zone_data["min_hr"] < zone_data["max_hr"]

    def test_zone_5_is_highest(self):
        """Zone 5 debe tener HR mas alto."""
        result = calculate_heart_rate_zones(age=35)
        assert result["zones"]["zone_5"]["max_hr"] > result["zones"]["zone_1"]["max_hr"]


class TestGenerateCardioSession:
    """Tests para generate_cardio_session."""

    def test_generate_hiit_beginner(self):
        """Debe generar sesion HIIT principiante."""
        result = generate_cardio_session(session_type="hiit_beginner")
        assert result["type"] == "hiit"
        assert "main_work" in result
        assert "rounds" in result["main_work"]

    def test_generate_hiit_advanced(self):
        """Debe generar sesion HIIT avanzado."""
        result = generate_cardio_session(session_type="hiit_advanced")
        assert result["type"] == "hiit"
        # HIIT avanzado tiene mas rounds
        assert result["main_work"]["rounds"] >= 15

    def test_generate_liss_session(self):
        """Debe generar sesion LISS."""
        result = generate_cardio_session(session_type="liss_fat_burn")
        assert result["type"] == "liss"
        assert "target_zone" in result["main_work"]

    def test_generate_tempo_run(self):
        """Debe generar sesion tempo run."""
        result = generate_cardio_session(session_type="tempo_run")
        assert result["type"] == "tempo_run"
        assert "tempo_minutes" in result["main_work"]

    def test_generate_fartlek(self):
        """Debe generar sesion fartlek."""
        result = generate_cardio_session(session_type="fartlek")
        assert result["type"] == "fartlek"
        assert "intervals" in result["main_work"]

    def test_generate_pyramid_intervals(self):
        """Debe generar sesion de intervalos piramide."""
        result = generate_cardio_session(session_type="pyramid_intervals")
        assert result["type"] == "intervals"
        assert "structure" in result["main_work"]

    def test_generate_metabolic_circuit(self):
        """Debe generar circuito metabolico."""
        result = generate_cardio_session(session_type="metabolic_circuit")
        assert result["type"] == "circuit"
        assert "exercises" in result["main_work"]

    def test_session_includes_warmup_cooldown(self):
        """Sesion debe incluir warmup y cooldown."""
        result = generate_cardio_session(session_type="hiit_intermediate")
        assert "warmup" in result
        assert "cooldown" in result
        assert result["warmup"]["duration_minutes"] > 0
        assert result["cooldown"]["duration_minutes"] > 0

    def test_invalid_type_defaults_to_hiit_intermediate(self):
        """Tipo invalido debe defaultear a hiit_intermediate."""
        result = generate_cardio_session(session_type="invalid_type")
        assert "main_work" in result


class TestSuggestCardioForGoals:
    """Tests para suggest_cardio_for_goals."""

    def test_fat_loss_plan(self):
        """Debe generar plan para perdida de grasa."""
        result = suggest_cardio_for_goals(
            primary_goal="fat_loss",
            days_per_week=3,
            experience_level="intermediate",
        )
        assert result["goal"] == "fat_loss"
        assert len(result["weekly_plan"]) <= 3

    def test_endurance_plan(self):
        """Debe generar plan para resistencia."""
        result = suggest_cardio_for_goals(
            primary_goal="endurance",
            days_per_week=4,
            experience_level="intermediate",
        )
        assert result["goal"] == "endurance"
        # Endurance debe incluir LISS
        session_types = [s["session_type"] for s in result["weekly_plan"]]
        assert any("liss" in st for st in session_types)

    def test_performance_plan(self):
        """Debe generar plan para rendimiento."""
        result = suggest_cardio_for_goals(
            primary_goal="performance",
            days_per_week=3,
            experience_level="advanced",
        )
        assert result["goal"] == "performance"
        # Performance debe incluir HIIT
        session_types = [s["session_type"] for s in result["weekly_plan"]]
        assert any("hiit" in st for st in session_types)

    def test_general_fitness_plan(self):
        """Debe generar plan para fitness general."""
        result = suggest_cardio_for_goals(
            primary_goal="general_fitness",
            days_per_week=3,
        )
        assert result["goal"] == "general_fitness"

    def test_respects_days_per_week(self):
        """Debe respetar dias por semana."""
        result = suggest_cardio_for_goals(
            primary_goal="fat_loss",
            days_per_week=2,
        )
        assert len(result["weekly_plan"]) <= 2

    def test_includes_tips(self):
        """Debe incluir consejos generales."""
        result = suggest_cardio_for_goals(
            primary_goal="fat_loss",
            days_per_week=3,
        )
        assert "general_tips" in result
        assert len(result["general_tips"]) > 0


class TestCalculateCaloriesBurned:
    """Tests para calculate_calories_burned."""

    def test_basic_calculation(self):
        """Debe calcular calorias basicas."""
        result = calculate_calories_burned(
            duration_minutes=30,
            intensity="moderate",
            body_weight_kg=70,
            activity_type="running",
        )
        assert "estimated_calories" in result
        assert result["estimated_calories"] > 0

    def test_higher_intensity_burns_more(self):
        """Mayor intensidad debe quemar mas calorias."""
        low = calculate_calories_burned(duration_minutes=30, intensity="low")
        high = calculate_calories_burned(duration_minutes=30, intensity="high")
        assert high["estimated_calories"] > low["estimated_calories"]

    def test_longer_duration_burns_more(self):
        """Mayor duracion debe quemar mas calorias."""
        short = calculate_calories_burned(duration_minutes=15)
        long = calculate_calories_burned(duration_minutes=45)
        assert long["estimated_calories"] > short["estimated_calories"]

    def test_heavier_person_burns_more(self):
        """Persona mas pesada debe quemar mas calorias."""
        light = calculate_calories_burned(duration_minutes=30, body_weight_kg=60)
        heavy = calculate_calories_burned(duration_minutes=30, body_weight_kg=90)
        assert heavy["estimated_calories"] > light["estimated_calories"]

    def test_different_activities(self):
        """Diferentes actividades tienen diferentes METs."""
        running = calculate_calories_burned(duration_minutes=30, activity_type="running")
        walking = calculate_calories_burned(duration_minutes=30, activity_type="walking")
        # Running quema mas que walking
        assert running["estimated_calories"] > walking["estimated_calories"]

    def test_includes_met_value(self):
        """Debe incluir valor MET."""
        result = calculate_calories_burned(duration_minutes=30)
        assert "met_value" in result
        assert result["met_value"] > 0


class TestSessionTemplatesIntegrity:
    """Tests para integridad de las plantillas de sesiones."""

    def test_all_templates_have_required_fields(self):
        """Todas las plantillas deben tener campos requeridos."""
        required_fields = ["name_es", "type", "duration_minutes", "modalities"]
        for template_id, template_data in SESSION_TEMPLATES.items():
            for field in required_fields:
                assert field in template_data, f"Template {template_id} falta campo {field}"

    def test_hiit_templates_have_interval_config(self):
        """Templates HIIT deben tener configuracion de intervalos."""
        hiit_templates = [k for k, v in SESSION_TEMPLATES.items() if v["type"] == "hiit"]
        for template_id in hiit_templates:
            template = SESSION_TEMPLATES[template_id]
            assert "work_seconds" in template
            assert "rest_seconds" in template
            assert "rounds" in template

    def test_valid_types(self):
        """Todos los tipos deben ser validos."""
        valid_types = {"hiit", "liss", "fartlek", "tempo_run", "intervals", "circuit"}
        for template_id, template_data in SESSION_TEMPLATES.items():
            assert template_data["type"] in valid_types, f"Tipo invalido en {template_id}"

    def test_durations_positive(self):
        """Todas las duraciones deben ser positivas."""
        for template_id, template_data in SESSION_TEMPLATES.items():
            assert template_data["duration_minutes"] > 0, f"Duracion invalida en {template_id}"


class TestHRZonesIntegrity:
    """Tests para integridad de las zonas HR."""

    def test_all_zones_have_required_fields(self):
        """Todas las zonas deben tener campos requeridos."""
        required_fields = ["name", "name_es", "min_pct", "max_pct", "rpe", "description"]
        for zone_id, zone_data in HR_ZONES.items():
            for field in required_fields:
                assert field in zone_data, f"Zona {zone_id} falta campo {field}"

    def test_zones_are_sequential(self):
        """Zonas deben ser secuenciales (zone_1 < zone_2 < ...)."""
        zone_ids = sorted(HR_ZONES.keys())
        for i in range(len(zone_ids) - 1):
            current = HR_ZONES[zone_ids[i]]
            next_zone = HR_ZONES[zone_ids[i + 1]]
            assert current["max_pct"] <= next_zone["min_pct"] + 1, f"Zonas no secuenciales: {zone_ids[i]}, {zone_ids[i+1]}"

    def test_percentages_in_range(self):
        """Porcentajes deben estar en rango valido."""
        for zone_id, zone_data in HR_ZONES.items():
            assert 0 < zone_data["min_pct"] <= 100, f"min_pct invalido en {zone_id}"
            assert 0 < zone_data["max_pct"] <= 100, f"max_pct invalido en {zone_id}"
            assert zone_data["min_pct"] < zone_data["max_pct"], f"min > max en {zone_id}"
