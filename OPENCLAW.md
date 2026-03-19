# Praxis para OpenClaw

Adaptación completa del framework praxis para funcionar en entornos OpenClaw.

## Qué es esto

[Praxis](https://github.com/pablontiv/praxis) es un framework de productividad AI-native
desarrollado por pablontiv. Esta es una adaptación completa que incluye los 8 skills,
2 agentes, rules y templates para funcionar en OpenClaw.

## Contenido

### Skills (8)

| Skill | Descripción | Archivo |
|-------|-------------|---------|
| `conform` | Auditar y estandarizar repos (seguridad, CI/CD, git hooks) | `.openclaw/skills/conform/SKILL.md` |
| `context-save` | Guardar contexto entre sesiones | `.openclaw/skills/context-save/SKILL.md` |
| `discover` | Framework R&D con ciclos PAOR | `.openclaw/skills/discover/SKILL.md` |
| `hypothesize` | Evaluar hipótesis con evidencia empírica | `.openclaw/skills/hypothesize/SKILL.md` |
| `praxis` | Meta-skill de orquestación | `.openclaw/skills/praxis/SKILL.md` |
| `preflight` | Validaciones pre-ejecución | `.openclaw/skills/preflight/SKILL.md` |
| `roadmap` | Planificación con epics/features/stories/tasks | `.openclaw/skills/roadmap/SKILL.md` |
| `test-loop` | Test runner inteligente | `.openclaw/skills/test-loop/SKILL.md` |

### Agentes (2)

| Agente | Descripción | Archivo |
|--------|-------------|---------|
| `grounded-theory-analyst` | Análisis de teoría fundamentada | `.openclaw/agents/grounded-theory-analyst.md` |
| `sdd-validator` | Validador de Software Design Documents | `.openclaw/agents/sdd-validator.md` |

### Rules (2)

| Rule | Descripción | Archivo |
|------|-------------|---------|
| `praxis-pipeline` | Pipeline de ejecución praxis | `.openclaw/rules/praxis-pipeline.md` |
| `skill-distribution` | Distribución de skills | `.openclaw/rules/skill-distribution.md` |

### Templates

| Categoría | Contenido | Ubicación |
|-----------|-----------|-----------|
| CI/CD | GitHub Actions workflows | `.openclaw/templates/ci/` |
| Seguridad | Dependabot, CodeQL, Scorecard | `.openclaw/templates/security/` |
| Configuración | Contributing, editor configs | `.openclaw/templates/config/` |
| Ecosistemas | Go, Rust, Node configs | `.openclaw/templates/ecosystems/` |

## Adaptaciones para OpenClaw

### Skills que funcionan nativamente (sin cambios)

| Skill | Notas |
|-------|-------|
| `conform` | Funciona con exec para gh CLI; sin gh = skips API checks |
| `context-save` | Requiere `rootline` — no disponible sin instalarlo |
| `hypothesize` | Research via web_search integrado |
| `preflight` | Validaciones con herramientas nativas |
| `praxis` | Orquestación con sessions_spawn |
| `test-loop` | Ejecuta tests vía exec |

### Skills adaptados (cambios menores)

| Skill | Adaptación |
|-------|------------|
| `discover` | Sin `rootline` → usa glob/read/grep; sin `backscroll` → usa memory_search |
| `roadmap` | Sin `rootline` → usa bash/grep para queries; estructura compatible |

## Integración con OpenClaw

### Tools disponibles

| Tool | Uso en skills |
|------|---------------|
| `read/write/edit` | Manipulación de archivos |
| `exec` | Ejecutar tests, git, gh CLI |
| `glob/grep` | Búsqueda de archivos |
| `web_search/kimi_search` | Investigación web |
| `memory_search` | Contexto de sesiones previas |
| `sessions_spawn` | Sub-agentes paralelos |
| `cron` | Recordatorios de seguimiento |

### Ejemplos de uso

```bash
# Conform - auditar repo
/conform --audit-only
/conform --apply

# Discover - investigación
/discover init mi-proyecto
/discover new-line tema-x
/discover cycle tema-x

# Roadmap - planificación
/roadmap pending
/roadmap plan

# Hypothesize - evaluar idea
/hypothesize "Kubernetes es mejor que Docker Swarm para este caso"

# Test-loop
/test-loop
/test-loop ./internal --once
```

## Estructura de archivos

```
.openclaw/
├── skills/
│   ├── conform/
│   │   ├── SKILL.md
│   │   ├── checks-reference.md
│   │   └── templates/
│   ├── context-save/
│   ├── discover/
│   │   ├── SKILL.md
│   │   ├── anti-presupposition.md
│   │   ├── ref-*.md
│   │   └── templates/
│   ├── hypothesize/
│   ├── praxis/
│   ├── preflight/
│   ├── roadmap/
│   │   ├── SKILL.md
│   │   ├── autonomous-mode.md
│   │   ├── loop-subcommand.md
│   │   └── templates/
│   └── test-loop/
├── agents/
│   ├── grounded-theory-analyst.md
│   └── sdd-validator.md
├── rules/
│   ├── praxis-pipeline.md
│   └── skill-distribution.md
└── templates/
    ├── ci/
    ├── security/
    ├── config/
    └── ecosystems/
```

## Instalación

### Opción 1: Copiar a tu workspace

```bash
# En tu repo o workspace personal
cp -r praxis/.openclaw/* .openclaw/
```

### Opción 2: Usar como referencia

Los skills pueden usarse como documentación de referencia sin copiar,
leyendo directamente desde el repo praxis.

## Diferencias con praxis original

| Característica | Praxis (Desktop) | Praxis (OpenClaw) |
|----------------|------------------|-------------------|
| CLI tools | rootline, backscroll | bash, grep, glob |
| Búsqueda en historial | backscroll search | memory_search |
| Validación schema | rootline validate | Manual (lee .stem) |
| Tree view | rootline tree | bash + find |
| Persistencia | ~/.claude/ | OpenClaw workspace |
| Web search | Tool externa | kimi_search integrado |
| Sub-agentes | No disponible | sessions_spawn |
| GitHub API | gh CLI local | gh CLI via exec o API |

## Workflow recomendado

1. **Iniciar**: Usar `/discover` para R&D o `/roadmap` para construcción
2. **Estandarizar**: Usar `/conform` para preparar repos
3. **Ejecutar**: Usar `/test-loop` para CI local
4. **Documentar**: Los skills crean archivos .md compatibles
5. **Sincronizar**: Git commit + PR via OpenClaw

## Beneficios de OpenClaw

- ✅ Sesiones persistentes (no dependen de máquina local)
- ✅ Web search integrado (sin API keys propias)
- ✅ Spawn de sub-agentes para paralelismo
- ✅ Cron para recordatorios
- ✅ Git integration directa para PRs
- ✅ Memoria semántica entre sesiones

## Limitaciones

- ⚠️ Sin validación automática de schema (sin rootline)
- ⚠️ Sin búsqueda full-text en historial (sin backscroll)
- ⚠️ gh CLI requiere auth setup en OpenClaw

## Contribuir

Esta adaptación mantiene compatibilidad upstream. Los archivos .md generados
son válidos tanto en praxis desktop como en OpenClaw.

Para mejoras:
1. Mantener compatibilidad de estructura
2. Documentar adaptaciones específicas
3. No agregar dependencias CLI externas

## Licencia

Misma licencia que praxis original (PolyForm Noncommercial).
