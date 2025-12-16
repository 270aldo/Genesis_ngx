# Guía de Referencia Avanzada: Sistemas Multi-Agente con ADK

Este documento proporciona ejemplos y mejores prácticas para la implementación de sistemas multi-agente utilizando el **Agent Development Kit (ADK)** de Google.

## 1. Tipos de Agentes en ADK

ADK ofrece una tipología de agentes flexible para construir sistemas robustos. La clase base es `BaseAgent`, de la cual derivan los siguientes tipos:

-   **Agentes LLM (`LlmAgent`, `Agent`):** Son el cerebro para tareas que requieren razonamiento, planificación y lenguaje natural. Utilizan un LLM (como Gemini) para decidir qué hacer a continuación, incluyendo qué herramientas usar. Son no deterministas y flexibles.

-   **Agentes de Flujo de Trabajo (`Workflow Agents`):** Orquestan la ejecución de otros agentes de forma predecinible y determinista, sin usar un LLM para el control de flujo. Son esenciales para procesos estructurados.
    -   `SequentialAgent`: Ejecuta sub-agentes en un orden estricto, uno tras otro.
    -   `ParallelAgent`: Ejecuta sub-agentes de forma concurrente, ideal para recolectar datos de múltiples fuentes a la vez.
    -   `LoopAgent`: Repite la ejecución de una secuencia de agentes un número determinado de veces o hasta que se cumpla una condición.

-   **Agentes Personalizados (`Custom Agents`):** Para una flexibilidad total, puedes heredar de `BaseAgent` y definir tu propia lógica de ejecución. Esto es útil para integraciones complejas o flujos de control únicos.

## 2. El Patrón Arquitectónico: Coordinador y Especialistas

La arquitectura más recomendada para sistemas complejos es la de **Coordinador/Especialista**.

-   **Agente Coordinador (Orquestador):** Un `LlmAgent` que actúa como el cerebro del sistema. Su función es analizar la solicitud, planificar los pasos y delegar el trabajo a los especialistas.
    -   **Modelo recomendado:** `Gemini 2.5 Pro`, por su capacidad superior de razonamiento.

-   **Agentes Especialistas:** `LlmAgent` o `CustomAgent` enfocados en una única tarea. Son rápidos, eficientes y predecibles.
    -   **Modelo recomendado:** `Gemini 2.5 Flash`, por su velocidad y bajo coste.

**Ventajas:** Modularidad, eficiencia, reusabilidad y seguridad.

## 3. Herramientas y Capacidades (`Tools`)

Las herramientas son la forma en que los agentes interactúan con el mundo exterior. ADK ofrece un ecosistema muy rico:

-   **`FunctionTool`:** La forma más común de crear una herramienta. Envuelve una función de Python simple. El `docstring` de la función es crucial, ya que el LLM lo usa para entender qué hace la herramienta y cómo usarla.
-   **`AgentTool` (`Agent-as-a-Tool`):** Permite que un agente trate a otro agente como si fuera una herramienta. Este es el mecanismo principal en el patrón Coordinador/Especialista.
-   **Herramientas Integradas (`Built-in Tools`):**
    -   `GoogleSearch`: Para realizar búsquedas web.
    -   `CodeExecution`: Para ejecutar código Python en un entorno aislado (sandbox).
    -   `VertexAISearch`: Para buscar en tus almacenes de datos privados.
-   **Herramientas de Terceros:** ADK permite integrar herramientas de ecosistemas como `LangChain` y `CrewAI`.
-   **Integración con OpenAPI:** Puedes generar un conjunto de herramientas automáticamente a partir de una especificación de OpenAPI v3, permitiendo al agente interactuar con cualquier API RESTful.

## 4. Ejemplo Práctico: "Sistema de Análisis de Mercado"

Este ejemplo ilustra el patrón de Coordinador/Especialista.

**Componentes:**

1.  **`AgenteCoordinador` (Gemini 2.5 Pro):** Orquesta el análisis.
2.  **`AgenteInvestigadorWeb` (Gemini 2.5 Flash):** Especialista en buscar en la web con `GoogleSearch`.
3.  **`AgenteRedactor` (Gemini 2.5 Flash):** Especialista en sintetizar información. No tiene herramientas.

### Implementación (Python con ADK)

```python path=null start=null
# --- agent_definitions.py ---

from adk.agents import LlmAgent, AgentTool, SequentialAgent
from adk.tools import google_search

# --- 1. Definición de Agentes Especialistas (Flash) ---

investigador_web = LlmAgent(
    name="AgenteInvestigadorWeb",
    model="gemini-2.5-flash",
    instruction="Eres un experto en encontrar información relevante y actual en la web. Usa la herramienta de búsqueda para responder.",
    tools=[google_search],
)

redactor = LlmAgent(
    name="AgenteRedactor",
    model="gemini-2.5-flash",
    instruction="Eres un experto redactor. Recibes datos brutos y debes sintetizarlos en un informe claro y conciso de 3 párrafos.",
)

# --- 2. Definición del Agente Coordinador (Pro) ---

# Convertimos los agentes especialistas en herramientas.
herramienta_investigador = AgentTool(investigador_web)
herramienta_redactor = AgentTool(redactor)

# El coordinador es un agente secuencial para un flujo predecible.
coordinador = SequentialAgent(
    name="AgenteCoordinador",
    # Los agentes de flujo de trabajo no usan LLM para orquestar.
    sub_agents=[
        LlmAgent(
            name="Planificador",
            model="gemini-2.5-pro",
            instruction="""
            Tu misión es orquestar un análisis de mercado.
            1. Recibe el nombre del producto.
            2. Llama a `AgenteInvestigadorWeb` para obtener noticias y contexto.
            3. Llama a `AgenteRedactor` con la información recopilada para que genere el informe.
            4. Devuelve únicamente el informe final del redactor.
            """,
            tools=[
                herramienta_investigador,
                herramienta_redactor,
            ],
            # La jerarquía ayuda al LLM a entender el sistema.
            sub_agents=[investigador_web, redactor]
        )
    ]
)

# --- 3. Lógica de Ejecución ---
# async def handle_request(product_name: str):
#     final_event = await coordinador.run(user_content=product_name)
#     print(final_event.content)
```

## 5. Opciones de Despliegue

-   **Vertex AI Agent Engine:** La opción recomendada para producción. Es una plataforma totalmente gestionada y escalable. Se despliega a través de un `AdkApp` y el comando `gcloud ai reasoning-engines apps deploy`.
-   **Cloud Run:** Ideal para aplicaciones basadas en contenedores. El comando `adk deploy cloud_run` facilita el despliegue.
-   **Google Kubernetes Engine (GKE):** Para un control máximo sobre la infraestructura. Requiere la creación de un `Dockerfile` y manifiestos de Kubernetes (`deployment.yaml`, `service.yaml`).

## 6. Seguridad y Mejores Prácticas

-   **Principio de Mínimo Privilegio:** Limita las herramientas de cada agente a lo estrictamente necesario. El `AgenteRedactor` no necesita acceso a internet.
-   **Callbacks como Guardrails:** Utiliza `before_tool_call` para interceptar y validar los argumentos de una llamada a herramienta antes de que se ejecute. Puedes usar un LLM rápido (Gemini Flash) como un "filtro de seguridad" para evaluar si la llamada es segura.
-   **Sandboxing:** Las herramientas de ejecución de código (`CodeExecutionTool`) que ofrece ADK se ejecutan en un entorno de sandbox para proteger el sistema anfitrión.
-   **Autenticación:** ADK tiene un sistema robusto para manejar la autenticación con herramientas externas, soportando API Keys, OAuth 2.0 y Cuentas de Servicio.
