# Multi-stage build para imagen más pequeña
FROM python:3.12-slim as builder

# Instalar dependencias de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copiar requirements y instalar dependencias
COPY agents/fitness/requirements.txt .
# Necesitamos copiar el root requirements porque el de fitness lo referencia
COPY requirements.txt ../../requirements.txt
RUN pip install --user --no-cache-dir -r requirements.txt

# =============================================================================
# Runtime stage
# =============================================================================
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8081

# Instalar curl para healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd -m -u 1000 fitness && \
    mkdir -p /app && \
    chown -R fitness:fitness /app

WORKDIR /app

# Copiar dependencias desde builder
COPY --from=builder --chown=fitness:fitness /root/.local /home/fitness/.local

# Copiar código de la aplicación
COPY --chown=fitness:fitness agents/ /app/agents/

# Cambiar a usuario no-root
USER fitness

# Agregar .local/bin al PATH
ENV PATH=/home/fitness/.local/bin:$PATH

# Exponer puerto
EXPOSE 8081

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8081/healthz || exit 1

# Comando por defecto
CMD ["uvicorn", "agents.fitness.main:app", "--host", "0.0.0.0", "--port", "8081"]
