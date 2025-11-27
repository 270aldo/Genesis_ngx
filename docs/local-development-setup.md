# Guia de Setup para Desarrollo Local

Esta guia te llevara paso a paso por el proceso de configurar Genesis NGX en tu maquina local para desarrollo.

## Requisitos Previos

### Software Requerido

1. **Python 3.12+**
   ```bash
   python --version  # Debe ser 3.12 o superior
   ```

2. **Git**
   ```bash
   git --version
   ```

3. **Google Cloud SDK** (para Vertex AI / Gemini)
   ```bash
   gcloud --version
   ```

4. **Google ADK CLI** (Agent Development Kit)
   ```bash
   pip install google-adk
   adk --version
   ```

5. **Supabase CLI** (opcional, para base de datos local)
   ```bash
   brew install supabase/tap/supabase  # macOS
   # o
   npm install -g supabase
   ```

### Cuentas Requeridas

1. **Google Cloud Platform**
   - Proyecto con Vertex AI API habilitada
   - Application Default Credentials configuradas

2. **Supabase** (puede ser local o cloud)
   - Proyecto creado en https://supabase.com
   - URL y keys copiadas

## 1. Clonar el Repositorio

```bash
git clone https://github.com/270aldo/Genesis_ngx.git
cd Genesis_ngx
```

## 2. Crear Entorno Virtual

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

## 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

## 4. Configurar Variables de Entorno

```bash
cp .env.example .env.local
```

Edita `.env.local` con tus credenciales:

```env
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key

# Google Cloud (opcional - usa ADC por defecto)
GOOGLE_CLOUD_PROJECT=tu-proyecto-gcp
```

## 5. Autenticar con Google Cloud

```bash
# Configurar Application Default Credentials
gcloud auth application-default login

# Configurar proyecto
gcloud config set project tu-proyecto-gcp
```

## 6. Ejecutar Agentes con ADK

### Opcion A: ADK Playground (Recomendado)

```bash
# Inicia el playground web con todos los agentes
adk web
```

Esto abre un playground en `http://localhost:8000` donde puedes:
- Probar cada agente individualmente
- Ver las tools disponibles
- Ejecutar conversaciones de prueba

### Opcion B: Ejecutar Agente Especifico

```bash
# Ejecutar GENESIS_X
adk run genesis_x

# Ejecutar BLAZE
adk run blaze

# Ejecutar SAGE
adk run sage
```

## 7. Ejecutar Tests

```bash
# Todos los tests
pytest agents/ -v

# Tests de un agente especifico
pytest agents/genesis_x/tests/ -v

# Con coverage
pytest --cov=agents --cov-report=html
open htmlcov/index.html
```

## 8. Linting

```bash
# Verificar estilo de codigo
ruff check agents/

# Auto-fix problemas
ruff check --fix agents/

# Formatear codigo
ruff format agents/
```

## 9. Base de Datos (Supabase)

### Opcion A: Supabase Cloud

1. Crea proyecto en https://supabase.com
2. Copia URL y keys a `.env.local`
3. Aplica migraciones desde SQL Editor

### Opcion B: Supabase Local

```bash
# Inicializar Supabase local
supabase init
supabase start

# Aplicar migraciones
supabase db push

# Ver estado
supabase status
```

## Estructura del Proyecto

```
Genesis_ngx/
├── agents/
│   ├── genesis_x/      # Orquestador principal
│   │   ├── agent.py    # Definicion ADK
│   │   ├── tools.py    # FunctionTools
│   │   ├── prompts.py  # System prompts
│   │   └── tests/
│   │
│   ├── blaze/          # Fuerza/hipertrofia
│   ├── sage/           # Nutricion
│   └── shared/         # Codigo compartido
│
├── adk.yaml            # Configuracion ADK
├── requirements.txt    # Dependencias Python
└── pytest.ini         # Configuracion tests
```

## Comandos Utiles

| Comando | Descripcion |
|---------|-------------|
| `adk web` | Playground local |
| `adk run <agent>` | Ejecutar agente |
| `adk deploy --env staging` | Deploy a staging |
| `pytest agents/` | Ejecutar tests |
| `ruff check agents/` | Linting |

## Troubleshooting

### Error: "No module named google.adk"

```bash
pip install google-adk
```

### Error: "Could not automatically determine credentials"

```bash
gcloud auth application-default login
```

### Error: "Supabase connection failed"

Verifica que las variables de entorno estan configuradas:
```bash
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY
```

## Siguiente Paso

Ver [AGENTS.md](../AGENTS.md) para la guia completa de implementacion de agentes.
