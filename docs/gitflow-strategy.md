# GitFlow Strategy - Genesis NGX

## Estrategia de Branches

### Branches Principales

#### `main`
- **Propósito**: Código en producción, siempre deployable
- **Protección**: Requiere PR + 2 aprobaciones + todos los checks verdes
- **Deploy**: Automático a producción (Agent Engine)
- **Tags**: Cada release se tagea con semver (v1.0.0, v1.1.0, etc.)
- **Naming**: Siempre `main`

#### `develop`
- **Propósito**: Rama de integración, próxima release
- **Protección**: Requiere PR + 1 aprobación + checks verdes
- **Deploy**: Automático a ambiente de staging
- **Base para**: Todas las feature branches
- **Naming**: Siempre `develop`

### Branches de Trabajo

#### Feature Branches
- **Base**: `develop`
- **Naming**: `feature/<ticket>-<descripcion-corta>`
- **Ejemplos**:
  - `feature/GEN-123-fitness-agent`
  - `feature/GEN-124-gemini-integration`
- **Ciclo de vida**:
  1. Crear desde `develop`
  2. Desarrollar y commitear
  3. PR hacia `develop`
  4. Squash merge después de aprobación
  5. Borrar branch

#### Bugfix Branches
- **Base**: `develop`
- **Naming**: `fix/<ticket>-<descripcion-bug>`
- **Ejemplos**:
  - `fix/GEN-125-auth-validation`
  - `fix/GEN-126-streaming-timeout`
- **Ciclo de vida**: Igual que features

#### Hotfix Branches
- **Base**: `main` (emergencias en producción)
- **Naming**: `hotfix/<ticket>-<descripcion-critica>`
- **Ejemplos**:
  - `hotfix/GEN-127-rls-bypass`
  - `hotfix/GEN-128-memory-leak`
- **Ciclo de vida**:
  1. Crear desde `main`
  2. Fix rápido + tests
  3. PR hacia `main` Y `develop` (merge a ambas)
  4. Tag inmediato (v1.0.1)
  5. Deploy urgente
  6. Borrar branch

#### Release Branches
- **Base**: `develop`
- **Naming**: `release/<version>`
- **Ejemplos**:
  - `release/1.0.0`
  - `release/1.1.0`
- **Propósito**: Preparar release (testing final, docs, versioning)
- **Ciclo de vida**:
  1. Crear desde `develop` cuando está lista
  2. Solo bugfixes menores y docs
  3. PR hacia `main` + tag
  4. Merge de vuelta a `develop`
  5. Borrar branch

#### Agent-Specific Branches (Opcional)
- **Base**: `develop`
- **Naming**: `agent/<agent-name>/<descripcion>`
- **Ejemplos**:
  - `agent/fitness/initial-implementation`
  - `agent/nutrition/meal-planning`
- **Uso**: Para desarrollo de agentes nuevos con múltiples PRs

## Ambientes

### Development (Local)
- **Branch**: Cualquier feature/fix
- **Servicios**: Docker Compose (Supabase local, mocks de Gemini)
- **Variables**: `.env.local`
- **Deploy**: Manual (desarrollador)

### Staging
- **Branch**: `develop`
- **Servicios**: Agent Engine (staging), Supabase staging
- **Variables**: Secret Manager (staging/)
- **Deploy**: Automático en merge a `develop`
- **URL**: `https://staging-*.run.app`

### Production
- **Branch**: `main`
- **Servicios**: Agent Engine (prod), Supabase prod
- **Variables**: Secret Manager (prod/)
- **Deploy**: Automático en merge a `main` + manual approval
- **URL**: `https://api.genesis-ngx.com`

## Conventional Commits

### Formato
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Solo cambios en documentación
- `style`: Formateo, espacios (no afecta código)
- `refactor`: Refactorización sin cambiar funcionalidad
- `perf`: Mejora de performance
- `test`: Agregar o corregir tests
- `chore`: Cambios en build, dependencias, configs
- `ci`: Cambios en CI/CD

### Scopes (Opcional)
- `nexus`: Orquestador NEXUS
- `fitness`: Agente Fitness
- `nutrition`: Agente Nutrición
- `mental`: Agente Salud Mental
- `shared`: Código compartido
- `db`: Base de datos
- `infra`: Infraestructura

### Ejemplos
```bash
feat(nexus): add intent classification with Gemini Flash-Lite
fix(shared): correct cost calculation for cached tokens
docs(readme): update local setup instructions
refactor(fitness): extract workout planning to separate service
test(shared): add A2A client retry tests
chore(deps): upgrade FastAPI to 0.115.5
ci(deploy): add staging environment deployment
```

### Breaking Changes
```bash
feat(shared)!: change A2A client constructor signature

BREAKING CHANGE: A2AClient now requires base_url as first parameter
Migration: Update all client instantiations
```

## Pull Request Workflow

### 1. Crear Branch
```bash
# Asegurarse de estar en develop actualizado
git checkout develop
git pull origin develop

# Crear feature branch
git checkout -b feature/GEN-123-gemini-integration
```

### 2. Desarrollo
```bash
# Commits frecuentes con conventional commits
git add .
git commit -m "feat(shared): add Gemini client base implementation"

# Push regular (permite colaboración)
git push -u origin feature/GEN-123-gemini-integration
```

### 3. Preparar PR
```bash
# Actualizar con develop (rebase o merge)
git checkout develop
git pull origin develop
git checkout feature/GEN-123-gemini-integration
git rebase develop  # o git merge develop

# Resolver conflictos si existen
# Ejecutar tests
pytest agents/

# Ejecutar linting
ruff check agents/
```

### 4. Crear Pull Request
- **Título**: Igual al commit principal (ej: `feat(shared): add Gemini integration`)
- **Descripción**: Usar template en `.github/pull_request_template.md`
- **Labels**: Agregar `feature`, `P1`, etc.
- **Reviewers**: Al menos 1 (2 para main)
- **Linked Issue**: `Closes #123`

### 5. Code Review
- Revisar feedback
- Push de correcciones
- Re-request review

### 6. Merge
- **Squash and Merge** (recomendado para features/fixes)
  - Mantiene historia limpia
  - Un commit por feature en develop/main
- **Merge Commit** (para releases)
  - Preserva historia completa
- Borrar branch automáticamente

## Protección de Branches

### `main`
```yaml
Required reviews: 2
Required checks:
  - lint-test
  - security-scan
  - terraform-plan
Dismiss stale reviews: true
Require linear history: true
Require signed commits: false (opcional)
Allow force push: false
Allow deletions: false
```

### `develop`
```yaml
Required reviews: 1
Required checks:
  - lint-test
Dismiss stale reviews: true
Require linear history: false
Allow force push: false (solo admins)
Allow deletions: false
```

## Release Process

### 1. Preparar Release
```bash
# Desde develop actualizado
git checkout develop
git pull origin develop

# Crear release branch
git checkout -b release/1.0.0

# Actualizar versiones
# - agents/nexus/__init__.py: __version__ = "1.0.0"
# - CHANGELOG.md

git commit -m "chore(release): prepare 1.0.0"
git push -u origin release/1.0.0
```

### 2. Testing Final
- Ejecutar suite completa de tests
- Verificar staging
- Actualizar documentación
- Solo bugfixes críticos

### 3. Merge a Main
```bash
# PR de release/1.0.0 -> main
# Después de merge:
git checkout main
git pull origin main

# Crear tag
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

### 4. Merge de vuelta a Develop
```bash
# PR de release/1.0.0 -> develop
# O merge directo:
git checkout develop
git merge release/1.0.0
git push origin develop

# Borrar release branch
git branch -d release/1.0.0
git push origin --delete release/1.0.0
```

## Versionado Semántico

### Formato: MAJOR.MINOR.PATCH

- **MAJOR** (1.x.x): Breaking changes
- **MINOR** (x.1.x): Nuevas features (backward compatible)
- **PATCH** (x.x.1): Bugfixes

### Ejemplos
- `0.1.0`: MVP inicial
- `0.2.0`: Agregar agente Fitness
- `0.2.1`: Fix en clasificación de intents
- `1.0.0`: Primera versión producción
- `2.0.0`: Cambio de protocolo A2A v0.4

## Gestión de Conflictos

### Rebase vs Merge

**Usar Rebase** (preferido):
- Features pequeñas (<5 commits)
- Historia limpia y lineal
```bash
git checkout feature/mi-feature
git rebase develop
```

**Usar Merge**:
- Features grandes con múltiples colaboradores
- Releases
- Cuando el historial es importante
```bash
git checkout feature/mi-feature
git merge develop
```

### Resolver Conflictos
```bash
# Durante rebase
git rebase develop
# ... resolver conflictos en archivos
git add <archivos-resueltos>
git rebase --continue

# Durante merge
git merge develop
# ... resolver conflictos
git add <archivos-resueltos>
git commit -m "merge: resolve conflicts from develop"
```

## Comandos Útiles

### Setup Inicial
```bash
# Configurar Git
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

# Configurar GPG signing (opcional)
git config --global commit.gpgsign true
git config --global user.signingkey <key-id>
```

### Workflows Comunes
```bash
# Crear y cambiar a feature
git checkout -b feature/GEN-123-nueva-feature

# Ver estado
git status

# Ver ramas
git branch -a

# Actualizar develop local
git checkout develop && git pull origin develop

# Ver commits
git log --oneline --graph --all

# Deshacer último commit (mantener cambios)
git reset --soft HEAD~1

# Limpiar branches locales borradas en remoto
git fetch --prune
git branch -vv | grep ': gone]' | awk '{print $1}' | xargs git branch -d
```

## Referencias

- [Git Flow Original](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
