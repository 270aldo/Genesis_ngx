from google.adk.agents import LlmAgent

# Agente raíz placeholder para diseño visual
# Este sirve como punto de entrada para el ADK Visual Builder
# Desde aquí diseñaremos la jerarquía completa de Genesis NGX

root_agent = LlmAgent(
    name="genesis_design_canvas",
    instruction="You are the root canvas for the Genesis NGX multi-agent system. "
                "Use this visual designer to prototype NEXUS orchestrator and specialized agents.",
)
