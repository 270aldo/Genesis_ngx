"""Tests para las tools de LOGOS."""

from __future__ import annotations

from agents.logos.tools import (
    explain_concept,
    present_evidence,
    debunk_myth,
    create_deep_dive,
    generate_quiz,
    CONCEPTS_DATABASE,
    EVIDENCE_DATABASE,
    MYTHS_DATABASE,
    QUIZ_TEMPLATES,
    QUIZ_TOPICS,
    LEARNING_LEVELS,
    ALL_TOOLS,
    Domain,
    LearningLevel,
    EvidenceGrade,
)


# =============================================================================
# Tests para explain_concept
# =============================================================================


class TestExplainConcept:
    """Tests para explain_concept."""

    def test_explain_basic_concept(self):
        """Debe explicar un concepto básico."""
        result = explain_concept(concept="progressive_overload")
        assert result["status"] == "explained"
        assert result["concept"] == "progressive_overload"

    def test_explain_returns_definition(self):
        """Debe incluir definición."""
        result = explain_concept(concept="hypertrophy")
        assert "definition" in result
        assert len(result["definition"]) > 10

    def test_explain_returns_why_important(self):
        """Debe explicar por qué es importante."""
        result = explain_concept(concept="energy_balance")
        assert "why_important" in result

    def test_explain_adapts_to_beginner(self):
        """Debe adaptar explicación a principiantes."""
        result = explain_concept(concept="progressive_overload", user_level="beginner")
        assert result["status"] == "explained"
        assert result["user_level"] == "beginner"
        assert "explanation_for_level" in result

    def test_explain_adapts_to_intermediate(self):
        """Debe adaptar explicación a intermedios."""
        result = explain_concept(concept="progressive_overload", user_level="intermediate")
        assert result["user_level"] == "intermediate"

    def test_explain_adapts_to_advanced(self):
        """Debe adaptar explicación a avanzados."""
        result = explain_concept(concept="progressive_overload", user_level="advanced")
        assert result["user_level"] == "advanced"

    def test_explain_includes_analogy(self):
        """Debe incluir analogía cuando existe."""
        result = explain_concept(concept="progressive_overload", include_examples=True)
        assert "analogy" in result

    def test_explain_includes_mistakes(self):
        """Debe incluir errores comunes cuando existe."""
        result = explain_concept(concept="progressive_overload", include_mistakes=True)
        assert "common_mistakes" in result

    def test_explain_includes_related_concepts(self):
        """Debe incluir conceptos relacionados."""
        result = explain_concept(concept="hypertrophy")
        assert "related_concepts" in result
        assert len(result["related_concepts"]) > 0

    def test_explain_not_found(self):
        """Debe manejar concepto no encontrado."""
        result = explain_concept(concept="concepto_que_no_existe")
        assert result["status"] == "not_found"
        assert "available_concepts" in result

    def test_explain_empty_input(self):
        """Debe manejar input vacío."""
        result = explain_concept(concept="")
        assert result["status"] == "error"

    def test_explain_finds_by_spanish_name(self):
        """Debe encontrar por nombre en español."""
        result = explain_concept(concept="sobrecarga progresiva")
        assert result["status"] == "explained"

    def test_explain_normalizes_input(self):
        """Debe normalizar input con espacios/guiones."""
        result = explain_concept(concept="progressive-overload")
        assert result["status"] == "explained"

    def test_explain_includes_domain(self):
        """Debe incluir dominio del concepto."""
        result = explain_concept(concept="energy_balance")
        assert result["domain"] == "nutrition"


# =============================================================================
# Tests para present_evidence
# =============================================================================


class TestPresentEvidence:
    """Tests para present_evidence."""

    def test_present_basic_evidence(self):
        """Debe presentar evidencia básica."""
        result = present_evidence(topic="creatine_muscle")
        assert result["status"] == "evaluated"

    def test_present_includes_verdict(self):
        """Debe incluir veredicto."""
        result = present_evidence(topic="creatine_muscle")
        assert "verdict" in result

    def test_present_includes_evidence_grade(self):
        """Debe incluir grado de evidencia."""
        result = present_evidence(topic="creatine_muscle")
        assert "evidence_grade" in result
        assert result["evidence_grade"] in ["A", "B", "C", "D"]

    def test_present_includes_studies(self):
        """Debe incluir estudios cuando se solicitan."""
        result = present_evidence(topic="creatine_muscle", include_studies=True)
        assert "key_studies" in result
        assert len(result["key_studies"]) > 0

    def test_present_limits_studies(self):
        """Debe respetar límite de estudios."""
        result = present_evidence(topic="creatine_muscle", include_studies=True, max_studies=1)
        assert len(result["key_studies"]) <= 1

    def test_present_includes_mechanism(self):
        """Debe incluir mecanismo."""
        result = present_evidence(topic="creatine_muscle")
        assert "mechanism" in result

    def test_present_includes_practical_takeaway(self):
        """Debe incluir aplicación práctica."""
        result = present_evidence(topic="creatine_muscle")
        assert "practical_takeaway" in result

    def test_present_not_found(self):
        """Debe manejar tema no encontrado."""
        result = present_evidence(topic="tema_inventado")
        assert result["status"] == "not_found"

    def test_present_empty_input(self):
        """Debe manejar input vacío."""
        result = present_evidence(topic="")
        assert result["status"] == "error"

    def test_present_includes_disclaimer(self):
        """Debe incluir disclaimer."""
        result = present_evidence(topic="creatine_muscle")
        assert "disclaimer" in result

    def test_present_partial_verdict(self):
        """Debe manejar veredictos parciales."""
        result = present_evidence(topic="anabolic_window")
        assert result["status"] == "evaluated"
        # anabolic window tiene veredicto "Parcialmente falso"
        assert result["verdict"] == "Parcialmente falso"

    def test_present_grade_meaning(self):
        """Debe incluir significado del grado."""
        result = present_evidence(topic="creatine_muscle")
        assert "evidence_grade_meaning" in result


# =============================================================================
# Tests para debunk_myth
# =============================================================================


class TestDebunkMyth:
    """Tests para debunk_myth."""

    def test_debunk_basic_myth(self):
        """Debe desmentir un mito básico."""
        result = debunk_myth(myth="spot_reduction")
        assert result["status"] == "debunked"

    def test_debunk_includes_truth(self):
        """Debe incluir la verdad."""
        result = debunk_myth(myth="spot_reduction")
        assert "truth" in result
        assert len(result["truth"]) > 10

    def test_debunk_includes_what_works(self):
        """Debe incluir qué funciona realmente."""
        result = debunk_myth(myth="spot_reduction")
        assert "what_works" in result

    def test_debunk_empathetic_mode(self):
        """Debe incluir empatía cuando se solicita."""
        result = debunk_myth(myth="spot_reduction", empathetic=True)
        assert "why_believed" in result
        assert "empathy_note" in result

    def test_debunk_without_empathy(self):
        """Debe funcionar sin modo empático."""
        result = debunk_myth(myth="spot_reduction", empathetic=False)
        assert result["status"] == "debunked"
        assert "why_believed" not in result

    def test_debunk_not_found(self):
        """Debe manejar mito no encontrado."""
        result = debunk_myth(myth="mito_que_no_existe")
        assert result["status"] == "not_found"
        assert "available_myths" in result

    def test_debunk_empty_input(self):
        """Debe manejar input vacío."""
        result = debunk_myth(myth="")
        assert result["status"] == "error"

    def test_debunk_includes_domain(self):
        """Debe incluir dominio del mito."""
        result = debunk_myth(myth="carbs_night_bad")
        assert result["domain"] == "nutrition"

    def test_debunk_includes_evidence_ref(self):
        """Debe incluir referencia a evidencia cuando existe."""
        result = debunk_myth(myth="spot_reduction")
        assert "supporting_evidence" in result

    def test_debunk_all_domains(self):
        """Debe poder desmentir mitos de todos los dominios."""
        domains_found = set()
        for myth_key in list(MYTHS_DATABASE.keys())[:10]:
            result = debunk_myth(myth=myth_key)
            if result["status"] == "debunked":
                domains_found.add(result["domain"])
        assert len(domains_found) >= 3  # Al menos 3 dominios

    def test_debunk_includes_disclaimer(self):
        """Debe incluir disclaimer."""
        result = debunk_myth(myth="spot_reduction")
        assert "disclaimer" in result


# =============================================================================
# Tests para create_deep_dive
# =============================================================================


class TestCreateDeepDive:
    """Tests para create_deep_dive."""

    def test_create_basic_deep_dive(self):
        """Debe crear un deep dive básico."""
        result = create_deep_dive(topic="progressive_overload")
        assert result["status"] == "created"

    def test_deep_dive_has_title(self):
        """Debe tener título."""
        result = create_deep_dive(topic="hypertrophy")
        assert "title" in result
        assert "Deep Dive" in result["title"]

    def test_deep_dive_has_sections(self):
        """Debe tener secciones."""
        result = create_deep_dive(topic="energy_balance")
        assert "sections" in result
        assert len(result["sections"]) >= 2

    def test_deep_dive_has_estimated_time(self):
        """Debe tener tiempo estimado."""
        result = create_deep_dive(topic="progressive_overload")
        assert "estimated_time_minutes" in result
        assert result["estimated_time_minutes"] > 0

    def test_deep_dive_adapts_to_level(self):
        """Debe adaptar al nivel del usuario."""
        beginner = create_deep_dive(topic="progressive_overload", user_level="beginner")
        advanced = create_deep_dive(topic="progressive_overload", user_level="advanced")
        assert beginner["estimated_time_minutes"] < advanced["estimated_time_minutes"]

    def test_deep_dive_includes_quiz(self):
        """Debe incluir quiz cuando se solicita."""
        result = create_deep_dive(topic="hypertrophy", include_quiz=True)
        assert "quiz" in result

    def test_deep_dive_without_quiz(self):
        """Debe funcionar sin quiz."""
        result = create_deep_dive(topic="hypertrophy", include_quiz=False)
        assert result["status"] == "created"

    def test_deep_dive_has_next_steps(self):
        """Debe tener siguientes pasos."""
        result = create_deep_dive(topic="progressive_overload")
        assert "next_steps" in result

    def test_deep_dive_not_found(self):
        """Debe manejar tema no encontrado."""
        result = create_deep_dive(topic="tema_que_no_existe")
        assert result["status"] == "not_found"

    def test_deep_dive_empty_input(self):
        """Debe manejar input vacío."""
        result = create_deep_dive(topic="")
        assert result["status"] == "error"


# =============================================================================
# Tests para generate_quiz
# =============================================================================


class TestGenerateQuiz:
    """Tests para generate_quiz."""

    def test_generate_basic_quiz(self):
        """Debe generar un quiz básico."""
        result = generate_quiz(topic="nutrition_basics")
        assert result["status"] == "generated"

    def test_quiz_has_questions(self):
        """Debe tener preguntas."""
        result = generate_quiz(topic="nutrition_basics")
        assert "quiz" in result
        assert "questions" in result["quiz"]
        assert len(result["quiz"]["questions"]) > 0

    def test_quiz_respects_num_questions(self):
        """Debe respetar número de preguntas."""
        result = generate_quiz(topic="training_fundamentals", num_questions=3)
        assert result["num_questions"] <= 3

    def test_quiz_has_difficulty(self):
        """Debe indicar dificultad."""
        result = generate_quiz(topic="nutrition_basics", difficulty="hard")
        assert result["difficulty"] == "hard"

    def test_quiz_questions_have_correct_answer(self):
        """Las preguntas deben tener respuesta correcta."""
        result = generate_quiz(topic="nutrition_basics", num_questions=2)
        for q in result["quiz"]["questions"]:
            assert "correct_answer" in q

    def test_quiz_questions_have_explanation(self):
        """Las preguntas deben tener explicación."""
        result = generate_quiz(topic="nutrition_basics", num_questions=2)
        for q in result["quiz"]["questions"]:
            assert "explanation" in q

    def test_quiz_multiple_choice_format(self):
        """Las preguntas de opción múltiple deben tener formato correcto."""
        result = generate_quiz(topic="training_fundamentals", question_types=["multiple_choice"])
        for q in result["quiz"]["questions"]:
            if q["type"] == "multiple_choice":
                assert "options" in q
                assert len(q["options"]) == 4

    def test_quiz_true_false_format(self):
        """Las preguntas V/F deben tener formato correcto."""
        result = generate_quiz(topic="behavior_change", question_types=["true_false"])
        for q in result["quiz"]["questions"]:
            if q["type"] == "true_false":
                assert "statement" in q
                assert isinstance(q["correct_answer"], bool)

    def test_quiz_not_found(self):
        """Debe manejar tema no encontrado."""
        result = generate_quiz(topic="tema_que_no_existe")
        assert result["status"] == "error"

    def test_quiz_empty_input(self):
        """Debe manejar input vacío."""
        result = generate_quiz(topic="")
        assert result["status"] == "error"

    def test_quiz_includes_disclaimer(self):
        """Debe incluir disclaimer."""
        result = generate_quiz(topic="nutrition_basics")
        assert "disclaimer" in result

    def test_quiz_predefined_topics(self):
        """Debe funcionar con todos los topics predefinidos."""
        for topic in QUIZ_TOPICS.keys():
            result = generate_quiz(topic=topic, num_questions=2)
            assert result["status"] == "generated"

    def test_quiz_by_domain(self):
        """Debe generar quiz por dominio."""
        result = generate_quiz(topic="fitness", num_questions=3)
        assert result["status"] == "generated"


# =============================================================================
# Tests para CONCEPTS_DATABASE
# =============================================================================


class TestConceptsDatabaseIntegrity:
    """Tests para integridad de CONCEPTS_DATABASE."""

    def test_all_concepts_have_required_fields(self):
        """Todos los conceptos deben tener campos requeridos."""
        required = ["domain", "name_es", "definition", "why_important", "levels"]
        for key, data in CONCEPTS_DATABASE.items():
            for field in required:
                assert field in data, f"Concepto {key} falta campo {field}"

    def test_all_concepts_have_all_levels(self):
        """Todos los conceptos deben tener los 3 niveles."""
        for key, data in CONCEPTS_DATABASE.items():
            levels = data["levels"]
            assert "beginner" in levels, f"Concepto {key} falta nivel beginner"
            assert "intermediate" in levels, f"Concepto {key} falta nivel intermediate"
            assert "advanced" in levels, f"Concepto {key} falta nivel advanced"

    def test_concepts_cover_all_domains(self):
        """Debe haber conceptos de todos los dominios."""
        domains = set(data["domain"] for data in CONCEPTS_DATABASE.values())
        expected_domains = {"fitness", "nutrition", "behavior", "recovery", "womens_health", "mobility", "analytics"}
        assert domains == expected_domains

    def test_concept_count_is_minimum_33(self):
        """Debe haber al menos 33 conceptos (expanded)."""
        assert len(CONCEPTS_DATABASE) >= 33

    def test_concepts_have_valid_domains(self):
        """Los dominios deben ser válidos."""
        valid_domains = {"fitness", "nutrition", "behavior", "recovery", "womens_health", "mobility", "analytics"}
        for key, data in CONCEPTS_DATABASE.items():
            assert data["domain"] in valid_domains, f"Concepto {key} tiene dominio inválido"


# =============================================================================
# Tests para EVIDENCE_DATABASE
# =============================================================================


class TestEvidenceDatabaseIntegrity:
    """Tests para integridad de EVIDENCE_DATABASE."""

    def test_all_evidence_has_required_fields(self):
        """Toda la evidencia debe tener campos requeridos."""
        required = ["claim", "verdict", "evidence_grade"]
        for key, data in EVIDENCE_DATABASE.items():
            for field in required:
                assert field in data, f"Evidencia {key} falta campo {field}"

    def test_evidence_grades_are_valid(self):
        """Los grados de evidencia deben ser válidos."""
        valid_grades = {"A", "B", "C", "D"}
        for key, data in EVIDENCE_DATABASE.items():
            assert data["evidence_grade"] in valid_grades, f"Evidencia {key} tiene grado inválido"

    def test_evidence_count_is_minimum_14(self):
        """Debe haber al menos 14 items de evidencia (expanded)."""
        assert len(EVIDENCE_DATABASE) >= 14

    def test_evidence_has_practical_takeaway(self):
        """La evidencia debe tener aplicación práctica."""
        for key, data in EVIDENCE_DATABASE.items():
            assert "practical_takeaway" in data, f"Evidencia {key} falta practical_takeaway"


# =============================================================================
# Tests para MYTHS_DATABASE
# =============================================================================


class TestMythsDatabaseIntegrity:
    """Tests para integridad de MYTHS_DATABASE."""

    def test_all_myths_have_required_fields(self):
        """Todos los mitos deben tener campos requeridos."""
        required = ["myth_es", "domain", "truth", "what_works"]
        for key, data in MYTHS_DATABASE.items():
            for field in required:
                assert field in data, f"Mito {key} falta campo {field}"

    def test_myths_cover_all_domains(self):
        """Debe haber mitos de todos los dominios."""
        domains = set(data["domain"] for data in MYTHS_DATABASE.values())
        expected_domains = {"fitness", "nutrition", "behavior", "recovery", "womens_health"}
        assert domains == expected_domains

    def test_myth_count_is_minimum_15(self):
        """Debe haber al menos 15 mitos (MVP)."""
        assert len(MYTHS_DATABASE) >= 15

    def test_myths_have_why_believed(self):
        """Los mitos deben explicar por qué se creen."""
        for key, data in MYTHS_DATABASE.items():
            assert "why_believed" in data, f"Mito {key} falta why_believed"


# =============================================================================
# Tests para QUIZ_TEMPLATES
# =============================================================================


class TestQuizTemplatesIntegrity:
    """Tests para integridad de QUIZ_TEMPLATES."""

    def test_has_multiple_choice(self):
        """Debe tener template de opción múltiple."""
        assert "multiple_choice" in QUIZ_TEMPLATES

    def test_has_true_false(self):
        """Debe tener template de verdadero/falso."""
        assert "true_false" in QUIZ_TEMPLATES

    def test_has_fill_blank(self):
        """Debe tener template de completar."""
        assert "fill_blank" in QUIZ_TEMPLATES

    def test_has_scenario(self):
        """Debe tener template de escenario."""
        assert "scenario" in QUIZ_TEMPLATES

    def test_templates_have_format(self):
        """Los templates deben tener formato."""
        for key, template in QUIZ_TEMPLATES.items():
            assert "format" in template, f"Template {key} falta format"


# =============================================================================
# Tests para QUIZ_TOPICS
# =============================================================================


class TestQuizTopicsIntegrity:
    """Tests para integridad de QUIZ_TOPICS."""

    def test_has_nutrition_basics(self):
        """Debe tener topic de nutrición básica."""
        assert "nutrition_basics" in QUIZ_TOPICS

    def test_has_training_fundamentals(self):
        """Debe tener topic de fundamentos de entrenamiento."""
        assert "training_fundamentals" in QUIZ_TOPICS

    def test_has_behavior_change(self):
        """Debe tener topic de cambio de comportamiento."""
        assert "behavior_change" in QUIZ_TOPICS

    def test_has_mobility_fundamentals(self):
        """Debe tener topic de fundamentos de movilidad."""
        assert "mobility_fundamentals" in QUIZ_TOPICS

    def test_has_analytics_essentials(self):
        """Debe tener topic de esenciales de analytics."""
        assert "analytics_essentials" in QUIZ_TOPICS

    def test_has_nutrition_advanced(self):
        """Debe tener topic de nutrición avanzada."""
        assert "nutrition_advanced" in QUIZ_TOPICS

    def test_has_womens_health_advanced(self):
        """Debe tener topic de salud femenina avanzada."""
        assert "womens_health_advanced" in QUIZ_TOPICS

    def test_topics_reference_valid_concepts(self):
        """Los topics deben referenciar conceptos válidos."""
        for topic, concepts in QUIZ_TOPICS.items():
            for concept in concepts:
                assert concept in CONCEPTS_DATABASE, f"Topic {topic} referencia concepto inválido {concept}"


# =============================================================================
# Tests para LEARNING_LEVELS
# =============================================================================


class TestLearningLevelsIntegrity:
    """Tests para integridad de LEARNING_LEVELS."""

    def test_has_three_levels(self):
        """Debe tener 3 niveles de aprendizaje."""
        assert len(LEARNING_LEVELS) == 3

    def test_has_beginner(self):
        """Debe tener nivel principiante."""
        assert "beginner" in LEARNING_LEVELS

    def test_has_intermediate(self):
        """Debe tener nivel intermedio."""
        assert "intermediate" in LEARNING_LEVELS

    def test_has_advanced(self):
        """Debe tener nivel avanzado."""
        assert "advanced" in LEARNING_LEVELS

    def test_levels_have_description(self):
        """Los niveles deben tener descripción."""
        for key, level in LEARNING_LEVELS.items():
            assert "description" in level, f"Nivel {key} falta description"
            assert "explanation_style" in level, f"Nivel {key} falta explanation_style"


# =============================================================================
# Tests para ALL_TOOLS
# =============================================================================


class TestAllTools:
    """Tests para ALL_TOOLS."""

    def test_has_5_tools(self):
        """Debe tener exactamente 5 tools."""
        assert len(ALL_TOOLS) == 5

    def test_tools_are_function_tools(self):
        """Las tools deben ser FunctionTool."""
        for tool in ALL_TOOLS:
            # Verificar que tienen el método func o similar
            assert hasattr(tool, "func") or hasattr(tool, "__call__")


# =============================================================================
# Tests para Enums
# =============================================================================


class TestEnums:
    """Tests para los enums."""

    def test_domain_enum_has_all_values(self):
        """Domain enum debe tener todos los valores."""
        assert Domain.FITNESS == "fitness"
        assert Domain.NUTRITION == "nutrition"
        assert Domain.BEHAVIOR == "behavior"
        assert Domain.RECOVERY == "recovery"
        assert Domain.WOMENS_HEALTH == "womens_health"
        assert Domain.MOBILITY == "mobility"
        assert Domain.ANALYTICS == "analytics"

    def test_learning_level_enum(self):
        """LearningLevel enum debe tener todos los valores."""
        assert LearningLevel.BEGINNER == "beginner"
        assert LearningLevel.INTERMEDIATE == "intermediate"
        assert LearningLevel.ADVANCED == "advanced"

    def test_evidence_grade_enum(self):
        """EvidenceGrade enum debe tener todos los valores."""
        assert EvidenceGrade.A == "A"
        assert EvidenceGrade.B == "B"
        assert EvidenceGrade.C == "C"
        assert EvidenceGrade.D == "D"
