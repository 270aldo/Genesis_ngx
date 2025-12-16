# ADR-008: Decisiones de Producción para México

**Estado**: Aceptado
**Fecha**: 2025-12-14
**Decisores**: Aldo (CEO/Arquitecto), Claude Opus 4.5 (Co-Arquitecto)

## Contexto

Genesis NGX v1.0.0 está implementado con 13 agentes, 1106 tests y 90% de cobertura. Este ADR documenta las decisiones necesarias para llevar el sistema a producción en México, considerando:

1. Requisitos de residencia de datos
2. Estrategia de autenticación
3. Datos de salud a capturar (compliance LFPDPPP)
4. Capacidad inicial esperada

## Decisiones

### 1. Residencia de Datos: México (Requerida)

**Decisión**: Los datos de usuarios mexicanos deben residir en una región compatible con México.

**Implementación**:
- **GCP Region**: `us-central1` (Iowa) - Latencia aceptable (~40ms a CDMX), soporte completo de Agent Engine
- **Supabase**: Región `us-central-1` o `us-east-1` (verificar disponibilidad)
- **Alternativa futura**: Migrar a `southamerica-west1` (Santiago) cuando Agent Engine esté disponible ahí

**Justificación**:
- La LFPDPPP no requiere estrictamente que los datos estén en México, pero sí que haya medidas de protección adecuadas
- `us-central1` tiene latencia aceptable y todos los servicios GCP necesarios
- Evita complejidad de multi-región en v1

### 2. Autenticación del Gateway: Supabase JWT

**Decisión**: Usar Supabase Auth con JWT para autenticación del Gateway.

**Implementación**:
- Gateway valida JWT firmado por Supabase
- Extrae `user_id` del claim `sub`
- Claims adicionales en `app_metadata` para roles de agente
- Mismo patrón que RLS existente (`auth.uid()`)

**Justificación**:
- Reutiliza infraestructura existente de Supabase Auth
- Consistente con el patrón de seguridad ya implementado (RLS + RPCs)
- Evita complejidad de OIDC propio en v1
- Los tokens son verificables sin llamada a Supabase (JWT firmado)

**Alternativa rechazada**: OIDC propio - Mayor control pero complejidad innecesaria para v1.

### 3. Datos de Salud: Sistema de Tiers con Consentimiento

**Decisión**: Implementar un sistema de 3 tiers para `health_metrics.metric_type`.

#### Tier 1: Habilitado por Defecto (con Aviso de Privacidad básico)

| metric_type | Descripción | Unidad |
|-------------|-------------|--------|
| `weight_kg` | Peso corporal | kg |
| `height_cm` | Altura | cm |
| `steps_daily` | Pasos diarios | count |
| `active_minutes` | Minutos de actividad | min |
| `calories_burned` | Calorías quemadas | kcal |
| `water_ml` | Hidratación | ml |
| `sleep_hours` | Horas de sueño | hours |

**Justificación**: Datos estándar de fitness que no revelan "estado de salud" bajo LFPDPPP.

#### Tier 2: Con Consentimiento Adicional (checkbox)

| metric_type | Descripción | Unidad |
|-------------|-------------|--------|
| `body_fat_percentage` | Porcentaje de grasa corporal | % |
| `muscle_mass_kg` | Masa muscular | kg |
| `resting_hr_bpm` | Frecuencia cardíaca en reposo | bpm |
| `sleep_quality_score` | Puntuación de calidad de sueño | 1-100 |

**Consentimiento requerido**: Checkbox en onboarding: "Autorizo el uso de datos de composición corporal y signos vitales básicos para recomendaciones personalizadas."

**Justificación**: Podrían inferir estado de salud indirectamente. Consentimiento adicional mitiga riesgo legal.

#### Tier 3: Excluido de v1 (Datos Sensibles LFPDPPP)

| metric_type | Motivo de exclusión |
|-------------|---------------------|
| `blood_glucose` | Dato de salud explícito |
| `blood_pressure_systolic` | Dato de salud explícito |
| `blood_pressure_diastolic` | Dato de salud explícito |
| `hrv_ms` | Puede revelar condiciones cardíacas |
| `menstrual_cycle_*` | Dato sensible de salud reproductiva |
| `body_temperature` | Puede revelar enfermedades |
| `spo2_percentage` | Dato médico (saturación de oxígeno) |

**Justificación**:
- La LFPDPPP 2025 define estos como "datos personales sensibles"
- Requieren consentimiento **explícito y por escrito** (firma, e-firma)
- Sanciones: 100-320,000 UMAs (~$1,200-$3.8M USD)
- Diferir a v2 con consulta legal formal

#### LUNA (Agente de Salud Femenina)

**Decisión**: En v1, LUNA operará **solo conversacionalmente**.

- NO persistirá datos de ciclo en `health_metrics`
- Puede dar consejos basados en información que el usuario mencione en la conversación
- Tracking de ciclo con persistencia diferido a v2

**Justificación**: Datos de ciclo menstrual son explícitamente sensibles bajo LFPDPPP.

### 4. Capacidad Inicial: ~100 Usuarios Q1

**Decisión**: Diseñar para 100 usuarios en el primer trimestre.

**Implementación**:
- `min_instances: 1` para Gateway (evitar cold start)
- `min_instances: 0` para agentes especializados Flash
- `min_instances: 1` para GENESIS_X (orquestador siempre caliente)
- Budget estimado: $20-50/mes

**Justificación**:
- Lanzamiento controlado con beta users
- Scale-to-zero para agentes Flash reduce costos
- Gateway siempre disponible mejora experiencia

## Consecuencias

### Positivas

1. **Compliance LFPDPPP**: Sistema diseñado para cumplimiento desde el inicio
2. **Simplicidad**: Supabase Auth reutiliza infraestructura existente
3. **Escalabilidad**: Sistema de tiers permite expansión gradual de datos
4. **Costo controlado**: Diseño para 100 usuarios minimiza gastos iniciales

### Negativas

1. **Funcionalidad limitada**: Tier 3 y tracking de ciclo diferidos
2. **Latencia**: `us-central1` no es óptimo para México (~40ms vs ~15ms local)
3. **Dependencia**: Fuerte dependencia de Supabase Auth

### Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Interpretación legal incorrecta | Media | Alto | Consultar abogado antes de v2 |
| Supabase Auth outage | Baja | Alto | Monitoreo, runbook de incident |
| Usuarios requieren datos Tier 3 | Media | Medio | Roadmap claro, comunicación |
| Costos exceden presupuesto | Baja | Medio | Budget alerts, autoscaling limits |

## Referencias

- [LFPDPPP 2025 - Lexology Analysis](https://www.lexology.com/library/detail.aspx?g=f633c3f8-1591-4a91-a2f2-255b97a107e1)
- [INAI Guía de Obligaciones](https://home.inai.org.mx/wp-content/documentos/DocumentosSectorPrivado/Guia_obligaciones_lfpdppp_junio2016.pdf)
- [SecurePrivacy LFPDPPP Guide 2025](https://secureprivacy.ai/blog/mexico-privacy-law-lfpdppp-2025)
- [Health Connect Data Types - Android](https://developer.android.com/health-and-fitness/guides/health-connect/plan/data-types)
- [ADR-005: Seguridad y Cumplimiento](./005-security-compliance.md)
- [ADR-007: Migración a Agent Engine](./ADR-007-agent-engine-migration.md)

## Notas

Este ADR establece las bases legales y técnicas para el lanzamiento en México. Los datos de Tier 3 y el tracking de ciclo para LUNA se abordarán en un ADR separado (ADR-009) cuando se cuente con asesoría legal formal.
