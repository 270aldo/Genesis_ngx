# Ejemplos de Sistemas Multi-Agente con ADK

Este documento contiene ejemplos de código extraídos del repositorio oficial de `adk-samples`. Estos ejemplos ilustran la arquitectura de **Coordinador/Especialista**, un patrón fundamental para construir sistemas de agentes robustos y modulares con el Agent Development Kit (ADK).

## Ejemplo 1: Asesor Financiero (`financial-advisor`)

Este ejemplo demuestra un sistema donde un agente coordinador orquesta a un equipo de especialistas financieros para proporcionar una estrategia de inversión.

**Arquitectura:**
-   **`financial_coordinator` (Agente Coordinador):** Recibe la solicitud del usuario (por ejemplo, analizar una acción) y delega las tareas a los especialistas. Utiliza `AgentTool` para tratar a cada sub-agente como una herramienta.
-   **`data_analyst_agent` (Especialista):** Su única función es buscar información de mercado utilizando `google_search`.
-   **`risk_analyst_agent` (Especialista):** Evalúa el riesgo de la estrategia propuesta. No tiene herramientas, solo razona sobre la información que se le proporciona.
-   Otros especialistas (como `trading_analyst` y `execution_analyst`) se encargan de otras partes del flujo.

### Código del Agente Coordinador

```python path=null start=null
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Financial coordinator: provide reasonable investment strategies."""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.data_analyst import data_analyst_agent
from .sub_agents.execution_analyst import execution_analyst_agent
from .sub_agents.risk_analyst import risk_analyst_agent
from .sub_agents.trading_analyst import trading_analyst_agent


MODEL = "gemini-2.5-pro"


financial_coordinator = LlmAgent(
    name="financial_coordinator",
    model=MODEL,
    description=(
        "guide users through a structured process to receive financial "
        "advice by orchestrating a series of expert subagents. help them "
        "analyze a market ticker, develop trading strategies, define "
        "execution plans, and evaluate the overall risk."
    ),
    instruction=prompt.FINANCIAL_COORDINATOR_PROMPT,
    output_key="financial_coordinator_output",
    tools=[
        AgentTool(agent=data_analyst_agent),
        AgentTool(agent=trading_analyst_agent),
        AgentTool(agent=execution_analyst_agent),
        AgentTool(agent=risk_analyst_agent),
    ],
)

root_agent = financial_coordinator
```

### Código de los Sub-Agentes Especialistas

**Analista de Datos:**
```python path=null start=null
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""data_analyst_agent for finding information using google search"""

from google.adk import Agent
from google.adk.tools import google_search

from . import prompt

MODEL = "gemini-2.5-pro"

data_analyst_agent = Agent(
    model=MODEL,
    name="data_analyst_agent",
    instruction=prompt.DATA_ANALYST_PROMPT,
    output_key="market_data_analysis_output",
    tools=[google_search],
)
```

**Analista de Riesgos:**
```python path=null start=null
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Risk Analysis Agent for providing the final risk evaluation"""

from google.adk import Agent

from . import prompt

MODEL="gemini-2.5-pro"

risk_analyst_agent = Agent(
    model=MODEL,
    name="risk_analyst_agent",
    instruction=prompt.RISK_ANALYST_PROMPT,
    output_key="final_risk_assessment_output",
)
```

---

## Ejemplo 2: Escritor de Blogs (`blog-writer`)

Este ejemplo muestra un flujo de trabajo en pipeline, donde un agente principal gestiona a un equipo de sub-agentes para producir un artículo de blog técnico, desde la planificación hasta la edición final.

**Arquitectura:**
-   **`interactive_blogger_agent` (Agente Coordinador):** Interactúa con el usuario y orquesta el flujo de trabajo completo.
-   **`robust_blog_planner` (Especialista):** Un `LoopAgent` que contiene al `blog_planner` para generar el esquema del blog. El `LoopAgent` asegura que la planificación se reintente si falla, añadiendo robustez.
-   **`robust_blog_writer` (Especialista):** Otro `LoopAgent` que contiene al `blog_writer` para redactar el contenido a partir del esquema.
-   **`blog_editor` (Especialista):** Edita el borrador final basándose en el feedback del usuario.

### Código del Agente Coordinador

```python path=null start=null
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .config import config
from .sub_agents import (
    blog_editor,
    robust_blog_planner,
    robust_blog_writer,
    social_media_writer,
)
from .tools import analyze_codebase, save_blog_post_to_file

# --- AGENT DEFINITIONS ---

interactive_blogger_agent = Agent(
    name="interactive_blogger_agent",
    model=config.worker_model,
    description="The primary technical blogging assistant. It collaborates with the user to create a blog post.",
    instruction=f"""
    You are a technical blogging assistant. Your primary function is to help users create technical blog posts.

    Your workflow is as follows:
    1.  **Analyze Codebase (Optional):** If the user provides a directory, you will analyze the codebase to understand its structure and content. To do this, use the `analyze_codebase` tool.
    2.  **Plan:** You will generate a blog post outline and present it to the user. To do this, use the `robust_blog_planner` tool.
    3.  **Refine:** The user can provide feedback to refine the outline. You will continue to refine the outline until it is approved by the user.
    4.  **Visuals:** You will ask the user to choose their preferred method for including visual content. You have two options for including visual content in your blog post:

    1.  **Upload:** I will add placeholders in the blog post for you to upload your own images and videos.
    2.  **None:** I will not include any images or videos in the blog post.

    Please respond with "1" or "2" to indicate your choice.
    5.  **Write:** Once the user approves the outline, you will write the blog post. To do this, use the `robust_blog_writer` tool. Be then open for feedback.
    6.  **Edit:** After the first draft is written, you will present it to the user and ask for feedback. You will then revise the blog post based on the feedback. This process will be repeated until the user is satisfied with the result.
    7.  **Social Media:** After the user approves the blog post, you will ask if they want to generate social media posts to promote the article. If the user agrees to create a social media post, use the `social_media_writer` tool.
    8.  **Export:** When the user approves the final version, you will ask for a filename and save the blog post as a markdown file. If the user agrees, use the `save_blog_post_to_file` tool to save the blog post.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    sub_agents=[
        robust_blog_writer,
        robust_blog_planner,
        blog_editor,
        social_media_writer,
    ],
    tools=[
        FunctionTool(save_blog_post_to_file),
        FunctionTool(analyze_codebase),
    ],
    output_key="blog_outline",
)


root_agent = interactive_blogger_agent
```

### Código de los Sub-Agentes Especialistas

**Planificador Robusto (Usa `LoopAgent`):**
```python path=null start=null
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent, LoopAgent
from google.adk.tools import google_search

from ..config import config
from ..agent_utils import suppress_output_callback
from ..validation_checkers import OutlineValidationChecker

blog_planner = Agent(
    model=config.worker_model,
    name="blog_planner",
    description="Generates a blog post outline.",
    instruction="""
    You are a technical content strategist. Your job is to create a blog post outline.
    The outline should be well-structured and easy to follow.
    It should include a title, an introduction, a main body with several sections, and a conclusion.
    If a codebase is provided, the outline should include sections for code snippets and technical deep dives.
    The codebase context will be available in the `codebase_context` state key.
    Use the information in the `codebase_context` to generate a specific and accurate outline.
    Use Google Search to find relevant information and examples to support your writing.
    Your final output should be a blog post outline in Markdown format.
    """,
    tools=[google_search],
    output_key="blog_outline",
    after_agent_callback=suppress_output_callback,
)

robust_blog_planner = LoopAgent(
    name="robust_blog_planner",
    description="A robust blog planner that retries if it fails.",
    sub_agents=[
        blog_planner,
        OutlineValidationChecker(name="outline_validation_checker"),
    ],
    max_iterations=3,
    after_agent_callback=suppress_output_callback,
)
```

**Editor:**
```python path=null start=null
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent

from ..config import config
from ..agent_utils import suppress_output_callback

blog_editor = Agent(
    model=config.critic_model,
    name="blog_editor",
    description="Edits a technical blog post based on user feedback.",
    instruction="""
    You are a professional technical editor. You will be given a blog post and user feedback.
    Your task is to edit the blog post based on the provided feedback.
    The final output should be a revised blog post in Markdown format.
    """,
    output_key="blog_post",
    after_agent_callback=suppress_output_callback,
)
```
