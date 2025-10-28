# ADR-004: Selección de Modelos Gemini 2.5 y Estrategia de Caching

Status: Accepted
Date: 2025-10-28

## Contexto
- Usaremos la familia Gemini 2.5 (Pro, Flash, Flash-Lite) con soporte de caching (descuento 90% en tokens cacheados).
- Necesitamos balancear costo, latencia y profundidad de razonamiento por agente.

## Decisión
- NEXUS (orquestador): `gemini-2.5-pro` para síntesis y resolución de conflictos.
- Agentes conversacionales: `gemini-2.5-flash` por defecto.
- Clasificaciones ligeras / prechecks: `gemini-2.5-flash-lite`.
- Habilitar caching implícito y explícito (TTL 1 hora) con objetivo de hit-rate ≥50%.

## Justificación
- **Ventana de contexto**: Pro/Flash/Flash-Lite aceptan 1,048,576 tokens de entrada y hasta 65,536 tokens de salida, suficiente para memorias extensas.
- **Costo** (por 1M tokens, Oct 2025):
  - Pro: input $1.25 / cached $0.125 / output $10.00.
  - Flash: input $0.30 / cached $0.030 / output $2.50.
  - Flash-Lite: input $0.10 / cached $0.010 / output $0.40.
- **Latencia**: Flash/Flash-Lite entregan p95 <2 s en prompts medianos; Pro puede llegar a 5–6 s pero con razonamiento superior.

## Heurística de Selección
- Lite: tareas <500 tokens (clasificación, preflight, selección de agente).
- Flash: conversación estándar (<10k tokens), planes diarios, respuestas rápidas.
- Pro: solicitudes multitagente (>50k tokens), conflictos entre agentes, agregación de planes y personalización profunda.

## Caching y Cost Control
- TTL inicial: 1 hora; podemos extender a 6 h para prompts estables (system prompts, instrucciones de agentes).
- Métricas obligatorias: `usage_metadata.cached_content_token_count`, `prompt_token_count`, `candidates_token_count`.
- Circuit breakers: si costo estimado > presupuesto, degradar (resumen más corto, pedir confirmación).
- Guardar embeddings recortados para reusar contexto en `pgvector`; pedir al LLM solo delta.

## Consecuencias
- Implementar `CostCalculator` compartido con fórmulas oficiales.
- Loggear costo estimado y real por respuesta para tuning.
- Ajustar prompts para maximizar cache hits (plantillas estables + variables mínimas).

## Referencias
- Vertex AI Pricing (Oct 2025).
- Documentación de caching Gemini 2.5.
