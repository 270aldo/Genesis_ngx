# Multi-stage build para imagen más pequeña
FROM python:3.12-slim as builder

# Instalar dependencias de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copiar requirements y instalar dependencias
COPY agents/nutrition/requirements.txt .
# Necesitamos copiar el root requirements porque el de nutrition lo referencia
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
    PORT=8082

# Instalar curl para healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd -m -u 1000 nutrition && \
    mkdir -p /app && \
    chown -R nutrition:nutrition /app

WORKDIR /app

# Copiar dependencias desde builder
COPY --from=builder --chown=nutrition:nutrition /root/.local /home/nutrition/.local

# Copiar código de la aplicación
COPY --chown=nutrition:nutrition agents/ /app/agents/

# Cambiar a usuario no-root
USER nutrition

# Agregar .local/bin al PATH
ENV PATH=/home/nutrition/.local/bin:$PATH

# Exponer puerto
EXPOSE 8082

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8082/healthz || exit 1

# Comando por defecto
CMD ["uvicorn", "agents.nutrition.main:app", "--host", "0.0.0.0", "--port", "8082"]
