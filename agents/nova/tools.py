"""Tools para NOVA - Agente de Suplementación.

Incluye funciones para:
- Recomendación de suplementos según objetivos
- Diseño de stacks personalizados
- Protocolos de timing y dosificación
- Verificación de interacciones
- Evaluación de nivel de evidencia
"""

from __future__ import annotations

from enum import Enum

from google.adk.tools import FunctionTool


# =============================================================================
# ENUMS Y TIPOS
# =============================================================================


class EvidenceLevel(str, Enum):
    """Nivel de evidencia científica."""

    A = "A"  # Fuerte: meta-análisis, consenso
    B = "B"  # Moderada: varios RCTs
    C = "C"  # Limitada: pocos estudios
    D = "D"  # Insuficiente: anecdótica


class InteractionSeverity(str, Enum):
    """Severidad de interacción."""

    SEVERE = "severe"
    MODERATE = "moderate"
    MILD = "mild"
    SYNERGY = "synergy"


class SupplementCategory(str, Enum):
    """Categoría de suplemento."""

    FOUNDATIONAL = "foundational"
    PERFORMANCE = "performance"
    HEALTH = "health"
    SLEEP = "sleep"
    COGNITIVE = "cognitive"
    RECOVERY = "recovery"


class GoalType(str, Enum):
    """Tipo de objetivo."""

    MUSCLE_GAIN = "muscle_gain"
    FAT_LOSS = "fat_loss"
    PERFORMANCE = "performance"
    SLEEP = "sleep"
    COGNITIVE = "cognitive"
    HEALTH = "health"
    RECOVERY = "recovery"
    LONGEVITY = "longevity"


# =============================================================================
# DATOS DE REFERENCIA
# =============================================================================


SUPPLEMENTS_DATABASE: dict[str, dict] = {
    # Foundational
    "vitamin_d3": {
        "name_es": "Vitamina D3",
        "category": "foundational",
        "evidence_level": "A",
        "typical_dose": "2000-5000 IU",
        "timing": "con comida grasa",
        "benefits": ["salud ósea", "inmunidad", "estado de ánimo", "testosterona"],
        "considerations": ["medir niveles 25-OH", "suplementar K2 juntos"],
        "price_range_usd": "5-15",
        "form_recommended": "D3 colecalciferol, no D2",
    },
    "omega3": {
        "name_es": "Omega-3 (EPA/DHA)",
        "category": "foundational",
        "evidence_level": "A",
        "typical_dose": "1-3g EPA+DHA",
        "timing": "con comida",
        "benefits": ["antiinflamatorio", "cardiovascular", "cognitivo", "articulaciones"],
        "considerations": ["calidad importa", "refrigerar", "puede adelgazar sangre"],
        "price_range_usd": "15-40",
        "form_recommended": "Triglicéridos o fosfolípidos, no ésteres etílicos",
    },
    "magnesium": {
        "name_es": "Magnesio",
        "category": "foundational",
        "evidence_level": "A",
        "typical_dose": "200-400mg",
        "timing": "noche preferible",
        "benefits": ["sueño", "relajación muscular", "estrés", "energía"],
        "considerations": ["evitar óxido (baja absorción)", "puede causar diarrea si exceso"],
        "price_range_usd": "10-25",
        "form_recommended": "Glicinato, citrato, o treonato",
    },
    "vitamin_k2": {
        "name_es": "Vitamina K2",
        "category": "foundational",
        "evidence_level": "B",
        "typical_dose": "100-200mcg MK-7",
        "timing": "con D3 y comida grasa",
        "benefits": ["dirige calcio a huesos", "salud cardiovascular"],
        "considerations": ["evitar si toma anticoagulantes", "MK-7 > MK-4"],
        "price_range_usd": "10-20",
        "form_recommended": "MK-7 (menaquinona-7)",
    },
    # Performance
    "creatine": {
        "name_es": "Creatina Monohidrato",
        "category": "performance",
        "evidence_level": "A",
        "typical_dose": "5g/día",
        "timing": "cualquier momento, consistencia",
        "benefits": ["fuerza", "potencia", "masa muscular", "cognición"],
        "considerations": ["no necesita carga", "hidratarse bien", "segura largo plazo"],
        "price_range_usd": "10-20",
        "form_recommended": "Monohidrato micronizado",
    },
    "caffeine": {
        "name_es": "Cafeína",
        "category": "performance",
        "evidence_level": "A",
        "typical_dose": "100-400mg",
        "timing": "30-60 min pre-entreno",
        "benefits": ["energía", "focus", "rendimiento", "oxidación grasa"],
        "considerations": ["tolerancia", "no después de 2pm", "puede afectar sueño"],
        "price_range_usd": "5-15",
        "form_recommended": "Cafeína anhidra o de fuente natural",
    },
    "beta_alanine": {
        "name_es": "Beta-Alanina",
        "category": "performance",
        "evidence_level": "A",
        "typical_dose": "3-5g/día",
        "timing": "dividir dosis, consistencia",
        "benefits": ["capacidad tamponamiento", "resistencia alta intensidad"],
        "considerations": ["hormigueo normal (parestesia)", "efecto tarda 4+ semanas"],
        "price_range_usd": "15-25",
        "form_recommended": "Beta-alanina pura",
    },
    "citrulline": {
        "name_es": "Citrulina",
        "category": "performance",
        "evidence_level": "B",
        "typical_dose": "6-8g L-citrulina",
        "timing": "30-45 min pre-entreno",
        "benefits": ["vasodilatación", "pump", "resistencia", "recuperación"],
        "considerations": ["L-citrulina > citrulina malato para dosis", "estómago vacío"],
        "price_range_usd": "15-30",
        "form_recommended": "L-Citrulina o Citrulina Malato 2:1",
    },
    # Sleep
    "ashwagandha": {
        "name_es": "Ashwagandha",
        "category": "sleep",
        "evidence_level": "B",
        "typical_dose": "300-600mg extracto",
        "timing": "noche o dividir AM/PM",
        "benefits": ["reduce cortisol", "ansiedad", "sueño", "testosterona"],
        "considerations": ["KSM-66 o Sensoril", "evitar en hipertiroidismo"],
        "price_range_usd": "15-30",
        "form_recommended": "KSM-66 o Sensoril (extractos estandarizados)",
    },
    "l_theanine": {
        "name_es": "L-Teanina",
        "category": "sleep",
        "evidence_level": "B",
        "typical_dose": "100-200mg",
        "timing": "con cafeína o noche",
        "benefits": ["relajación sin sedación", "focus con cafeína", "sueño"],
        "considerations": ["sinergia 2:1 con cafeína", "muy seguro"],
        "price_range_usd": "10-20",
        "form_recommended": "L-Teanina (Suntheanine)",
    },
    "melatonin": {
        "name_es": "Melatonina",
        "category": "sleep",
        "evidence_level": "A",
        "typical_dose": "0.5-3mg",
        "timing": "30-60 min antes dormir",
        "benefits": ["jet lag", "onset del sueño", "antioxidante"],
        "considerations": ["menos es más", "no uso crónico", "solo si necesario"],
        "price_range_usd": "5-15",
        "form_recommended": "Liberación inmediata, dosis baja",
    },
    # Cognitive
    "lions_mane": {
        "name_es": "Melena de León",
        "category": "cognitive",
        "evidence_level": "C",
        "typical_dose": "500-1000mg extracto",
        "timing": "mañana o dividir",
        "benefits": ["NGF", "neuroprotección", "cognición", "ánimo"],
        "considerations": ["extracto dual > polvo", "efectos tardan semanas"],
        "price_range_usd": "20-40",
        "form_recommended": "Extracto dual (agua + alcohol)",
    },
    "bacopa": {
        "name_es": "Bacopa Monnieri",
        "category": "cognitive",
        "evidence_level": "B",
        "typical_dose": "300-450mg extracto",
        "timing": "con comida grasa",
        "benefits": ["memoria", "aprendizaje", "ansiedad"],
        "considerations": ["efecto tarda 8-12 semanas", "puede causar fatiga inicial"],
        "price_range_usd": "15-25",
        "form_recommended": "Extracto estandarizado 50% bacósidos",
    },
    "phosphatidylserine": {
        "name_es": "Fosfatidilserina",
        "category": "cognitive",
        "evidence_level": "B",
        "typical_dose": "100-300mg",
        "timing": "con comida",
        "benefits": ["memoria", "cortisol post-ejercicio", "cognición bajo estrés"],
        "considerations": ["derivado de soja o girasol", "caro pero efectivo"],
        "price_range_usd": "25-45",
        "form_recommended": "Fosfatidilserina de girasol",
    },
    # Health/Recovery
    "zinc": {
        "name_es": "Zinc",
        "category": "health",
        "evidence_level": "A",
        "typical_dose": "15-30mg",
        "timing": "con comida",
        "benefits": ["inmunidad", "testosterona", "recuperación", "piel"],
        "considerations": ["balance con cobre", "no exceder 40mg", "forma importa"],
        "price_range_usd": "5-15",
        "form_recommended": "Picolinato, citrato, o bisglicinato",
    },
    "collagen": {
        "name_es": "Colágeno",
        "category": "recovery",
        "evidence_level": "B",
        "typical_dose": "10-15g",
        "timing": "30-60 min antes de ejercicio o noche",
        "benefits": ["articulaciones", "piel", "cabello", "tendones"],
        "considerations": ["tomar con vitamina C", "hidrolizado para absorción"],
        "price_range_usd": "20-40",
        "form_recommended": "Péptidos de colágeno hidrolizado tipo I/III",
    },
    "curcumin": {
        "name_es": "Curcumina",
        "category": "health",
        "evidence_level": "B",
        "typical_dose": "500-1000mg",
        "timing": "con comida grasa",
        "benefits": ["antiinflamatorio", "antioxidante", "articulaciones", "cognición"],
        "considerations": ["baja biodisponibilidad sola", "usar con piperina o forma mejorada"],
        "price_range_usd": "20-40",
        "form_recommended": "Meriva, Longvida, o con piperina",
    },
    "probiotics": {
        "name_es": "Probióticos",
        "category": "health",
        "evidence_level": "B",
        "typical_dose": "10-50 billion CFU",
        "timing": "30 min antes comida",
        "benefits": ["salud intestinal", "inmunidad", "inflamación", "ánimo"],
        "considerations": ["cepa específica para objetivo", "refrigerar si necesario"],
        "price_range_usd": "15-40",
        "form_recommended": "Multi-cepa con Lactobacillus y Bifidobacterium",
    },
}


INTERACTIONS_DATABASE: dict[str, list[dict]] = {
    "omega3": [
        {
            "with": "anticoagulantes",
            "type": "medicamento",
            "severity": "moderate",
            "mechanism": "Efecto aditivo adelgazamiento sangre",
            "recommendation": "Consultar médico, posible ajuste dosis",
        },
        {
            "with": "vitamin_e",
            "type": "suplemento",
            "severity": "synergy",
            "mechanism": "Vitamina E previene oxidación omega-3",
            "recommendation": "Combinación beneficiosa",
        },
    ],
    "vitamin_k2": [
        {
            "with": "warfarina",
            "type": "medicamento",
            "severity": "severe",
            "mechanism": "K2 antagoniza efecto anticoagulante",
            "recommendation": "EVITAR o monitoreo estricto INR",
        },
        {
            "with": "vitamin_d3",
            "type": "suplemento",
            "severity": "synergy",
            "mechanism": "K2 dirige calcio movilizado por D3 a huesos",
            "recommendation": "Tomar juntos para máximo beneficio",
        },
    ],
    "zinc": [
        {
            "with": "antibióticos_quinolonas",
            "type": "medicamento",
            "severity": "moderate",
            "mechanism": "Zinc reduce absorción de antibiótico",
            "recommendation": "Separar 2+ horas",
        },
        {
            "with": "hierro",
            "type": "suplemento",
            "severity": "moderate",
            "mechanism": "Competencia por absorción",
            "recommendation": "Separar tomas o tomar con comida",
        },
        {
            "with": "cobre",
            "type": "suplemento",
            "severity": "mild",
            "mechanism": "Zinc alto depleta cobre",
            "recommendation": "Mantener ratio 15:1 zinc:cobre",
        },
    ],
    "magnesium": [
        {
            "with": "antibióticos",
            "type": "medicamento",
            "severity": "moderate",
            "mechanism": "Reduce absorción mutua",
            "recommendation": "Separar 2+ horas",
        },
        {
            "with": "bifosfonatos",
            "type": "medicamento",
            "severity": "moderate",
            "mechanism": "Magnesio reduce absorción",
            "recommendation": "Separar 2+ horas",
        },
    ],
    "caffeine": [
        {
            "with": "l_theanine",
            "type": "suplemento",
            "severity": "synergy",
            "mechanism": "L-teanina suaviza efectos negativos cafeína",
            "recommendation": "Ratio 2:1 teanina:cafeína ideal",
        },
        {
            "with": "efedrina",
            "type": "suplemento",
            "severity": "severe",
            "mechanism": "Efectos cardiovasculares aditivos peligrosos",
            "recommendation": "EVITAR combinación",
        },
    ],
    "ashwagandha": [
        {
            "with": "sedantes",
            "type": "medicamento",
            "severity": "moderate",
            "mechanism": "Efecto aditivo sedante",
            "recommendation": "Precaución, posible ajuste",
        },
        {
            "with": "medicamentos_tiroides",
            "type": "medicamento",
            "severity": "moderate",
            "mechanism": "Puede aumentar función tiroidea",
            "recommendation": "Evitar en hipertiroidismo",
        },
    ],
    "curcumin": [
        {
            "with": "anticoagulantes",
            "type": "medicamento",
            "severity": "moderate",
            "mechanism": "Efecto anticoagulante aditivo",
            "recommendation": "Consultar médico",
        },
        {
            "with": "piperina",
            "type": "suplemento",
            "severity": "synergy",
            "mechanism": "Piperina aumenta biodisponibilidad 2000%",
            "recommendation": "Combinar para mejor absorción",
        },
    ],
    "melatonin": [
        {
            "with": "sedantes",
            "type": "medicamento",
            "severity": "moderate",
            "mechanism": "Efecto sedante aditivo",
            "recommendation": "Precaución, usar dosis bajas",
        },
        {
            "with": "anticoagulantes",
            "type": "medicamento",
            "severity": "mild",
            "mechanism": "Posible efecto anticoagulante leve",
            "recommendation": "Monitorear si dosis altas",
        },
    ],
}


GOAL_TO_SUPPLEMENTS: dict[str, list[str]] = {
    "muscle_gain": ["creatine", "vitamin_d3", "omega3", "zinc", "magnesium"],
    "fat_loss": ["caffeine", "omega3", "vitamin_d3", "magnesium", "l_theanine"],
    "performance": ["creatine", "caffeine", "beta_alanine", "citrulline", "omega3"],
    "sleep": ["magnesium", "ashwagandha", "l_theanine", "melatonin", "vitamin_d3"],
    "cognitive": ["omega3", "lions_mane", "bacopa", "phosphatidylserine", "caffeine"],
    "health": ["vitamin_d3", "omega3", "magnesium", "vitamin_k2", "probiotics"],
    "recovery": ["omega3", "magnesium", "collagen", "curcumin", "zinc"],
    "longevity": ["omega3", "vitamin_d3", "magnesium", "curcumin", "probiotics"],
}


TIMING_WINDOWS: dict[str, dict] = {
    "morning_fasted": {
        "name_es": "Mañana en ayunas",
        "supplements": ["probiotics", "l_theanine"],
        "reasoning": "Mejor absorción sin competencia de alimentos",
    },
    "morning_with_food": {
        "name_es": "Mañana con desayuno",
        "supplements": ["vitamin_d3", "vitamin_k2", "omega3", "curcumin"],
        "reasoning": "Liposolubles necesitan grasa para absorción",
    },
    "pre_workout": {
        "name_es": "Pre-entreno (30-60 min antes)",
        "supplements": ["caffeine", "citrulline", "beta_alanine"],
        "reasoning": "Tiempo para absorción y efecto máximo",
    },
    "post_workout": {
        "name_es": "Post-entreno",
        "supplements": ["creatine", "collagen"],
        "reasoning": "Ventana de recuperación, aunque timing flexible",
    },
    "with_meals": {
        "name_es": "Con comidas",
        "supplements": ["zinc", "magnesium", "bacopa"],
        "reasoning": "Reduce molestias GI, mejora absorción",
    },
    "evening": {
        "name_es": "Noche (1-2h antes de dormir)",
        "supplements": ["magnesium", "ashwagandha", "l_theanine", "melatonin"],
        "reasoning": "Efectos relajantes y promotores del sueño",
    },
}


# =============================================================================
# FUNCIONES DE CÁLCULO
# =============================================================================


def recommend_supplements(
    goal: str,
    current_supplements: list[str] | None = None,
    dietary_restrictions: list[str] | None = None,
    budget_monthly_usd: int = 50,
    max_supplements: int = 5,
) -> dict:
    """Recomienda suplementos basados en objetivos específicos.

    Args:
        goal: Objetivo principal (muscle_gain, fat_loss, performance, etc.).
        current_supplements: Suplementos que ya toma el usuario.
        dietary_restrictions: Restricciones (vegano, sin soja, etc.).
        budget_monthly_usd: Presupuesto mensual en USD.
        max_supplements: Número máximo de suplementos a recomendar.

    Returns:
        Dict con recomendaciones priorizadas.
    """
    if not goal or len(goal.strip()) < 3:
        return {
            "status": "error",
            "error": "Especifica un objetivo (muscle_gain, sleep, performance, etc.)",
        }

    # Normalizar goal
    goal_normalized = goal.lower().replace(" ", "_")
    if goal_normalized not in GOAL_TO_SUPPLEMENTS:
        # Mapear términos comunes
        goal_mapping = {
            "ganar_musculo": "muscle_gain",
            "muscular": "muscle_gain",
            "perder_grasa": "fat_loss",
            "adelgazar": "fat_loss",
            "dormir": "sleep",
            "sueño": "sleep",
            "concentracion": "cognitive",
            "energia": "performance",
            "recuperacion": "recovery",
            "salud": "health",
        }
        goal_normalized = goal_mapping.get(goal_normalized, "health")

    current_set = set(current_supplements or [])

    # Obtener suplementos para el objetivo
    recommended_ids = GOAL_TO_SUPPLEMENTS.get(goal_normalized, GOAL_TO_SUPPLEMENTS["health"])

    # Filtrar los que ya toma
    new_recommendations = [s for s in recommended_ids if s not in current_set]

    # Construir recomendaciones detalladas
    recommendations = []
    total_cost = 0

    for supp_id in new_recommendations[:max_supplements]:
        if supp_id not in SUPPLEMENTS_DATABASE:
            continue

        supp = SUPPLEMENTS_DATABASE[supp_id]

        # Estimar costo
        price_range = supp["price_range_usd"].split("-")
        avg_price = (int(price_range[0]) + int(price_range[1])) / 2

        if total_cost + avg_price > budget_monthly_usd:
            continue

        total_cost += avg_price

        # Verificar restricciones
        skip = False
        if dietary_restrictions:
            for restriction in dietary_restrictions:
                if restriction.lower() == "vegano" and supp_id in ["omega3", "collagen"]:
                    skip = True
                    break
        if skip:
            continue

        recommendations.append({
            "id": supp_id,
            "name_es": supp["name_es"],
            "dose": supp["typical_dose"],
            "timing": supp["timing"],
            "evidence_level": supp["evidence_level"],
            "benefits": supp["benefits"][:3],
            "price_range_usd": supp["price_range_usd"],
            "form_recommended": supp["form_recommended"],
            "priority": len(recommendations) + 1,
        })

    # Calcular tier de prioridad
    tier_1 = [r for r in recommendations if r["evidence_level"] == "A"]
    tier_2 = [r for r in recommendations if r["evidence_level"] == "B"]
    tier_3 = [r for r in recommendations if r["evidence_level"] in ["C", "D"]]

    return {
        "status": "recommended",
        "goal": goal_normalized,
        "total_recommendations": len(recommendations),
        "estimated_monthly_cost_usd": round(total_cost, 2),
        "recommendations": recommendations,
        "by_tier": {
            "tier_1_essential": tier_1,
            "tier_2_beneficial": tier_2,
            "tier_3_optional": tier_3,
        },
        "already_taking": list(current_set) if current_set else [],
        "disclaimer": "Consulta con tu médico antes de comenzar cualquier suplementación.",
    }


def design_stack(
    primary_goal: str,
    secondary_goals: list[str] | None = None,
    experience_level: str = "beginner",
    budget_monthly_usd: int = 75,
    preferences: dict | None = None,
) -> dict:
    """Diseña un stack completo de suplementos personalizado.

    Args:
        primary_goal: Objetivo principal.
        secondary_goals: Objetivos secundarios.
        experience_level: Nivel de experiencia (beginner, intermediate, advanced).
        budget_monthly_usd: Presupuesto mensual.
        preferences: Preferencias adicionales (vegano, sin cafeína, etc.).

    Returns:
        Dict con stack diseñado y protocolo.
    """
    if not primary_goal or len(primary_goal.strip()) < 3:
        return {
            "status": "error",
            "error": "Especifica un objetivo principal",
        }

    # Normalizar goal
    primary_normalized = primary_goal.lower().replace(" ", "_")
    goal_mapping = {
        "ganar_musculo": "muscle_gain",
        "muscular": "muscle_gain",
        "perder_grasa": "fat_loss",
        "adelgazar": "fat_loss",
        "dormir": "sleep",
        "sueño": "sleep",
        "concentracion": "cognitive",
        "energia": "performance",
        "recuperacion": "recovery",
        "salud": "health",
    }
    primary_normalized = goal_mapping.get(primary_normalized, primary_normalized)
    if primary_normalized not in GOAL_TO_SUPPLEMENTS:
        primary_normalized = "health"

    # Recopilar suplementos de todos los objetivos
    all_supplements = set(GOAL_TO_SUPPLEMENTS.get(primary_normalized, []))

    if secondary_goals:
        for sg in secondary_goals[:2]:  # Máximo 2 secundarios
            sg_norm = goal_mapping.get(sg.lower().replace(" ", "_"), sg.lower())
            if sg_norm in GOAL_TO_SUPPLEMENTS:
                all_supplements.update(GOAL_TO_SUPPLEMENTS[sg_norm][:3])

    # Filtrar por preferencias
    prefs = preferences or {}
    if prefs.get("no_caffeine"):
        all_supplements.discard("caffeine")
    if prefs.get("vegan"):
        all_supplements.discard("omega3")
        all_supplements.discard("collagen")

    # Construir stack por niveles
    stack = {
        "base": [],
        "goal_specific": [],
        "optimization": [],
    }

    total_cost = 0

    # Base: Foundational siempre
    foundational = ["vitamin_d3", "omega3", "magnesium"]
    for supp_id in foundational:
        if supp_id in all_supplements and supp_id in SUPPLEMENTS_DATABASE:
            supp = SUPPLEMENTS_DATABASE[supp_id]
            price_range = supp["price_range_usd"].split("-")
            avg_price = (int(price_range[0]) + int(price_range[1])) / 2

            if total_cost + avg_price <= budget_monthly_usd:
                stack["base"].append({
                    "id": supp_id,
                    "name_es": supp["name_es"],
                    "dose": supp["typical_dose"],
                    "timing": supp["timing"],
                    "evidence_level": supp["evidence_level"],
                })
                total_cost += avg_price
                all_supplements.discard(supp_id)

    # Goal-specific
    remaining = list(all_supplements)
    for supp_id in remaining[:3]:
        if supp_id in SUPPLEMENTS_DATABASE:
            supp = SUPPLEMENTS_DATABASE[supp_id]
            price_range = supp["price_range_usd"].split("-")
            avg_price = (int(price_range[0]) + int(price_range[1])) / 2

            if total_cost + avg_price <= budget_monthly_usd:
                stack["goal_specific"].append({
                    "id": supp_id,
                    "name_es": supp["name_es"],
                    "dose": supp["typical_dose"],
                    "timing": supp["timing"],
                    "evidence_level": supp["evidence_level"],
                })
                total_cost += avg_price
                all_supplements.discard(supp_id)

    # Optimization (solo si avanzado y hay presupuesto)
    if experience_level == "advanced":
        remaining = list(all_supplements)
        for supp_id in remaining[:2]:
            if supp_id in SUPPLEMENTS_DATABASE:
                supp = SUPPLEMENTS_DATABASE[supp_id]
                price_range = supp["price_range_usd"].split("-")
                avg_price = (int(price_range[0]) + int(price_range[1])) / 2

                if total_cost + avg_price <= budget_monthly_usd:
                    stack["optimization"].append({
                        "id": supp_id,
                        "name_es": supp["name_es"],
                        "dose": supp["typical_dose"],
                        "timing": supp["timing"],
                        "evidence_level": supp["evidence_level"],
                    })
                    total_cost += avg_price

    # Protocolo de introducción
    introduction_protocol = _create_introduction_protocol(stack)

    return {
        "status": "designed",
        "primary_goal": primary_normalized,
        "secondary_goals": secondary_goals,
        "experience_level": experience_level,
        "stack": stack,
        "total_supplements": (
            len(stack["base"]) + len(stack["goal_specific"]) + len(stack["optimization"])
        ),
        "estimated_monthly_cost_usd": round(total_cost, 2),
        "budget_remaining_usd": round(budget_monthly_usd - total_cost, 2),
        "introduction_protocol": introduction_protocol,
        "synergies_included": _identify_synergies(stack),
        "disclaimer": "Consulta con tu médico antes de comenzar cualquier suplementación.",
    }


def create_timing_protocol(
    supplements: list[str],
    workout_time: str | None = None,
    wake_time: str = "07:00",
    sleep_time: str = "23:00",
) -> dict:
    """Crea un protocolo de timing y dosificación optimizado.

    Args:
        supplements: Lista de IDs de suplementos a programar.
        workout_time: Hora de entrenamiento (si aplica).
        wake_time: Hora de despertar.
        sleep_time: Hora de dormir.

    Returns:
        Dict con protocolo de timing detallado.
    """
    if not supplements:
        return {
            "status": "error",
            "error": "Proporciona una lista de suplementos",
        }

    schedule = {
        "morning_fasted": [],
        "morning_with_breakfast": [],
        "pre_workout": [],
        "post_workout": [],
        "with_lunch": [],
        "afternoon": [],
        "with_dinner": [],
        "before_bed": [],
    }

    supplement_details = []

    for supp_id in supplements:
        supp_normalized = supp_id.lower().replace(" ", "_")

        if supp_normalized not in SUPPLEMENTS_DATABASE:
            continue

        supp = SUPPLEMENTS_DATABASE[supp_normalized]
        timing = supp["timing"].lower()

        detail = {
            "id": supp_normalized,
            "name_es": supp["name_es"],
            "dose": supp["typical_dose"],
            "considerations": supp.get("considerations", [])[:2],
        }

        # Asignar a ventana de tiempo
        if supp_normalized == "probiotics":
            schedule["morning_fasted"].append(detail)
        elif "noche" in timing or supp_normalized in ["magnesium", "ashwagandha", "melatonin"]:
            schedule["before_bed"].append(detail)
        elif "pre-entreno" in timing or supp_normalized in ["caffeine", "citrulline", "beta_alanine"]:
            if workout_time:
                schedule["pre_workout"].append(detail)
            else:
                schedule["morning_with_breakfast"].append(detail)
        elif "grasa" in timing or supp_normalized in ["vitamin_d3", "vitamin_k2", "omega3", "curcumin"]:
            schedule["morning_with_breakfast"].append(detail)
        elif supp_normalized in ["creatine", "collagen"]:
            if workout_time:
                schedule["post_workout"].append(detail)
            else:
                schedule["with_lunch"].append(detail)
        else:
            schedule["with_lunch"].append(detail)

        supplement_details.append(detail)

    # Generar horario legible
    readable_schedule = _generate_readable_schedule(
        schedule, wake_time, sleep_time, workout_time
    )

    # Identificar separaciones necesarias
    separations = _identify_separations(supplements)

    return {
        "status": "created",
        "total_supplements": len(supplement_details),
        "schedule_by_window": schedule,
        "daily_schedule": readable_schedule,
        "required_separations": separations,
        "optimization_tips": [
            "Toma liposolubles (D, K, omega) con comida grasa",
            "Separa hierro y calcio si tomas ambos",
            "Cafeína antes de las 2pm para no afectar sueño",
            "Magnesio y ashwagandha funcionan mejor en la noche",
        ],
        "wake_time": wake_time,
        "sleep_time": sleep_time,
        "workout_time": workout_time,
    }


def check_interactions(
    supplements: list[str],
    medications: list[str] | None = None,
    conditions: list[str] | None = None,
) -> dict:
    """Verifica interacciones entre suplementos, medicamentos y condiciones.

    Args:
        supplements: Lista de suplementos a verificar.
        medications: Medicamentos que toma el usuario.
        conditions: Condiciones médicas del usuario.

    Returns:
        Dict con interacciones identificadas y recomendaciones.
    """
    if not supplements:
        return {
            "status": "error",
            "error": "Proporciona una lista de suplementos",
        }

    interactions_found = []
    synergies_found = []
    warnings = []

    # Normalizar nombres
    supplements_normalized = [s.lower().replace(" ", "_") for s in supplements]
    medications_normalized = [m.lower().replace(" ", "_") for m in (medications or [])]
    conditions_normalized = [c.lower().replace(" ", "_") for c in (conditions or [])]

    # Verificar interacciones de cada suplemento
    for supp in supplements_normalized:
        if supp in INTERACTIONS_DATABASE:
            for interaction in INTERACTIONS_DATABASE[supp]:
                interaction_with = interaction["with"].lower().replace(" ", "_")

                # Interacción con otro suplemento en la lista
                if interaction["type"] == "suplemento" and interaction_with in supplements_normalized:
                    entry = {
                        "supplement_1": supp,
                        "supplement_2": interaction_with,
                        "type": "suplemento-suplemento",
                        "severity": interaction["severity"],
                        "mechanism": interaction["mechanism"],
                        "recommendation": interaction["recommendation"],
                    }
                    if interaction["severity"] == "synergy":
                        synergies_found.append(entry)
                    else:
                        interactions_found.append(entry)

                # Interacción con medicamento
                if interaction["type"] == "medicamento":
                    for med in medications_normalized:
                        if interaction_with in med or med in interaction_with:
                            interactions_found.append({
                                "supplement": supp,
                                "medication": med,
                                "type": "suplemento-medicamento",
                                "severity": interaction["severity"],
                                "mechanism": interaction["mechanism"],
                                "recommendation": interaction["recommendation"],
                            })

    # Verificar condiciones
    condition_warnings = {
        "hipertiroidismo": ["ashwagandha"],
        "embarazo": ["ashwagandha", "melatonin", "lions_mane"],
        "lactancia": ["ashwagandha", "melatonin"],
        "anticoagulantes": ["omega3", "vitamin_k2", "curcumin"],
        "diabetes": [],  # Monitorear glucosa
    }

    for condition in conditions_normalized:
        if condition in condition_warnings:
            for supp in supplements_normalized:
                if supp in condition_warnings[condition]:
                    warnings.append({
                        "supplement": supp,
                        "condition": condition,
                        "warning": f"{supp} puede no ser apropiado con {condition}",
                        "action": "Consultar médico antes de usar",
                    })

    # Priorizar por severidad
    severe = [i for i in interactions_found if i["severity"] == "severe"]
    moderate = [i for i in interactions_found if i["severity"] == "moderate"]
    mild = [i for i in interactions_found if i["severity"] == "mild"]

    return {
        "status": "checked",
        "supplements_checked": supplements_normalized,
        "medications_checked": medications_normalized,
        "conditions_checked": conditions_normalized,
        "total_interactions": len(interactions_found),
        "total_synergies": len(synergies_found),
        "interactions_by_severity": {
            "severe": severe,
            "moderate": moderate,
            "mild": mild,
        },
        "synergies": synergies_found,
        "condition_warnings": warnings,
        "overall_safety": _calculate_safety_score(severe, moderate, mild),
        "recommendations": _generate_safety_recommendations(severe, moderate, warnings),
        "disclaimer": "Esta información no reemplaza consejo médico. Consulta con tu doctor.",
    }


def grade_evidence(
    supplement: str,
    claim: str | None = None,
) -> dict:
    """Evalúa el nivel de evidencia científica de un suplemento o claim.

    Args:
        supplement: Nombre del suplemento a evaluar.
        claim: Claim específico a evaluar (opcional).

    Returns:
        Dict con evaluación de evidencia detallada.
    """
    if not supplement or len(supplement.strip()) < 2:
        return {
            "status": "error",
            "error": "Especifica un suplemento a evaluar",
        }

    supp_normalized = supplement.lower().replace(" ", "_")

    # Buscar en base de datos
    if supp_normalized not in SUPPLEMENTS_DATABASE:
        # Intentar mapeo
        name_mapping = {
            "vitamina_d": "vitamin_d3",
            "omega_3": "omega3",
            "omega-3": "omega3",
            "fish_oil": "omega3",
            "creatina": "creatine",
            "cafeina": "caffeine",
            "melatonina": "melatonin",
        }
        supp_normalized = name_mapping.get(supp_normalized, supp_normalized)

    if supp_normalized not in SUPPLEMENTS_DATABASE:
        return {
            "status": "not_found",
            "supplement": supplement,
            "message": "Suplemento no encontrado en base de datos",
            "general_advice": "Busca estudios en PubMed o Examine.com",
        }

    supp = SUPPLEMENTS_DATABASE[supp_normalized]
    evidence_level = supp["evidence_level"]

    # Detalles de evidencia
    evidence_details = _get_evidence_details(supp_normalized, evidence_level)

    # Evaluar claim específico si se proporciona
    claim_evaluation = None
    if claim:
        claim_evaluation = _evaluate_claim(supp_normalized, claim)

    return {
        "status": "evaluated",
        "supplement": supp["name_es"],
        "supplement_id": supp_normalized,
        "overall_evidence_level": evidence_level,
        "evidence_meaning": {
            "A": "Fuerte: Múltiples meta-análisis y consenso científico",
            "B": "Moderada: Varios RCTs de buena calidad",
            "C": "Limitada: Pocos estudios o resultados mixtos",
            "D": "Insuficiente: Principalmente anecdótica",
        }[evidence_level],
        "evidence_details": evidence_details,
        "claim_evaluation": claim_evaluation,
        "benefits_supported": supp["benefits"],
        "considerations": supp["considerations"],
        "recommended_form": supp["form_recommended"],
        "typical_dose": supp["typical_dose"],
        "research_recommendation": (
            "Evidencia sólida, recomendación general"
            if evidence_level == "A"
            else (
                "Evidencia buena, considerar según contexto"
                if evidence_level == "B"
                else "Evidencia limitada, usar con precaución"
            )
        ),
    }


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================


def _create_introduction_protocol(stack: dict) -> list[dict]:
    """Crea protocolo de introducción gradual."""
    protocol = []
    week = 1

    # Primero base
    for supp in stack.get("base", []):
        protocol.append({
            "week": week,
            "action": f"Introducir {supp['name_es']}",
            "dose": supp["dose"],
            "monitor": "Tolerancia digestiva, energía",
        })
        week += 1

    # Luego goal-specific
    for supp in stack.get("goal_specific", []):
        protocol.append({
            "week": week,
            "action": f"Agregar {supp['name_es']}",
            "dose": supp["dose"],
            "monitor": "Efectos específicos del suplemento",
        })
        week += 1

    # Finalmente optimization
    for supp in stack.get("optimization", []):
        protocol.append({
            "week": week,
            "action": f"Agregar {supp['name_es']} (opcional)",
            "dose": supp["dose"],
            "monitor": "Evaluar si aporta beneficio adicional",
        })
        week += 1

    return protocol


def _identify_synergies(stack: dict) -> list[dict]:
    """Identifica sinergias en el stack."""
    synergies = []
    all_supps = []

    for level in ["base", "goal_specific", "optimization"]:
        all_supps.extend([s["id"] for s in stack.get(level, [])])

    synergy_pairs = [
        ("vitamin_d3", "vitamin_k2", "D3 + K2 optimizan metabolismo del calcio"),
        ("caffeine", "l_theanine", "Cafeína + L-teanina: focus sin ansiedad"),
        ("omega3", "curcumin", "Omega-3 + Curcumina: potente antiinflamatorio"),
        ("creatine", "beta_alanine", "Creatina + Beta-alanina: performance completo"),
    ]

    for s1, s2, benefit in synergy_pairs:
        if s1 in all_supps and s2 in all_supps:
            synergies.append({
                "supplements": [s1, s2],
                "benefit": benefit,
            })

    return synergies


def _generate_readable_schedule(
    schedule: dict, wake: str, sleep: str, workout: str | None
) -> list[dict]:
    """Genera horario legible."""
    readable = []

    # Calcular horas
    wake_hour = int(wake.split(":")[0])
    sleep_hour = int(sleep.split(":")[0])

    time_mapping = {
        "morning_fasted": f"{wake_hour:02d}:00 (al despertar)",
        "morning_with_breakfast": f"{wake_hour:02d}:30 (desayuno)",
        "pre_workout": workout if workout else None,
        "post_workout": None,
        "with_lunch": "13:00 (almuerzo)",
        "afternoon": "16:00 (tarde)",
        "with_dinner": "20:00 (cena)",
        "before_bed": f"{sleep_hour - 1:02d}:00 (antes de dormir)",
    }

    if workout:
        workout_hour = int(workout.split(":")[0])
        time_mapping["pre_workout"] = f"{workout_hour - 1:02d}:00 (pre-entreno)"
        time_mapping["post_workout"] = f"{workout_hour + 1:02d}:00 (post-entreno)"

    for window, supps in schedule.items():
        if supps and time_mapping.get(window):
            readable.append({
                "time": time_mapping[window],
                "supplements": [s["name_es"] for s in supps],
                "notes": [s["dose"] for s in supps],
            })

    return sorted(readable, key=lambda x: x["time"])


def _identify_separations(supplements: list[str]) -> list[dict]:
    """Identifica separaciones necesarias entre suplementos."""
    separations = []

    separation_rules = [
        (["zinc", "hierro"], "2+ horas", "Competencia por absorción"),
        (["calcium", "hierro"], "2+ horas", "Calcio inhibe absorción de hierro"),
        (["magnesium", "zinc"], "OK juntos", "Pueden tomarse juntos"),
        (["caffeine", "melatonin"], "8+ horas", "Efectos opuestos"),
    ]

    supps_lower = [s.lower().replace(" ", "_") for s in supplements]

    for rule_supps, separation, reason in separation_rules:
        if all(s in supps_lower for s in rule_supps):
            separations.append({
                "supplements": rule_supps,
                "separation": separation,
                "reason": reason,
            })

    return separations


def _calculate_safety_score(severe: list, moderate: list, mild: list) -> dict:
    """Calcula score de seguridad."""
    if severe:
        return {
            "score": "LOW",
            "message": "Interacciones severas detectadas - consultar médico",
            "color": "red",
        }
    elif len(moderate) >= 2:
        return {
            "score": "MODERATE",
            "message": "Varias interacciones moderadas - precaución",
            "color": "yellow",
        }
    elif moderate or mild:
        return {
            "score": "ACCEPTABLE",
            "message": "Interacciones menores - monitorear",
            "color": "yellow",
        }
    else:
        return {
            "score": "GOOD",
            "message": "Sin interacciones significativas detectadas",
            "color": "green",
        }


def _generate_safety_recommendations(
    severe: list, moderate: list, warnings: list
) -> list[str]:
    """Genera recomendaciones de seguridad."""
    recommendations = []

    if severe:
        recommendations.append("URGENTE: Consulta con tu médico antes de combinar estos suplementos")
        for interaction in severe:
            recommendations.append(
                f"Evitar: {interaction.get('supplement_1', interaction.get('supplement'))} "
                f"con {interaction.get('supplement_2', interaction.get('medication'))}"
            )

    if moderate:
        recommendations.append("Precaución: Algunas combinaciones requieren ajustes")
        for interaction in moderate[:2]:
            recommendations.append(interaction["recommendation"])

    if warnings:
        for warning in warnings[:2]:
            recommendations.append(warning["action"])

    if not recommendations:
        recommendations.append("Stack parece seguro, pero siempre consulta con tu médico")

    return recommendations


def _get_evidence_details(supp_id: str, level: str) -> dict:
    """Obtiene detalles de evidencia para un suplemento."""
    evidence_data = {
        "creatine": {
            "studies": "500+ estudios en humanos",
            "key_findings": [
                "Aumenta fuerza 5-10% en ejercicio resistencia",
                "Mejora rendimiento en ejercicio alta intensidad",
                "Beneficios cognitivos en poblaciones específicas",
            ],
            "limitations": "Responders vs non-responders",
        },
        "vitamin_d3": {
            "studies": "Miles de estudios observacionales y RCTs",
            "key_findings": [
                "Deficiencia asociada con múltiples problemas de salud",
                "Suplementación beneficiosa si niveles bajos",
                "Dosis óptima aún debatida",
            ],
            "limitations": "Beneficios menos claros si niveles ya óptimos",
        },
        "omega3": {
            "studies": "Extensiva literatura, incluyendo meta-análisis",
            "key_findings": [
                "Beneficios cardiovasculares establecidos",
                "Propiedades antiinflamatorias",
                "Importancia para desarrollo cerebral",
            ],
            "limitations": "Dosis y ratio EPA:DHA óptimos variables",
        },
        "ashwagandha": {
            "studies": "Creciente número de RCTs",
            "key_findings": [
                "Reduce cortisol y estrés percibido",
                "Mejora ansiedad en múltiples estudios",
                "Posibles beneficios en testosterona",
            ],
            "limitations": "Mecanismos no completamente entendidos",
        },
    }

    default = {
        "studies": "Evidencia variable según el claim",
        "key_findings": ["Consultar literatura específica"],
        "limitations": "Más investigación necesaria",
    }

    return evidence_data.get(supp_id, default)


def _evaluate_claim(supp_id: str, claim: str) -> dict:
    """Evalúa un claim específico."""
    claim_lower = claim.lower()

    claim_evaluations = {
        "creatine": {
            "fuerza": ("A", "Bien establecido por múltiples estudios"),
            "musculo": ("A", "Aumenta masa muscular con entrenamiento"),
            "cognición": ("B", "Evidencia emergente, especialmente en déficit"),
        },
        "omega3": {
            "corazon": ("A", "Beneficios cardiovasculares bien documentados"),
            "cerebro": ("B", "Importante para estructura, beneficios variables"),
            "inflamacion": ("A", "Propiedades antiinflamatorias establecidas"),
        },
        "vitamin_d3": {
            "huesos": ("A", "Esencial para salud ósea"),
            "inmunidad": ("B", "Evidencia de rol en sistema inmune"),
            "estado de ánimo": ("B", "Asociaciones en estudios observacionales"),
        },
    }

    if supp_id in claim_evaluations:
        for keyword, (level, explanation) in claim_evaluations[supp_id].items():
            if keyword in claim_lower:
                return {
                    "claim": claim,
                    "evidence_level": level,
                    "evaluation": explanation,
                    "verdict": (
                        "Claim bien soportado"
                        if level == "A"
                        else "Claim moderadamente soportado"
                    ),
                }

    return {
        "claim": claim,
        "evidence_level": "C",
        "evaluation": "Claim específico no evaluado en base de datos",
        "verdict": "Investigar literatura específica",
    }


# =============================================================================
# EXPORTACIÓN DE TOOLS
# =============================================================================


recommend_supplements_tool = FunctionTool(recommend_supplements)
design_stack_tool = FunctionTool(design_stack)
create_timing_protocol_tool = FunctionTool(create_timing_protocol)
check_interactions_tool = FunctionTool(check_interactions)
grade_evidence_tool = FunctionTool(grade_evidence)


ALL_TOOLS = [
    recommend_supplements_tool,
    design_stack_tool,
    create_timing_protocol_tool,
    check_interactions_tool,
    grade_evidence_tool,
]


__all__ = [
    # Functions
    "recommend_supplements",
    "design_stack",
    "create_timing_protocol",
    "check_interactions",
    "grade_evidence",
    # Tools
    "recommend_supplements_tool",
    "design_stack_tool",
    "create_timing_protocol_tool",
    "check_interactions_tool",
    "grade_evidence_tool",
    "ALL_TOOLS",
    # Data
    "SUPPLEMENTS_DATABASE",
    "INTERACTIONS_DATABASE",
    "GOAL_TO_SUPPLEMENTS",
    "TIMING_WINDOWS",
    # Enums
    "EvidenceLevel",
    "InteractionSeverity",
    "SupplementCategory",
    "GoalType",
]
