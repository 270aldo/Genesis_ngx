"""Tools para LOGOS - Especialista en Educación.

Este módulo contiene las herramientas educativas y las bases de conocimiento
que LOGOS usa para explicar conceptos, presentar evidencia, desmentir mitos,
crear contenido educativo y generar quizzes.

MVP Scope:
- ~20 conceptos (4 por dominio)
- ~15 mitos (3 por dominio)
- ~10 evidencias clave
"""

from __future__ import annotations

from enum import Enum
import random

from google.adk.tools import FunctionTool


# =============================================================================
# ENUMS Y TIPOS
# =============================================================================


class Domain(str, Enum):
    """Dominios de conocimiento."""

    FITNESS = "fitness"
    NUTRITION = "nutrition"
    BEHAVIOR = "behavior"
    RECOVERY = "recovery"
    WOMENS_HEALTH = "womens_health"


class LearningLevel(str, Enum):
    """Niveles de aprendizaje del usuario."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class EvidenceGrade(str, Enum):
    """Grados de evidencia científica."""

    A = "A"  # Fuerte - múltiples RCTs de calidad
    B = "B"  # Moderada - algunos RCTs o meta-análisis
    C = "C"  # Limitada - estudios observacionales
    D = "D"  # Insuficiente - evidencia anecdótica


class QuestionType(str, Enum):
    """Tipos de preguntas para quizzes."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    SCENARIO = "scenario"


class Difficulty(str, Enum):
    """Niveles de dificultad para quizzes."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# =============================================================================
# BASE DE DATOS: CONCEPTOS (~20)
# =============================================================================


CONCEPTS_DATABASE: dict[str, dict] = {
    # -------------------------------------------------------------------------
    # FITNESS (4 conceptos)
    # -------------------------------------------------------------------------
    "progressive_overload": {
        "domain": "fitness",
        "name_es": "Sobrecarga Progresiva",
        "definition": "Incremento gradual y sistemático del estrés de entrenamiento para forzar adaptaciones continuas",
        "why_important": "Es el principio fundamental para ganar fuerza y músculo. Sin sobrecarga, el cuerpo no tiene razón para adaptarse.",
        "levels": {
            "beginner": "Cada semana intenta hacer una repetición más o añadir un poco de peso. Tu cuerpo se adapta a lo que le pides.",
            "intermediate": "Varía entre aumentar peso, repeticiones, series o reducir descansos. Periodiza para evitar estancamientos.",
            "advanced": "Usa periodización ondulante, bloques de acumulación/intensificación, y maneja fatiga acumulada estratégicamente.",
        },
        "related_concepts": ["hypertrophy", "periodization", "deload"],
        "common_mistakes": [
            "Aumentar demasiado rápido (lesiones)",
            "Ignorar señales de fatiga acumulada",
            "No trackear progreso",
        ],
        "analogy": "Es como subir una escalera: cada peldaño es un poco más alto que el anterior. Si saltas muchos de golpe, te caes.",
    },
    "hypertrophy": {
        "domain": "fitness",
        "name_es": "Hipertrofia Muscular",
        "definition": "Aumento del tamaño de las fibras musculares como respuesta al entrenamiento",
        "why_important": "Es el mecanismo por el cual los músculos crecen. Entenderlo permite optimizar el entrenamiento.",
        "levels": {
            "beginner": "Tus músculos crecen cuando los trabajas lo suficiente y les das comida y descanso para recuperarse.",
            "intermediate": "Ocurre por daño muscular, tensión mecánica y estrés metabólico. El volumen total es el driver principal.",
            "advanced": "La tensión mecánica parece ser el estímulo principal. 10-20 series semanales por grupo muscular es el rango óptimo para la mayoría.",
        },
        "related_concepts": ["progressive_overload", "protein_synthesis", "volume"],
        "common_mistakes": [
            "Priorizar 'sentir el músculo' sobre carga progresiva",
            "Volumen excesivo sin recuperación",
            "Ignorar la importancia de la proteína",
        ],
        "analogy": "Tu músculo es como una casa que reconstruyes constantemente. El entrenamiento la 'daña', y la proteína son los ladrillos para hacerla más grande.",
    },
    "periodization": {
        "domain": "fitness",
        "name_es": "Periodización",
        "definition": "Organización sistemática del entrenamiento en fases con diferentes objetivos y cargas",
        "why_important": "Permite progreso a largo plazo, previene estancamientos y reduce riesgo de sobreentrenamiento.",
        "levels": {
            "beginner": "Alterna semanas más intensas con semanas más suaves. No puedes ir al máximo siempre.",
            "intermediate": "Organiza mesociclos de 4-6 semanas con fases de acumulación (volumen) e intensificación (carga).",
            "advanced": "Considera periodización ondulante diaria (DUP), bloques de especialización, y picos para competición.",
        },
        "related_concepts": ["progressive_overload", "deload", "fatigue_management"],
        "common_mistakes": [
            "Entrenar siempre al máximo",
            "No incluir semanas de descarga",
            "Cambiar programa cada semana",
        ],
        "analogy": "Es como preparar un examen importante: no estudias igual de intenso todos los días. Hay días de aprender, días de practicar, y días de descansar.",
    },
    "mind_muscle_connection": {
        "domain": "fitness",
        "name_es": "Conexión Mente-Músculo",
        "definition": "Capacidad de activar conscientemente y sentir el trabajo de un músculo específico durante un ejercicio",
        "why_important": "Puede mejorar la activación muscular, especialmente útil para ejercicios de aislamiento e hipertrofia.",
        "levels": {
            "beginner": "Intenta 'sentir' el músculo que estás trabajando. Si haces curl de bíceps, siente cómo se contrae.",
            "intermediate": "Es más útil en aislamiento que en compuestos pesados. No sacrifiques carga por 'sentir' en ejercicios como sentadilla.",
            "advanced": "La evidencia muestra beneficio para hipertrofia en aislamiento. En compuestos pesados, enfócate en técnica y fuerza.",
        },
        "related_concepts": ["hypertrophy", "isolation_exercises", "technique"],
        "common_mistakes": [
            "Usar peso muy ligero solo para 'sentir'",
            "Intentar conexión en ejercicios muy pesados",
            "Confundirlo con el único factor de crecimiento",
        ],
        "analogy": "Es como aprender a mover las orejas: al principio no puedes, pero con práctica desarrollas control sobre músculos específicos.",
    },
    # -------------------------------------------------------------------------
    # NUTRITION (4 conceptos)
    # -------------------------------------------------------------------------
    "energy_balance": {
        "domain": "nutrition",
        "name_es": "Balance Energético",
        "definition": "Relación entre las calorías que consumes y las que gastas. Determina si ganas, pierdes o mantienes peso.",
        "why_important": "Es la ley fundamental del peso corporal. Sin entenderlo, es imposible controlar la composición corporal.",
        "levels": {
            "beginner": "Si comes más de lo que gastas, subes. Si comes menos, bajas. Así de simple es la base.",
            "intermediate": "Tu TDEE (gasto total) incluye metabolismo basal + actividad + TEF. El déficit óptimo es 300-500 kcal para preservar músculo.",
            "advanced": "Considera adaptación metabólica, NEAT, y cómo el déficit prolongado afecta hormonas. Usa refeeds estratégicos.",
        },
        "related_concepts": ["tdee", "caloric_deficit", "surplus", "body_composition"],
        "common_mistakes": [
            "Ignorar calorías líquidas",
            "Subestimar porciones",
            "Déficits demasiado agresivos",
        ],
        "analogy": "Tu cuerpo es como una cuenta bancaria de energía. Si depositas (comes) más de lo que retiras (gastas), el balance crece.",
    },
    "protein_synthesis": {
        "domain": "nutrition",
        "name_es": "Síntesis Proteica Muscular",
        "definition": "Proceso por el cual el cuerpo construye nuevas proteínas musculares, esencial para la recuperación y el crecimiento",
        "why_important": "Entenderlo permite optimizar timing y distribución de proteína para máxima ganancia muscular.",
        "levels": {
            "beginner": "Después de entrenar, tu cuerpo usa la proteína que comes para reparar y fortalecer los músculos.",
            "intermediate": "Se eleva post-entrenamiento por 24-48h. Distribuir proteína en 3-4 comidas (30-40g cada una) es más efectivo que una sola grande.",
            "advanced": "El umbral de leucina (~2.5g) es clave para maximizar MPS. La 'ventana anabólica' es más amplia de lo que se pensaba.",
        },
        "related_concepts": ["hypertrophy", "protein_timing", "amino_acids"],
        "common_mistakes": [
            "Obsesionarse con timing exacto post-entreno",
            "Consumir toda la proteína en una comida",
            "Ignorar calidad de proteína (aminoácidos esenciales)",
        ],
        "analogy": "Imagina trabajadores construyendo un muro. La proteína son los ladrillos, y hay un límite de cuántos pueden usar por hora.",
    },
    "macronutrients": {
        "domain": "nutrition",
        "name_es": "Macronutrientes",
        "definition": "Los tres nutrientes que aportan calorías: proteínas (4 kcal/g), carbohidratos (4 kcal/g) y grasas (9 kcal/g)",
        "why_important": "Cada macro tiene funciones específicas. Su distribución afecta rendimiento, composición corporal y salud.",
        "levels": {
            "beginner": "Proteína para músculos, carbos para energía, grasas para hormonas. Todos son importantes.",
            "intermediate": "Prioriza proteína (1.6-2.2g/kg). Distribuye carbos y grasas según preferencia, pero no elimines ninguno.",
            "advanced": "Ciclado de carbos puede optimizar rendimiento y composición corporal. Mínimo 0.5g/kg de grasa para hormonas.",
        },
        "related_concepts": ["energy_balance", "protein_synthesis", "carb_cycling"],
        "common_mistakes": [
            "Demonizar un macro (carbos o grasas)",
            "Proteína insuficiente en déficit",
            "Grasas demasiado bajas",
        ],
        "analogy": "Son como los materiales de construcción: necesitas cemento (proteína), ladrillos (carbos) y electricidad (grasas). Sin uno, la casa no funciona.",
    },
    "nutrient_timing": {
        "domain": "nutrition",
        "name_es": "Timing de Nutrientes",
        "definition": "Estrategia de cuándo consumir ciertos nutrientes en relación al entrenamiento y el día",
        "why_important": "Puede optimizar rendimiento y recuperación, aunque importa menos que el total diario.",
        "levels": {
            "beginner": "Come algo antes y después de entrenar. El total del día importa más que el momento exacto.",
            "intermediate": "Carbos pre-entreno mejoran rendimiento. Proteína post-entreno en las siguientes horas (no minutos) es suficiente.",
            "advanced": "La 'ventana anabólica' es de horas, no minutos. La distribución de proteína (cada 3-5h) importa más que el timing post-entreno.",
        },
        "related_concepts": ["protein_synthesis", "glycogen", "performance"],
        "common_mistakes": [
            "Obsesión con los 30 minutos post-entreno",
            "Entrenar en ayunas sin necesidad",
            "Suplementos pre-entreno como prioridad sobre alimentación",
        ],
        "analogy": "Es como regar plantas: importa que reciban agua suficiente, pero no necesitas cronometrar cada gota al segundo.",
    },
    # -------------------------------------------------------------------------
    # BEHAVIOR (4 conceptos)
    # -------------------------------------------------------------------------
    "habit_loop": {
        "domain": "behavior",
        "name_es": "Ciclo del Hábito",
        "definition": "El patrón neurológico de Señal → Rutina → Recompensa que gobierna los hábitos automáticos",
        "why_important": "Entenderlo permite diseñar nuevos hábitos y modificar los existentes de forma efectiva.",
        "levels": {
            "beginner": "Todo hábito tiene un disparador (señal), una acción (rutina) y un beneficio (recompensa). Identifica los tuyos.",
            "intermediate": "Para crear un hábito, diseña una señal clara, haz la rutina ridículamente fácil al inicio, y celebra inmediatamente.",
            "advanced": "Los hábitos se 'apilan' sobre otros. El contexto (ambiente) es más poderoso que la motivación.",
        },
        "related_concepts": ["habit_stacking", "environment_design", "intrinsic_motivation"],
        "common_mistakes": [
            "Depender solo de motivación",
            "Hacer el hábito nuevo demasiado grande",
            "No celebrar pequeños éxitos",
        ],
        "analogy": "Es como un sendero en el bosque: cuanto más lo caminas, más marcado queda. Al inicio cuesta, pero luego es automático.",
    },
    "intrinsic_motivation": {
        "domain": "behavior",
        "name_es": "Motivación Intrínseca",
        "definition": "Motivación que viene de dentro: disfrute, curiosidad, satisfacción personal, no recompensas externas",
        "why_important": "La motivación intrínseca es más sostenible a largo plazo que depender de recompensas externas.",
        "levels": {
            "beginner": "Encuentra algo que disfrutes del ejercicio, no solo el resultado. El proceso también cuenta.",
            "intermediate": "Autonomía, maestría y propósito son los tres pilares. Busca actividades donde los sientas.",
            "advanced": "Las recompensas externas pueden socavar la motivación intrínseca (efecto de sobrejustificación). Úsalas con cuidado.",
        },
        "related_concepts": ["habit_loop", "self_determination", "consistency"],
        "common_mistakes": [
            "Depender solo de resultados para motivarse",
            "Compararse constantemente con otros",
            "Ignorar qué tipos de ejercicio disfrutan",
        ],
        "analogy": "Es la diferencia entre jugar un videojuego porque te divierte vs porque te pagan. Sin pago, ¿seguirías jugando?",
    },
    "cognitive_dissonance": {
        "domain": "behavior",
        "name_es": "Disonancia Cognitiva",
        "definition": "Incomodidad mental cuando tus acciones no coinciden con tus creencias o valores",
        "why_important": "Entenderlo ayuda a alinear comportamiento con metas y a no auto-sabotearte.",
        "levels": {
            "beginner": "Cuando dices que la salud es importante pero no haces ejercicio, esa incomodidad es disonancia.",
            "intermediate": "Puedes resolverla cambiando la acción (hacer ejercicio) o la creencia (la salud no importa tanto). Lo segundo es auto-sabotaje.",
            "advanced": "Usa compromisos públicos y cambios de identidad para aprovechar la disonancia a tu favor.",
        },
        "related_concepts": ["identity_change", "commitment", "self_sabotage"],
        "common_mistakes": [
            "Justificar malos hábitos para reducir disonancia",
            "No reconocer la incomodidad como señal útil",
            "Comprometerse sin accountability",
        ],
        "analogy": "Es como una alarma interna que suena cuando lo que haces no coincide con quien crees que eres.",
    },
    "implementation_intentions": {
        "domain": "behavior",
        "name_es": "Intenciones de Implementación",
        "definition": "Planes específicos de 'si-entonces': Si [situación X], entonces [haré Y]",
        "why_important": "Duplican o triplican las probabilidades de seguir con un comportamiento vs solo tener la intención.",
        "levels": {
            "beginner": "En vez de 'voy a hacer ejercicio', di 'los lunes a las 7am iré al gym antes del trabajo'.",
            "intermediate": "Planifica también obstáculos: 'Si no puedo ir al gym, haré 20 minutos de ejercicio en casa'.",
            "advanced": "Combina con habit stacking y diseño de ambiente para máxima efectividad.",
        },
        "related_concepts": ["habit_loop", "planning", "obstacle_planning"],
        "common_mistakes": [
            "Planes vagos ('haré más ejercicio')",
            "No planificar para obstáculos",
            "Demasiados planes a la vez",
        ],
        "analogy": "Es como programar una cita en tu calendario vs decir 'algún día nos vemos'. La especificidad hace que suceda.",
    },
    # -------------------------------------------------------------------------
    # RECOVERY (4 conceptos)
    # -------------------------------------------------------------------------
    "supercompensation": {
        "domain": "recovery",
        "name_es": "Supercompensación",
        "definition": "Fenómeno donde el cuerpo se recupera más allá del nivel inicial después de un estímulo de entrenamiento",
        "why_important": "Es el mecanismo fundamental por el cual mejoramos. Sin entenderlo, es fácil sobreentrenar o subentrenar.",
        "levels": {
            "beginner": "Después de entrenar y descansar, tu cuerpo queda un poco más fuerte que antes. Pero necesita tiempo.",
            "intermediate": "El timing del siguiente entreno importa: muy pronto no te recuperas, muy tarde pierdes la ganancia.",
            "advanced": "El modelo es simplificado - diferentes sistemas (neural, muscular, metabólico) tienen diferentes curvas de recuperación.",
        },
        "related_concepts": ["recovery", "periodization", "fatigue_management"],
        "common_mistakes": [
            "No dar suficiente tiempo de recuperación",
            "Esperar demasiado entre sesiones",
            "Ignorar señales de fatiga acumulada",
        ],
        "analogy": "Es como una ola: el entrenamiento te hunde, el descanso te eleva más alto que antes, pero si no surfeas la ola a tiempo, baja.",
    },
    "sleep_architecture": {
        "domain": "recovery",
        "name_es": "Arquitectura del Sueño",
        "definition": "Estructura de las fases del sueño: ligero, profundo (SWS) y REM, cada una con funciones diferentes",
        "why_important": "El sueño profundo es cuando ocurre la mayor recuperación física. El REM es crucial para memoria y aprendizaje motor.",
        "levels": {
            "beginner": "Duerme 7-9 horas. La calidad importa tanto como la cantidad - horarios consistentes ayudan.",
            "intermediate": "El sueño profundo ocurre más en la primera mitad de la noche. El REM en la segunda. Ambos importan.",
            "advanced": "La privación de sueño reduce testosterona, aumenta cortisol, y afecta decisiones alimentarias. Es tan importante como el entrenamiento.",
        },
        "related_concepts": ["recovery", "hormones", "performance"],
        "common_mistakes": [
            "Sacrificar sueño por entrenar más",
            "Horarios de sueño inconsistentes",
            "Pantallas antes de dormir",
        ],
        "analogy": "El sueño es como el pit stop en una carrera: puedes saltarte algunos, pero eventualmente tu auto se rompe.",
    },
    "active_recovery": {
        "domain": "recovery",
        "name_es": "Recuperación Activa",
        "definition": "Actividad de baja intensidad que promueve recuperación sin añadir fatiga significativa",
        "why_important": "Puede acelerar recuperación al aumentar flujo sanguíneo sin estresar los sistemas de recuperación.",
        "levels": {
            "beginner": "En días de descanso, una caminata suave o estiramiento ligero puede ayudarte a sentir mejor que el reposo total.",
            "intermediate": "Mantén la intensidad muy baja (40-50% FC máx). Si terminas cansado, fue demasiado.",
            "advanced": "Considera el tipo de fatiga: la recuperación activa ayuda más con fatiga metabólica que con daño muscular severo.",
        },
        "related_concepts": ["supercompensation", "deload", "fatigue_management"],
        "common_mistakes": [
            "Hacer 'recuperación activa' demasiado intensa",
            "Confundirla con un entrenamiento real",
            "Ignorar cuándo el cuerpo necesita reposo total",
        ],
        "analogy": "Es como limpiar una herida suavemente vs dejarla quieta vs frotarla fuerte. El movimiento suave ayuda, el exceso empeora.",
    },
    "stress_recovery_balance": {
        "domain": "recovery",
        "name_es": "Balance Estrés-Recuperación",
        "definition": "El equilibrio entre el estrés total (entrenamiento + vida) y la capacidad de recuperación",
        "why_important": "El cuerpo no distingue entre tipos de estrés. Una semana de trabajo intensa requiere ajustar el entrenamiento.",
        "levels": {
            "beginner": "Si tu vida está muy estresante, entrena menos intenso. El estrés del gym se suma al del trabajo.",
            "intermediate": "Considera tu 'presupuesto de estrés': trabajo, relaciones, sueño, nutrición, todo afecta cuánto puedes entrenar.",
            "advanced": "Monitorea HRV, calidad de sueño, y rendimiento para ajustar volumen/intensidad en tiempo real.",
        },
        "related_concepts": ["supercompensation", "periodization", "cortisol"],
        "common_mistakes": [
            "Ignorar estrés de vida al programar entreno",
            "No reducir volumen en semanas difíciles",
            "Usar el gym como 'escape' cuando el cuerpo necesita descanso",
        ],
        "analogy": "Tu capacidad de recuperación es como un vaso de agua. Cada estrés (trabajo, gym, problemas) le quita agua. Si se vacía, te quemas.",
    },
    # -------------------------------------------------------------------------
    # WOMEN'S HEALTH (4 conceptos)
    # -------------------------------------------------------------------------
    "menstrual_phases": {
        "domain": "womens_health",
        "name_es": "Fases del Ciclo Menstrual",
        "definition": "Las cuatro fases del ciclo: menstrual, folicular, ovulatoria y lútea, cada una con características hormonales distintas",
        "why_important": "Entrenamiento y nutrición pueden optimizarse según la fase para mejor rendimiento y bienestar.",
        "levels": {
            "beginner": "Tu cuerpo no es igual todos los días del mes. Algunas semanas tendrás más energía que otras, y está bien.",
            "intermediate": "Fase folicular = estrógeno subiendo = mejor momento para PRs. Fase lútea = progesterona alta = puede requerir ajustes.",
            "advanced": "La variación individual es alta. Usa tracking para encontrar tus patrones personales antes de hacer cambios drásticos.",
        },
        "related_concepts": ["hormonal_fluctuations", "training_adaptation", "nutrition_adaptation"],
        "common_mistakes": [
            "Aplicar reglas generales sin personalizar",
            "Ignorar cómo te sientes por seguir un plan rígido",
            "No trackear para identificar patrones",
        ],
        "analogy": "Tu ciclo es como las estaciones del año interno: cada fase tiene su clima, y puedes vestirte (entrenar) apropiadamente.",
    },
    "hormonal_fluctuations": {
        "domain": "womens_health",
        "name_es": "Fluctuaciones Hormonales",
        "definition": "Cambios en estrógeno y progesterona a lo largo del ciclo que afectan energía, fuerza, recuperación y metabolismo",
        "why_important": "Explica por qué el rendimiento y bienestar varían a lo largo del mes. No eres inconsistente, eres cíclica.",
        "levels": {
            "beginner": "Tus hormonas cambian cada semana. Esto afecta energía, humor, y hasta cómo respondes al ejercicio.",
            "intermediate": "Estrógeno alto = mejor sensibilidad a insulina, más fuerza potencial. Progesterona alta = metabolismo ligeramente elevado, posible retención de líquidos.",
            "advanced": "La investigación en mujeres es limitada. Usa principios generales pero prioriza tu experiencia personal.",
        },
        "related_concepts": ["menstrual_phases", "training_adaptation", "metabolism"],
        "common_mistakes": [
            "Comparar rendimiento sin considerar fase del ciclo",
            "Frustrarse por variaciones normales",
            "Ignorar síntomas que podrían indicar desequilibrios",
        ],
        "analogy": "Las hormonas son como el termostato interno: ajustan muchas funciones, y es normal que la 'temperatura' cambie.",
    },
    "perimenopause": {
        "domain": "womens_health",
        "name_es": "Perimenopausia",
        "definition": "Período de transición hacia la menopausia (típicamente 40-50 años) con ciclos irregulares y síntomas variados",
        "why_important": "Requiere adaptaciones en entrenamiento y nutrición. Es un proceso natural, no una enfermedad.",
        "levels": {
            "beginner": "Es la transición natural hacia la menopausia. Los ciclos se vuelven irregulares y pueden aparecer nuevos síntomas.",
            "intermediate": "Prioriza entrenamiento de fuerza para preservar masa muscular y ósea. La proteína se vuelve aún más importante.",
            "advanced": "Los síntomas varían enormemente entre mujeres. Trabaja con profesionales de salud para manejo personalizado.",
        },
        "related_concepts": ["menstrual_phases", "bone_health", "muscle_preservation"],
        "common_mistakes": [
            "Reducir ejercicio cuando es más importante que nunca",
            "No aumentar proteína para compensar cambios",
            "No buscar ayuda profesional para síntomas severos",
        ],
        "analogy": "Es como cambiar de temporada: el cuerpo se está adaptando a un nuevo 'clima hormonal'. Toma tiempo y requiere ajustes.",
    },
    "training_cycle_sync": {
        "domain": "womens_health",
        "name_es": "Sincronización de Entrenamiento con el Ciclo",
        "definition": "Adaptar intensidad, volumen y tipo de entrenamiento según la fase del ciclo menstrual",
        "why_important": "Puede optimizar resultados y reducir riesgo de lesiones aprovechando las ventajas de cada fase.",
        "levels": {
            "beginner": "En general: más intensidad cuando te sientes bien (folicular/ovulatoria), más moderado cuando no (menstrual/lútea tardía).",
            "intermediate": "Fase folicular = progresión agresiva. Ovulación = PRs potenciales pero cuidado con ligamentos. Lútea = mantén pero no fuerces.",
            "advanced": "La evidencia es mixta sobre beneficios. Algunos estudios muestran ventaja, otros no. Personaliza basándote en tu respuesta.",
        },
        "related_concepts": ["menstrual_phases", "hormonal_fluctuations", "periodization"],
        "common_mistakes": [
            "Ser demasiado rígida con las 'reglas'",
            "Ignorar completamente el ciclo",
            "No escuchar al cuerpo por seguir un plan",
        ],
        "analogy": "Es como surfear: aprovechas las olas cuando vienen, no luchas contra el océano.",
    },
}


# =============================================================================
# BASE DE DATOS: EVIDENCIA (~10)
# =============================================================================


EVIDENCE_DATABASE: dict[str, dict] = {
    "creatine_muscle": {
        "claim": "La creatina aumenta masa muscular y fuerza",
        "verdict": True,
        "evidence_grade": "A",
        "domain": "nutrition",
        "key_studies": [
            {
                "authors": "Kreider et al.",
                "year": 2017,
                "type": "Position Stand (ISSN)",
                "finding": "Aumenta masa magra +1-2kg en 4-12 semanas de entrenamiento",
                "doi": "10.1186/s12970-017-0173-z",
            },
            {
                "authors": "Rawson & Volek",
                "year": 2003,
                "type": "Meta-análisis",
                "finding": "Mejora fuerza máxima en press de banca y sentadilla",
            },
        ],
        "mechanism": "Aumenta fosfocreatina intramuscular, permitiendo más ATP para contracciones de alta intensidad. Más energía = más repeticiones = más volumen efectivo.",
        "practical_takeaway": "3-5g/día de creatina monohidrato. No necesita fase de carga. Tómala cuando sea conveniente.",
        "limitations": "La respuesta individual varía. Algunos son 'no-respondedores'. La ganancia de peso inicial es agua intramuscular.",
    },
    "protein_amount": {
        "claim": "Necesitas 1.6-2.2g de proteína por kg de peso para máxima ganancia muscular",
        "verdict": True,
        "evidence_grade": "A",
        "domain": "nutrition",
        "key_studies": [
            {
                "authors": "Morton et al.",
                "year": 2018,
                "type": "Meta-análisis",
                "finding": "Beneficios se maximizan alrededor de 1.6g/kg, con poco beneficio adicional hasta 2.2g/kg",
            },
            {
                "authors": "Schoenfeld & Aragon",
                "year": 2018,
                "type": "Revisión sistemática",
                "finding": "Recomienda 1.6-2.2g/kg para optimizar adaptaciones de entrenamiento",
            },
        ],
        "mechanism": "Provee aminoácidos esenciales para síntesis proteica muscular. La leucina es particularmente importante como 'interruptor' de MPS.",
        "practical_takeaway": "Apunta a ~2g/kg si entrenas fuerza. Distribuye en 3-4 comidas. Prioriza fuentes de calidad (alto en leucina).",
        "limitations": "Estas recomendaciones son para personas que entrenan. Más no es necesariamente mejor.",
    },
    "anabolic_window": {
        "claim": "Debes consumir proteína dentro de 30 minutos post-entreno (ventana anabólica)",
        "verdict": "Parcialmente falso",
        "evidence_grade": "B",
        "domain": "nutrition",
        "key_studies": [
            {
                "authors": "Schoenfeld et al.",
                "year": 2013,
                "type": "Meta-análisis",
                "finding": "El efecto del timing desaparece cuando se controla por proteína total diaria",
            },
            {
                "authors": "Aragon & Schoenfeld",
                "year": 2013,
                "type": "Revisión",
                "finding": "La 'ventana anabólica' es más amplia de lo que se pensaba (4-6 horas mínimo)",
            },
        ],
        "mechanism": "La síntesis proteica muscular se eleva post-entreno, pero por horas, no minutos. El total diario y la distribución importan más.",
        "practical_takeaway": "Come proteína en algún momento después del entreno (horas, no minutos). Prioriza total diario y distribución.",
        "limitations": "Si entrenas en ayunas prolongado, puede importar más. Para la mayoría, no es crítico.",
    },
    "spot_reduction_fat": {
        "claim": "Puedes quemar grasa de zonas específicas ejercitando esa área",
        "verdict": False,
        "evidence_grade": "A",
        "domain": "fitness",
        "key_studies": [
            {
                "authors": "Vispute et al.",
                "year": 2011,
                "type": "RCT",
                "finding": "6 semanas de ejercicios abdominales no redujeron grasa abdominal más que el grupo control",
            },
            {
                "authors": "Ramírez-Campillo et al.",
                "year": 2013,
                "type": "RCT",
                "finding": "Entrenamiento unilateral de pierna no redujo grasa local preferentemente",
            },
        ],
        "mechanism": "La lipólisis (liberación de grasa) ocurre sistémicamente en respuesta a déficit calórico. El cuerpo decide de dónde tomar grasa según genética y hormonas.",
        "practical_takeaway": "Para perder grasa de cualquier zona: déficit calórico + entrenamiento de fuerza para preservar músculo. No hay atajos localizados.",
        "limitations": "El entrenamiento de una zona puede mejorar tono muscular, que da apariencia diferente, pero no quema grasa local.",
    },
    "progressive_overload_necessity": {
        "claim": "La sobrecarga progresiva es necesaria para seguir ganando fuerza y músculo",
        "verdict": True,
        "evidence_grade": "A",
        "domain": "fitness",
        "key_studies": [
            {
                "authors": "Schoenfeld et al.",
                "year": 2017,
                "type": "Meta-análisis",
                "finding": "El volumen progresivo es un predictor principal de hipertrofia",
            },
            {
                "authors": "Fonseca et al.",
                "year": 2014,
                "type": "RCT",
                "finding": "Grupos con progresión ganaron significativamente más fuerza que grupos con carga constante",
            },
        ],
        "mechanism": "El cuerpo se adapta al estrés. Sin aumento de demanda (peso, reps, volumen), no hay razón fisiológica para adaptarse más.",
        "practical_takeaway": "Trackea tus entrenamientos. Intenta progreso semanal o mensual en alguna variable (peso, reps, series).",
        "limitations": "La progresión no es lineal indefinidamente. Periodización y deloads son necesarios.",
    },
    "sleep_muscle_growth": {
        "claim": "El sueño inadecuado reduce significativamente las ganancias musculares",
        "verdict": True,
        "evidence_grade": "B",
        "domain": "recovery",
        "key_studies": [
            {
                "authors": "Dattilo et al.",
                "year": 2011,
                "type": "Revisión",
                "finding": "La privación de sueño reduce testosterona y aumenta cortisol, desfavoreciendo anabolismo",
            },
            {
                "authors": "Nedeltcheva et al.",
                "year": 2010,
                "type": "RCT",
                "finding": "Restricción de sueño en déficit calórico aumentó pérdida de masa magra significativamente",
            },
        ],
        "mechanism": "Durante sueño profundo se libera hormona del crecimiento. Sueño inadecuado aumenta cortisol y reduce testosterona. Afecta recuperación y síntesis proteica.",
        "practical_takeaway": "Prioriza 7-9 horas de sueño de calidad. Es tan importante como el entrenamiento y la nutrición.",
        "limitations": "La sensibilidad individual varía. Algunos funcionan bien con menos, pero son excepciones.",
    },
    "carbs_night_fat": {
        "claim": "Comer carbohidratos de noche engorda más que comerlos de día",
        "verdict": False,
        "evidence_grade": "B",
        "domain": "nutrition",
        "key_studies": [
            {
                "authors": "Sofer et al.",
                "year": 2011,
                "type": "RCT",
                "finding": "Grupo que comió carbos principalmente de noche perdió más grasa que grupo con distribución uniforme",
            },
            {
                "authors": "Keim et al.",
                "year": 1997,
                "type": "Crossover",
                "finding": "El timing de calorías no afectó pérdida de peso cuando calorías totales fueron iguales",
            },
        ],
        "mechanism": "El balance energético total determina cambios de peso, no el timing. El metabolismo no 'se apaga' de noche.",
        "practical_takeaway": "Come carbos cuando te funcione mejor. Si entrenas de noche, carbos de noche tiene sentido. El total diario es lo que importa.",
        "limitations": "Comer muy tarde puede afectar calidad de sueño en algunas personas.",
    },
    "strength_training_women_bulk": {
        "claim": "Las mujeres se ponen muy musculosas/masculinas si entrenan con pesas pesadas",
        "verdict": False,
        "evidence_grade": "A",
        "domain": "fitness",
        "key_studies": [
            {
                "authors": "Ivey et al.",
                "year": 2000,
                "type": "Estudio longitudinal",
                "finding": "Mujeres ganaron significativamente menos músculo que hombres con mismo programa",
            },
        ],
        "mechanism": "Las mujeres tienen ~15-20x menos testosterona que los hombres. Sin esta hormona anabólica, la hipertrofia masiva es fisiológicamente muy difícil.",
        "practical_takeaway": "Entrena pesado sin miedo. El 'tonificado' que buscan muchas mujeres viene de músculo + bajo grasa corporal, y pesas pesadas son óptimas.",
        "limitations": "Con PEDs (esteroides), las mujeres pueden ganar músculo como hombres, pero es artificial.",
    },
    "habit_formation_time": {
        "claim": "Se necesitan exactamente 21 días para formar un hábito",
        "verdict": False,
        "evidence_grade": "B",
        "domain": "behavior",
        "key_studies": [
            {
                "authors": "Lally et al.",
                "year": 2010,
                "type": "Estudio longitudinal",
                "finding": "El rango fue de 18 a 254 días, con mediana de 66 días para alcanzar automaticidad",
            },
        ],
        "mechanism": "La formación de hábitos depende de complejidad del comportamiento, frecuencia, contexto, y diferencias individuales. No hay número mágico.",
        "practical_takeaway": "No te desanimes si después de 21 días aún requiere esfuerzo. Algunos hábitos toman meses. La consistencia importa más que el plazo.",
        "limitations": "El estudio fue con comportamientos simples (beber agua, comer fruta). Hábitos complejos probablemente toman más.",
    },
    "menstrual_cycle_performance": {
        "claim": "El rendimiento físico varía significativamente según la fase del ciclo menstrual",
        "verdict": "Parcialmente verdadero",
        "evidence_grade": "C",
        "domain": "womens_health",
        "key_studies": [
            {
                "authors": "McNulty et al.",
                "year": 2020,
                "type": "Meta-análisis",
                "finding": "Pequeña reducción de rendimiento en fase lútea temprana, pero alta variabilidad individual",
            },
            {
                "authors": "Bruinvels et al.",
                "year": 2017,
                "type": "Survey",
                "finding": "41% de atletas reportan que el ciclo afecta negativamente su entrenamiento/competición",
            },
        ],
        "mechanism": "Las fluctuaciones de estrógeno y progesterona afectan fuerza, termorregulación, uso de sustratos, y recuperación. Pero la magnitud varía enormemente.",
        "practical_takeaway": "Trackea tu ciclo y rendimiento para encontrar TUS patrones. No asumas que las reglas generales aplican a ti.",
        "limitations": "La investigación en mujeres es limitada. La mayoría de estudios de ejercicio se hicieron en hombres. La variabilidad individual es muy alta.",
    },
}


# =============================================================================
# BASE DE DATOS: MITOS (~15)
# =============================================================================


MYTHS_DATABASE: dict[str, dict] = {
    # FITNESS (3 mitos)
    "spot_reduction": {
        "myth_es": "Puedes quemar grasa de zonas específicas haciendo ejercicios localizados",
        "domain": "fitness",
        "truth": "La pérdida de grasa es sistémica. Tu cuerpo decide de dónde moviliza grasa según genética y hormonas, no según qué músculo ejercites.",
        "why_believed": "Es intuitivo pensar que trabajar una zona 'quema' su grasa. El marketing de productos lo explota.",
        "what_works": "Déficit calórico sostenido + entrenamiento de fuerza. El músculo local puede dar mejor apariencia, pero la grasa baja globalmente.",
        "evidence_ref": "spot_reduction_fat",
    },
    "women_bulk_weights": {
        "myth_es": "Las mujeres que levantan pesas pesadas se ponen muy musculosas",
        "domain": "fitness",
        "truth": "Sin testosterona en niveles masculinos (o PEDs), la hipertrofia masiva es fisiológicamente casi imposible para mujeres.",
        "why_believed": "Fotos de bodybuilders femeninas (que usan PEDs) crean la impresión de que cualquier mujer que levante pesado terminará así.",
        "what_works": "Entrena con pesas progresivamente más pesadas. El look 'tonificado' viene de músculo + bajo % grasa, y las pesas son óptimas para eso.",
        "evidence_ref": "strength_training_women_bulk",
    },
    "muscle_confusion": {
        "myth_es": "Debes cambiar tu rutina constantemente para 'confundir' al músculo y seguir progresando",
        "domain": "fitness",
        "truth": "El músculo no se 'confunde'. Lo que necesita para crecer es sobrecarga progresiva sostenida, no variedad constante.",
        "why_believed": "Algunos programas comerciales lo promueven. La novedad se siente productiva. Evita el aburrimiento.",
        "what_works": "Mantén los ejercicios principales por 6-12 semanas, progresando en peso/reps. Varía ejercicios accesorios si quieres novedad.",
        "evidence_ref": "progressive_overload_necessity",
    },
    # NUTRITION (3 mitos)
    "carbs_night_bad": {
        "myth_es": "Comer carbohidratos de noche engorda porque el metabolismo se ralentiza",
        "domain": "nutrition",
        "truth": "El balance energético total del día determina cambios de peso, no el timing. Tu metabolismo no 'se apaga' de noche.",
        "why_believed": "Es intuitivo pensar que comida antes de dormir 'se almacena'. Algunos estudios observacionales confundieron correlación con causalidad.",
        "what_works": "Come carbos cuando te funcione. Si entrenas de tarde/noche, carbos después tiene total sentido.",
        "evidence_ref": "carbs_night_fat",
    },
    "anabolic_window_myth": {
        "myth_es": "Si no comes proteína dentro de 30 minutos post-entreno, pierdes ganancias",
        "domain": "nutrition",
        "truth": "La 'ventana anabólica' existe, pero es de horas, no minutos. El total de proteína diario y su distribución importan más.",
        "why_believed": "Marketing de suplementos. Estudios iniciales mal interpretados. Se siente bien 'hacer algo' inmediatamente.",
        "what_works": "Come proteína en las horas después del entreno (no minutos). Distribuye proteína en 3-4 comidas al día.",
        "evidence_ref": "anabolic_window",
    },
    "detox_cleanses": {
        "myth_es": "Necesitas hacer 'detox' o jugos depurativos para limpiar tu cuerpo de toxinas",
        "domain": "nutrition",
        "truth": "Tu hígado y riñones hacen 'detox' 24/7. No hay evidencia de que jugos, tés o ayunos especiales mejoren este proceso.",
        "why_believed": "Marketing masivo. 'Toxinas' es vago y asusta. La pérdida de peso rápida (agua) parece validarlo.",
        "what_works": "Come suficientes vegetales, frutas, fibra, y mantén hidratación. Eso apoya los sistemas naturales de detoxificación.",
        "evidence_ref": None,
    },
    # BEHAVIOR (3 mitos)
    "21_days_habit": {
        "myth_es": "Se necesitan exactamente 21 días para formar un nuevo hábito",
        "domain": "behavior",
        "truth": "El rango real es de 18 a 254+ días, con mediana alrededor de 66 días. Depende de complejidad y persona.",
        "why_believed": "Un cirujano plástico observó que pacientes se adaptaban a cambios en ~21 días. Se generalizó incorrectamente.",
        "what_works": "No te pongas plazos. Enfócate en consistencia y en hacer el hábito tan fácil que no puedas decir no.",
        "evidence_ref": "habit_formation_time",
    },
    "motivation_key": {
        "myth_es": "Necesitas estar motivado para hacer ejercicio consistentemente",
        "domain": "behavior",
        "truth": "La motivación fluctúa naturalmente. Los hábitos, el ambiente, y los sistemas son más confiables que esperar sentirte motivado.",
        "why_believed": "Las historias de transformación se enfocan en 'encontrar motivación'. La industria vende motivación como producto.",
        "what_works": "Diseña ambiente, crea rutinas, haz el hábito pequeño, y no dependas de cómo te sientas ese día.",
        "evidence_ref": None,
    },
    "willpower_muscle": {
        "myth_es": "La fuerza de voluntad es como un músculo que se agota con el uso",
        "domain": "behavior",
        "truth": "La evidencia sobre 'agotamiento del ego' es mixta. Probablemente importan más las creencias sobre la fuerza de voluntad que su 'reserva'.",
        "why_believed": "Estudios iniciales de Baumeister. Se siente verdad cuando estamos cansados. Justifica ceder.",
        "what_works": "No dependas de fuerza de voluntad. Diseña tu ambiente y hábitos para que la opción correcta sea la fácil.",
        "evidence_ref": None,
    },
    # RECOVERY (3 mitos)
    "no_pain_no_gain": {
        "myth_es": "Si no te duele, no estás entrenando lo suficientemente duro",
        "domain": "recovery",
        "truth": "El DOMS (dolor muscular tardío) no es un indicador confiable de entrenamiento efectivo. Puedes progresar sin dolor significativo.",
        "why_believed": "El dolor se siente 'productivo'. Entrenamientos iniciales causan mucho DOMS. Cultura gym lo glorifica.",
        "what_works": "Enfócate en progresión medible (más peso, más reps). Algo de fatiga es normal, dolor intenso no es necesario ni deseable.",
        "evidence_ref": None,
    },
    "more_training_better": {
        "myth_es": "Más entrenamiento siempre es mejor - si no progresas, entrena más",
        "domain": "recovery",
        "truth": "Existe un punto de rendimientos decrecientes y luego negativos. El sobreentrenamiento es real y contraproducente.",
        "why_believed": "Más esfuerzo = más resultados parece lógico. Las personas exitosas suelen entrenar mucho. Sesgo de supervivencia.",
        "what_works": "Encuentra el volumen mínimo efectivo. Progresa gradualmente. Incluye deloads. Prioriza recuperación.",
        "evidence_ref": "supercompensation",
    },
    "stretching_prevents_injury": {
        "myth_es": "El estiramiento estático antes de entrenar previene lesiones",
        "domain": "recovery",
        "truth": "La evidencia es mixta. El estiramiento estático pre-entreno puede reducir rendimiento de fuerza. Un calentamiento dinámico es mejor.",
        "why_believed": "Tradición. Se siente como 'preparación'. Algunos deportes lo requieren (gimnasia, danza).",
        "what_works": "Calentamiento dinámico antes (movilidad, activación). Estiramiento estático después si quieres mejorar flexibilidad.",
        "evidence_ref": None,
    },
    # WOMEN'S HEALTH (3 mitos)
    "period_no_exercise": {
        "myth_es": "No deberías hacer ejercicio durante tu período",
        "domain": "womens_health",
        "truth": "El ejercicio durante la menstruación es seguro y puede incluso ayudar con síntomas como cólicos y humor.",
        "why_believed": "Tabú cultural. Incomodidad real de algunas mujeres. Sobreprotección histórica.",
        "what_works": "Escucha tu cuerpo. Si te sientes bien, entrena normal. Si no, reduce intensidad. El movimiento suave puede ayudar.",
        "evidence_ref": None,
    },
    "pms_inevitable": {
        "myth_es": "El síndrome premenstrual severo es inevitable y no se puede hacer nada",
        "domain": "womens_health",
        "truth": "Muchos síntomas de PMS pueden reducirse con ejercicio, nutrición, sueño, y manejo de estrés. Síntomas severos pueden requerir atención médica.",
        "why_believed": "Normalización del sufrimiento. Falta de educación sobre opciones. Algunos síntomas son comunes.",
        "what_works": "Ejercicio regular, reducir sal/azúcar/cafeína premenstrual, priorizar sueño. Si es severo, consulta a ginecólogo.",
        "evidence_ref": None,
    },
    "hormones_excuse": {
        "myth_es": "Las fluctuaciones hormonales significan que las mujeres no pueden entrenar de forma consistente",
        "domain": "womens_health",
        "truth": "Las mujeres pueden entrenar consistente y efectivamente. Las fluctuaciones hormonales son normales y manejables con ajustes menores.",
        "why_believed": "Generalización de casos extremos. Historias de algunas atletas. Falta de educación en entrenadoras/es.",
        "what_works": "Trackea tu ciclo, identifica patrones personales, haz ajustes menores cuando necesites. La consistencia es posible.",
        "evidence_ref": "menstrual_cycle_performance",
    },
}


# =============================================================================
# QUIZ TEMPLATES
# =============================================================================


QUIZ_TEMPLATES: dict[str, dict] = {
    "multiple_choice": {
        "format": "Pregunta con 4 opciones, 1 correcta",
        "difficulty_adjustment": "Fácil: opciones muy distintas. Difícil: opciones sutilmente diferentes.",
        "example": {
            "question": "¿Cuál es el factor MÁS importante para ganar músculo?",
            "options": [
                "A) Tomar suplementos de proteína",
                "B) Sobrecarga progresiva en el entrenamiento",
                "C) Hacer cardio todos los días",
                "D) Entrenar en ayunas",
            ],
            "correct": "B",
            "explanation": "La sobrecarga progresiva es el principio fundamental. Sin aumentar el estímulo, el cuerpo no tiene razón para adaptarse.",
        },
    },
    "true_false": {
        "format": "Afirmación que puede ser verdadera o falsa",
        "difficulty_adjustment": "Fácil: afirmaciones claras. Difícil: afirmaciones con matices.",
        "example": {
            "statement": "Debes consumir proteína dentro de 30 minutos después de entrenar para maximizar ganancias.",
            "correct": False,
            "explanation": "La 'ventana anabólica' es más amplia de lo que se pensaba. Las horas post-entreno son suficientes, y el total diario importa más.",
        },
    },
    "fill_blank": {
        "format": "Oración con espacio a completar",
        "difficulty_adjustment": "Fácil: contexto muy claro. Difícil: requiere conocimiento específico.",
        "example": {
            "sentence": "El rango óptimo de proteína para ganancia muscular es aproximadamente _____ gramos por kg de peso corporal.",
            "correct": "1.6-2.2",
            "explanation": "Múltiples meta-análisis convergen en este rango. Menos puede limitar ganancias, más no aporta beneficio adicional.",
        },
    },
    "scenario": {
        "format": "Situación práctica donde debes aplicar conocimiento",
        "difficulty_adjustment": "Fácil: un factor. Difícil: múltiples factores a considerar.",
        "example": {
            "scenario": "María lleva 3 meses entrenando y dejó de progresar en sus levantamientos. Entrena los mismos ejercicios con el mismo peso y repeticiones. ¿Qué le recomendarías?",
            "options": [
                "A) Cambiar todos los ejercicios por otros diferentes",
                "B) Implementar sobrecarga progresiva aumentando peso o repeticiones",
                "C) Reducir los días de entrenamiento",
                "D) Añadir más ejercicios de cardio",
            ],
            "correct": "B",
            "explanation": "María está estancada porque no está aplicando sobrecarga progresiva. Cambiar ejercicios no es la solución; progresar en los actuales sí.",
        },
    },
}


QUIZ_TOPICS: dict[str, list[str]] = {
    "nutrition_basics": ["energy_balance", "macronutrients", "protein_synthesis", "nutrient_timing"],
    "training_fundamentals": ["progressive_overload", "hypertrophy", "periodization", "mind_muscle_connection"],
    "behavior_change": ["habit_loop", "intrinsic_motivation", "implementation_intentions", "cognitive_dissonance"],
    "recovery_essentials": ["supercompensation", "sleep_architecture", "active_recovery", "stress_recovery_balance"],
    "womens_health_basics": ["menstrual_phases", "hormonal_fluctuations", "training_cycle_sync", "perimenopause"],
}


# =============================================================================
# LEARNING LEVELS
# =============================================================================


LEARNING_LEVELS: dict[str, dict] = {
    "beginner": {
        "name_es": "Principiante",
        "description": "Nuevo en el tema, poca o ninguna experiencia previa",
        "explanation_style": "Simple, analogías cotidianas, sin jerga técnica",
        "depth": "Conceptos básicos, reglas prácticas simples",
        "example_type": "Situaciones diarias, analogías familiares",
        "vocabulary": "Evitar términos técnicos, definir cualquier término necesario",
    },
    "intermediate": {
        "name_es": "Intermedio",
        "description": "Tiene experiencia, entiende lo básico, busca profundizar",
        "explanation_style": "Más técnico, introduce terminología correcta",
        "depth": "Mecanismos básicos, matices, excepciones comunes",
        "example_type": "Casos de entrenamiento reales, aplicaciones prácticas",
        "vocabulary": "Usar terminología del campo, explicar términos avanzados",
    },
    "advanced": {
        "name_es": "Avanzado",
        "description": "Experiencia significativa, busca optimización y edge cases",
        "explanation_style": "Técnico completo, referencias a literatura",
        "depth": "Mecanismos fisiológicos/bioquímicos, controversias, edge cases",
        "example_type": "Optimización, periodización avanzada, casos complejos",
        "vocabulary": "Lenguaje técnico completo, discusión de literatura científica",
    },
}


# =============================================================================
# FUNCIONES TOOL
# =============================================================================


def explain_concept(
    concept: str,
    user_level: str = "intermediate",
    include_examples: bool = True,
    include_mistakes: bool = True,
) -> dict:
    """Explica un concepto adaptado al nivel del usuario.

    Args:
        concept: Nombre del concepto a explicar (ej: "progressive_overload", "energy_balance").
        user_level: Nivel del usuario ("beginner", "intermediate", "advanced").
        include_examples: Si incluir ejemplos prácticos.
        include_mistakes: Si incluir errores comunes a evitar.

    Returns:
        Dict con explicación adaptada, ejemplos, y conceptos relacionados.
    """
    # Validación de inputs
    if not concept or len(concept.strip()) < 2:
        return {
            "status": "error",
            "error": "Debes especificar un concepto a explicar.",
        }

    # Normalizar nivel
    level = user_level.lower().strip()
    if level not in LEARNING_LEVELS:
        level = "intermediate"

    # Buscar concepto (normalizar para búsqueda)
    concept_key = concept.lower().strip().replace(" ", "_").replace("-", "_")

    # Búsqueda exacta
    concept_data = CONCEPTS_DATABASE.get(concept_key)

    # Si no encuentra, buscar por nombre en español o parcial
    if not concept_data:
        for key, data in CONCEPTS_DATABASE.items():
            if concept.lower() in data.get("name_es", "").lower():
                concept_data = data
                concept_key = key
                break
            if concept.lower() in key:
                concept_data = data
                concept_key = key
                break

    if not concept_data:
        # Sugerir conceptos disponibles
        available = [
            f"{data['name_es']} ({key})"
            for key, data in CONCEPTS_DATABASE.items()
        ]
        return {
            "status": "not_found",
            "message": f"No encontré el concepto '{concept}' en mi base de conocimiento.",
            "available_concepts": available,
            "suggestion": "¿Querías decir alguno de estos? También puedo intentar explicarlo si me das más contexto.",
        }

    # Construir explicación según nivel
    _level_info = LEARNING_LEVELS[level]  # noqa: F841 - kept for reference
    level_explanation = concept_data["levels"].get(level, concept_data["levels"]["intermediate"])

    response = {
        "status": "explained",
        "concept": concept_key,
        "name_es": concept_data["name_es"],
        "domain": concept_data["domain"],
        "user_level": level,
        "definition": concept_data["definition"],
        "why_important": concept_data["why_important"],
        "explanation_for_level": level_explanation,
        "related_concepts": concept_data.get("related_concepts", []),
    }

    if include_examples and "analogy" in concept_data:
        response["analogy"] = concept_data["analogy"]

    if include_mistakes and "common_mistakes" in concept_data:
        response["common_mistakes"] = concept_data["common_mistakes"]

    # Añadir guía de profundización
    if level == "beginner":
        response["next_step"] = "Cuando te sientas cómodo con esto, podemos profundizar en los mecanismos."
    elif level == "intermediate":
        response["next_step"] = "Si quieres más detalle técnico, puedo explicar a nivel avanzado."

    return response


def present_evidence(
    topic: str,
    include_studies: bool = True,
    max_studies: int = 3,
) -> dict:
    """Presenta la evidencia científica sobre un tema o afirmación.

    Args:
        topic: Tema o afirmación a evaluar (ej: "creatine", "anabolic window").
        include_studies: Si incluir detalles de estudios específicos.
        max_studies: Número máximo de estudios a incluir.

    Returns:
        Dict con veredicto, grado de evidencia, estudios clave, y aplicación práctica.
    """
    if not topic or len(topic.strip()) < 2:
        return {
            "status": "error",
            "error": "Debes especificar un tema para evaluar su evidencia.",
        }

    # Normalizar para búsqueda
    topic_key = topic.lower().strip().replace(" ", "_").replace("-", "_")

    # Buscar en evidence database
    evidence = EVIDENCE_DATABASE.get(topic_key)

    # Búsqueda parcial
    if not evidence:
        for key, data in EVIDENCE_DATABASE.items():
            if topic.lower() in key or topic.lower() in data.get("claim", "").lower():
                evidence = data
                topic_key = key
                break

    if not evidence:
        available = list(EVIDENCE_DATABASE.keys())
        return {
            "status": "not_found",
            "message": f"No tengo evidencia específica sobre '{topic}' en mi base de datos.",
            "available_topics": available,
            "suggestion": "Puedo investigar más si me das el claim específico que quieres evaluar.",
        }

    response = {
        "status": "evaluated",
        "topic": topic_key,
        "claim": evidence["claim"],
        "verdict": evidence["verdict"],
        "evidence_grade": evidence["evidence_grade"],
        "evidence_grade_meaning": {
            "A": "Fuerte - múltiples RCTs de calidad confirman",
            "B": "Moderada - algunos RCTs o meta-análisis apoyan",
            "C": "Limitada - principalmente estudios observacionales",
            "D": "Insuficiente - mayormente evidencia anecdótica",
        }.get(evidence["evidence_grade"], "Desconocido"),
        "domain": evidence.get("domain", "general"),
        "mechanism": evidence.get("mechanism", "No especificado"),
        "practical_takeaway": evidence.get("practical_takeaway", "Consultar fuentes adicionales"),
    }

    if include_studies and "key_studies" in evidence:
        response["key_studies"] = evidence["key_studies"][:max_studies]

    if "limitations" in evidence:
        response["limitations"] = evidence["limitations"]

    response["disclaimer"] = "Esta información es educativa. Consulta profesionales para decisiones personales de salud."

    return response


def debunk_myth(
    myth: str,
    empathetic: bool = True,
) -> dict:
    """Corrige un mito común con empatía y evidencia.

    Args:
        myth: El mito a desmentir (ej: "spot reduction", "carbs at night").
        empathetic: Si incluir validación empática de por qué se cree el mito.

    Returns:
        Dict con el mito, la verdad, evidencia, y práctica correcta.
    """
    if not myth or len(myth.strip()) < 2:
        return {
            "status": "error",
            "error": "Debes especificar un mito a evaluar.",
        }

    # Normalizar para búsqueda
    myth_key = myth.lower().strip().replace(" ", "_").replace("-", "_")

    # Buscar mito
    myth_data = MYTHS_DATABASE.get(myth_key)

    # Búsqueda por contenido
    if not myth_data:
        for key, data in MYTHS_DATABASE.items():
            if myth.lower() in key or myth.lower() in data.get("myth_es", "").lower():
                myth_data = data
                myth_key = key
                break

    if not myth_data:
        available = [
            f"{data['myth_es'][:50]}..." for data in MYTHS_DATABASE.values()
        ]
        return {
            "status": "not_found",
            "message": f"No encontré el mito '{myth}' en mi base de datos.",
            "available_myths": available[:10],
            "suggestion": "¿Podrías describir el mito con más detalle?",
        }

    response = {
        "status": "debunked",
        "myth_key": myth_key,
        "myth": myth_data["myth_es"],
        "domain": myth_data["domain"],
        "truth": myth_data["truth"],
        "what_works": myth_data["what_works"],
    }

    if empathetic and "why_believed" in myth_data:
        response["why_believed"] = myth_data["why_believed"]
        response["empathy_note"] = "Es comprensible creer esto - muchas fuentes aparentemente confiables lo repiten."

    if "evidence_ref" in myth_data and myth_data["evidence_ref"]:
        evidence = EVIDENCE_DATABASE.get(myth_data["evidence_ref"])
        if evidence:
            response["supporting_evidence"] = {
                "claim": evidence["claim"],
                "grade": evidence["evidence_grade"],
            }

    response["disclaimer"] = "Esta información es educativa. Si tienes dudas específicas sobre tu situación, consulta a un profesional."

    return response


def create_deep_dive(
    topic: str,
    sections: list[str] | None = None,
    include_quiz: bool = True,
    user_level: str = "intermediate",
) -> dict:
    """Crea un módulo educativo completo sobre un tema.

    Args:
        topic: Tema principal del deep dive.
        sections: Secciones específicas a incluir (opcional).
        include_quiz: Si incluir un mini-quiz al final.
        user_level: Nivel del usuario para adaptar contenido.

    Returns:
        Dict con módulo educativo estructurado.
    """
    if not topic or len(topic.strip()) < 2:
        return {
            "status": "error",
            "error": "Debes especificar un tema para el deep dive.",
        }

    # Normalizar
    topic_key = topic.lower().strip().replace(" ", "_").replace("-", "_")
    level = user_level.lower().strip()
    if level not in LEARNING_LEVELS:
        level = "intermediate"

    # Buscar concepto principal
    main_concept = CONCEPTS_DATABASE.get(topic_key)

    if not main_concept:
        for key, data in CONCEPTS_DATABASE.items():
            if topic.lower() in key or topic.lower() in data.get("name_es", "").lower():
                main_concept = data
                topic_key = key
                break

    if not main_concept:
        return {
            "status": "not_found",
            "message": f"No puedo crear un deep dive sobre '{topic}' - no está en mi base de conocimiento.",
            "available_topics": list(CONCEPTS_DATABASE.keys()),
        }

    # Construir módulo
    module = {
        "status": "created",
        "topic": topic_key,
        "title": f"Deep Dive: {main_concept['name_es']}",
        "user_level": level,
        "estimated_time_minutes": 10 if level == "beginner" else 15 if level == "intermediate" else 20,
        "sections": [],
    }

    # Sección 1: Introducción
    module["sections"].append({
        "title": "¿Por qué importa esto?",
        "content": main_concept["why_important"],
        "key_point": main_concept["definition"],
    })

    # Sección 2: Explicación principal
    module["sections"].append({
        "title": "Entendiendo el concepto",
        "content": main_concept["levels"].get(level, main_concept["levels"]["intermediate"]),
        "analogy": main_concept.get("analogy", None),
    })

    # Sección 3: Errores comunes
    if "common_mistakes" in main_concept:
        module["sections"].append({
            "title": "Errores comunes a evitar",
            "content": main_concept["common_mistakes"],
        })

    # Sección 4: Conceptos relacionados
    related = main_concept.get("related_concepts", [])
    if related:
        related_explanations = []
        for rel_key in related[:3]:
            rel_data = CONCEPTS_DATABASE.get(rel_key)
            if rel_data:
                related_explanations.append({
                    "concept": rel_data["name_es"],
                    "connection": f"Relacionado con {main_concept['name_es']} porque ambos son fundamentales para {main_concept['domain']}.",
                })
        if related_explanations:
            module["sections"].append({
                "title": "Conceptos relacionados",
                "content": related_explanations,
            })

    # Sección 5: Quiz
    if include_quiz:
        quiz = generate_quiz(
            topic=topic_key,
            difficulty="easy" if level == "beginner" else "medium",
            num_questions=3,
            question_types=["multiple_choice", "true_false"],
        )
        if quiz.get("status") == "generated":
            module["quiz"] = quiz["quiz"]

    # Sección final: Siguiente paso
    module["next_steps"] = {
        "deepen": f"Para profundizar, explora: {', '.join(related[:2]) if related else 'conceptos relacionados'}",
        "apply": "Intenta aplicar este concepto en tu próxima sesión de entrenamiento/nutrición.",
    }

    return module


def generate_quiz(
    topic: str,
    difficulty: str = "medium",
    num_questions: int = 5,
    question_types: list[str] | None = None,
) -> dict:
    """Genera un quiz educativo sobre un tema.

    Args:
        topic: Tema del quiz (concepto específico o categoría).
        difficulty: Nivel de dificultad ("easy", "medium", "hard").
        num_questions: Número de preguntas (1-10).
        question_types: Tipos de preguntas a incluir.

    Returns:
        Dict con quiz generado, respuestas correctas, y explicaciones.
    """
    if not topic or len(topic.strip()) < 2:
        return {
            "status": "error",
            "error": "Debes especificar un tema para el quiz.",
        }

    # Normalizar
    topic_key = topic.lower().strip().replace(" ", "_").replace("-", "_")
    diff = difficulty.lower().strip()
    if diff not in ["easy", "medium", "hard"]:
        diff = "medium"

    num_q = min(max(int(num_questions), 1), 10)

    if question_types is None:
        question_types = ["multiple_choice", "true_false"]

    # Determinar conceptos a cubrir
    concepts_to_cover = []

    # Si es un topic de quiz predefinido
    if topic_key in QUIZ_TOPICS:
        concepts_to_cover = QUIZ_TOPICS[topic_key]
    # Si es un concepto específico
    elif topic_key in CONCEPTS_DATABASE:
        concepts_to_cover = [topic_key]
        # Añadir relacionados si necesitamos más preguntas
        related = CONCEPTS_DATABASE[topic_key].get("related_concepts", [])
        concepts_to_cover.extend([r for r in related if r in CONCEPTS_DATABASE])
    else:
        # Buscar por dominio
        for key, data in CONCEPTS_DATABASE.items():
            if topic.lower() in data.get("domain", ""):
                concepts_to_cover.append(key)

    if not concepts_to_cover:
        return {
            "status": "error",
            "message": f"No pude encontrar contenido para crear un quiz sobre '{topic}'.",
            "available_topics": list(QUIZ_TOPICS.keys()) + ["fitness", "nutrition", "behavior", "recovery", "womens_health"],
        }

    # Generar preguntas
    questions = []

    for i in range(num_q):
        concept_key = concepts_to_cover[i % len(concepts_to_cover)]
        concept = CONCEPTS_DATABASE.get(concept_key, {})

        if not concept:
            continue

        q_type = question_types[i % len(question_types)]

        if q_type == "multiple_choice":
            question = _generate_multiple_choice(concept, concept_key, diff)
        elif q_type == "true_false":
            question = _generate_true_false(concept, concept_key, diff)
        else:
            question = _generate_multiple_choice(concept, concept_key, diff)

        question["question_number"] = i + 1
        questions.append(question)

    return {
        "status": "generated",
        "topic": topic_key,
        "difficulty": diff,
        "num_questions": len(questions),
        "quiz": {
            "title": f"Quiz: {topic.replace('_', ' ').title()}",
            "instructions": "Responde cada pregunta. Al final verás las explicaciones.",
            "questions": questions,
        },
        "disclaimer": "Este quiz es educativo. La puntuación no define tu conocimiento real.",
    }


# =============================================================================
# FUNCIONES HELPER PRIVADAS
# =============================================================================


def _generate_multiple_choice(concept: dict, concept_key: str, difficulty: str) -> dict:
    """Genera una pregunta de opción múltiple."""
    name = concept.get("name_es", concept_key)
    definition = concept.get("definition", "")

    # Pregunta básica sobre el concepto
    question = f"¿Qué es la {name}?"

    correct = definition[:100] + "..." if len(definition) > 100 else definition

    # Generar distractores basados en errores comunes o conceptos relacionados
    mistakes = concept.get("common_mistakes", [])
    distractors = [
        "Un tipo de suplemento para ganar músculo",
        "Una técnica de cardio de alta intensidad",
        "Un método de recuperación pasiva",
    ]

    if mistakes:
        distractors = [f"Error: {m[:50]}..." for m in mistakes[:3]]

    options = [correct] + distractors[:3]
    random.shuffle(options)

    correct_index = options.index(correct)
    correct_letter = ["A", "B", "C", "D"][correct_index]

    return {
        "type": "multiple_choice",
        "concept": concept_key,
        "question": question,
        "options": {
            "A": options[0],
            "B": options[1],
            "C": options[2],
            "D": options[3],
        },
        "correct_answer": correct_letter,
        "explanation": f"La {name} se refiere a: {definition}",
    }


def _generate_true_false(concept: dict, concept_key: str, difficulty: str) -> dict:
    """Genera una pregunta de verdadero/falso."""
    name = concept.get("name_es", concept_key)

    # Alternar entre afirmaciones verdaderas y falsas
    is_true = random.choice([True, False])

    if is_true:
        statement = f"La {name} es importante porque {concept.get('why_important', 'ayuda a mejorar resultados')}."
        explanation = "Correcto. " + concept.get("why_important", "")
    else:
        mistakes = concept.get("common_mistakes", ["no tiene importancia real"])
        statement = f"Para aprovechar la {name}, es recomendable {mistakes[0].lower() if mistakes else 'ignorarla completamente'}."
        explanation = f"Falso. Este es un error común. La realidad es que {concept.get('why_important', 'es importante para progresar')}."

    return {
        "type": "true_false",
        "concept": concept_key,
        "statement": statement,
        "correct_answer": is_true,
        "explanation": explanation,
    }


# =============================================================================
# TOOL WRAPPERS
# =============================================================================


explain_concept_tool = FunctionTool(explain_concept)
present_evidence_tool = FunctionTool(present_evidence)
debunk_myth_tool = FunctionTool(debunk_myth)
create_deep_dive_tool = FunctionTool(create_deep_dive)
generate_quiz_tool = FunctionTool(generate_quiz)


ALL_TOOLS = [
    explain_concept_tool,
    present_evidence_tool,
    debunk_myth_tool,
    create_deep_dive_tool,
    generate_quiz_tool,
]


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Tools
    "explain_concept",
    "present_evidence",
    "debunk_myth",
    "create_deep_dive",
    "generate_quiz",
    # Tool wrappers
    "explain_concept_tool",
    "present_evidence_tool",
    "debunk_myth_tool",
    "create_deep_dive_tool",
    "generate_quiz_tool",
    "ALL_TOOLS",
    # Databases
    "CONCEPTS_DATABASE",
    "EVIDENCE_DATABASE",
    "MYTHS_DATABASE",
    "QUIZ_TEMPLATES",
    "QUIZ_TOPICS",
    "LEARNING_LEVELS",
    # Enums
    "Domain",
    "LearningLevel",
    "EvidenceGrade",
    "QuestionType",
    "Difficulty",
]
