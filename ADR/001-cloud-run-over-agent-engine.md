# ADR-001: Cloud Run sobre Agent Engine para el MVP

Status: Accepted
Date: 2025-10-28

## Contexto
- Necesitamos desplegar NEXUS y agentes especializados con el ADK y protocolo A2A.
- Alternativas evaluadas: Vertex AI Agent Engine (servicio gestionado) vs. Cloud Run (contenedores + ADK).

## Decisión
Usar Cloud Run + ADK como plataforma de ejecución para el MVP y primeras fases de producción.

## Justificación
- **Flexibilidad total**: definimos endpoints JSON-RPC/SSE, middlewares (auth, rate limiting, logging) y pipelines propios.
- **Control operativo**: escalado a cero, despliegues por servicio, versiones coherentes con CI/CD.
- **Cuotas**: evitamos límites de Agent Engine (p. ej. 60 POST A2A/min/agente, 90 queries/min) que restringen orquestaciones paralelas.
- **Madurez**: Cloud Run + ADK están probados en producción; Agent Engine aún tiene features en Preview (Memory Bank, Code Execution, Sessions extendidas).

## Costo de Referencia (2025-10, us-central1)
- Cloud Run: $0.0864 por vCPU-h, $0.009 por GiB-h. Con seis servicios (NEXUS + 5 agentes), 2 vCPU/4 GiB c/u y ~30% utilización → ~2,592 vCPU-h y 5,184 GiB-h → ≈ $265/mes tras free tier.
- Agent Engine: $0.0994 por vCPU-h, $0.0105 por GiB-h. Con seis agentes 24/7, 1 vCPU/4 GiB c/u → 4,320 vCPU-h y 17,280 GiB-h → ≈ $611/mes.
- Diferencia: Cloud Run ≈ 28% más barato bajo supuestos conservadores, además de permitir optimizar por request.

## SLOs y KPIs
- Latencia p95: ≤2.0 s (Flash), ≤6.0 s (Pro).
- Disponibilidad: ≥99.5% (medida por health checks).
- Presupuesto por interacción: ≤$0.01 para agentes Flash, ≤$0.05 para NEXUS (Pro).

## Riesgos
- Mayor responsabilidad operativa (observabilidad, seguridad, actualización de runtimes) recae en nosotros.
- Debemos implementar discovery y tracing A2A manualmente.

## Consecuencias
- Diseñamos IaC (Terraform) para servicios Cloud Run, secretos, redes y monitoreo.
- Mantendremos la opción de migrar agentes específicos a Agent Engine cuando sus capacidades maduren o si necesitamos gobernanza adicional.

## Referencias
- Vertex AI Pricing (Oct 2025).
- Documentación ADK + Cloud Run.
