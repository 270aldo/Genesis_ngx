# Arquitectura de Referencia para Sistemas Multi-Agente (ADK + A2A + GCP)

**Versión del Documento:** 1.0
**Fecha:** Noviembre 2025
**Contexto:** Basado en la implementación exitosa de *Genesis NGX*.

---

## 1. Resumen Ejecutivo

Este documento establece los estándares de ingeniería para el desarrollo, despliegue y orquestación de sistemas multi-agente utilizando el **Google Agent Development Kit (ADK)** y el protocolo **Agent-to-Agent (A2A)** sobre infraestructura de **Google Cloud Platform (GCP)**.

El objetivo es trascender la prueba de concepto y construir sistemas resilientes, escalables y seguros, donde la Inteligencia Artificial (Vertex AI) se integra con lógica determinista en una arquitectura de microservicios.

---

## 2. Filosofía de Diseño: El Modelo "Nexus"

La arquitectura se basa en un modelo de **Orquestador y Especialistas**:

*   **Nexus (El Cerebro/Router):** Un agente central ligero cuya única responsabilidad es entender la intención del usuario (Intent Classification) y enrutar la solicitud. No ejecuta tareas especializadas.
*   **Agentes Especialistas (Los Músculos):** Microservicios aislados (Fitness, Nutrición, Salud Mental) que ejecutan lógica de negocio específica. Son agnósticos al usuario final; solo responden a solicitudes A2A.
*   **Infraestructura Inmutable:** Nada se configura manualmente ("ClickOps"). Todo recurso en la nube nace a partir de código (Terraform).

---

## 3. Desarrollo del Agente (Capa de Aplicación)

### 3.1. Gestión de Dependencias (La Lección Crítica)
El ecosistema de IA en Python evoluciona rápido. El conflicto entre `google-adk`, `fastapi`, `starlette` y `pydantic` es común.

**Estrategia de Resolución ("The Nuclear Fix"):**
*   **No fijar versiones estrictas (`==`)** en librerías de alto nivel (`fastapi`, `uvicorn`) a menos que sea estrictamente necesario por un bug conocido.
*   **Uso de Rangos (`>=`):** Permite a `pip` resolver el grafo de dependencias complejo.
*   **Segregación:** Mantener un `requirements.txt` base y uno específico por agente si divergen mucho, aunque el Monorepo suele beneficiarse de dependencias compartidas para consistencia.

### 3.2. Configuración Tipada (Pydantic Settings)
Jamás usar `os.getenv('VAR')` disperso por el código.
*   **Implementación:** Clase centralizada `config.py` usando `BaseSettings` de Pydantic.
*   **Beneficio:** Validación automática al inicio. Si falta la `GEMINI_PROJECT_ID`, el contenedor falla inmediatamente (Fail Fast) en lugar de fallar silenciosamente en tiempo de ejecución.

### 3.3. El Cliente de IA (Gemini Wrapper)
*   **Abstracción:** No llamar a `vertexai` directamente en los controladores. Usar una clase `GeminiClient`.
*   **Modo Híbrido (Mock vs Real):** Implementar un flag `MOCK_GEMINI` en el cliente.
    *   *Local/CI:* Devuelve respuestas predecibles instantáneas.
    *   *Prod:* Conecta a Vertex AI.
    *   *Por qué:* Ahorra dinero y tiempo durante el desarrollo de lógica de enrutamiento.

---

## 4. Infraestructura como Código (Terraform)

La infraestructura no es un "afterthought", es la base.

### 4.1. El "Bootstrap" de APIs
Antes de crear recursos, se deben habilitar las capacidades del proyecto. Terraform debe gestionar la activación de:
*   `serviceusage.googleapis.com` (La llave maestra).
*   `aiplatform.googleapis.com` (Vertex AI).
*   `run.googleapis.com` (Cómputo).
*   `secretmanager.googleapis.com` (Seguridad).

### 4.2. Identidad y Seguridad (IAM)
*   **Principio de Menor Privilegio:** Cada agente (Cloud Run Service) debe tener su propia **Service Account**.
*   **Nexus SA:** Solo permisos para invocar a Vertex AI y a los otros agentes (Cloud Run Invoker).
*   **No usar llaves JSON en producción:** En Cloud Run, la identidad es inyectada automáticamente. Las llaves `.json` son **solo** para desarrollo local.

---

## 5. Flujo de Desarrollo Local (La Estrategia Híbrida)

Desarrollar en la nube es lento. Desarrollar localmente sin nube es irreal. La solución es el **Entorno Híbrido**.

### 5.1. Docker Compose con Inyección de Credenciales
El contenedor local no tiene acceso a GCP por defecto.
*   **Solución:** Montar las Application Default Credentials (ADC) del host al contenedor.
    ```yaml
    volumes:
      - ~/.config/gcloud/application_default_credentials.json:/app/credentials.json:ro
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
    ```
*   **Beneficio:** Permite probar la IA real (Vertex AI) desde tu laptop sin desplegar.

### 5.2. Gestión de Conflictos de Autenticación
*   **Problema:** Variables de entorno globales (`GOOGLE_APPLICATION_CREDENTIALS`) en la máquina host que apuntan a proyectos antiguos.
*   **Solución:** Limpieza de sesión (`unset`) antes de operaciones críticas (Terraform/Docker) y uso estricto de `gcloud auth application-default login` por proyecto.

---

## 6. Protocolo A2A (Agent-to-Agent)

### 6.1. Enrutamiento Semántico
El orquestador no usa `if/else` simples. Usa **Intent Classification**.
1.  **Input:** "Quiero una rutina de espalda".
2.  **Vertex AI (Flash Model):** Clasifica -> `intent: plan_workout`, `confidence: 0.98`.
3.  **Router:** Mapea `plan_workout` -> `AGENT_FITNESS_URL`.
4.  **Dispath:** Envía el payload JSON al agente especialista.

### 6.2. Comunicación Síncrona
Para MVP y V1, usar HTTP REST (FastAPI) entre agentes es superior a colas de mensajes (Pub/Sub) por simplicidad y facilidad de depuración.

---

## 7. Checklist para Nuevos Proyectos

1.  **Inicialización:** Crear repo + `requirements.txt` relajado.
2.  **Infraestructura:** `terraform init` -> Habilitar APIs (manual o script bootstrap si Service Usage está off).
3.  **Local:** `docker-compose` con montaje de credenciales.
4.  **Validación:** Script de integración (`test_local_integration.py`) que pruebe el flujo completo (User -> Nexus -> Agent) en local antes del primer `gcloud run deploy`.

---

**Autor:** Gemini CLI (Asistente de Ingeniería)
**Proyecto:** Genesis NGX
