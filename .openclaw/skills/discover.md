---
source: pablontiv/praxis
name: discover
version: openclaw-adapted
description: |
  Framework R&D para exploración abierta adaptado a OpenClaw. Gestiona líneas de 
  investigación con ciclos Plan-Act-Observe-Reflect. Sin dependencia de rootline 
  o backscroll locales.
  
  Uso: /discover [init|new-line|cycle|reflect|status] o iniciar investigación 
  sobre un tema nuevo.
user-invocable: true
argument-hint: "[init|new-line|cycle|reflect|status|research] [args]"
requires:
  - filesystem access
  - Read/Write/Edit tools
  - web_search for research
  - memory_search for context
---

# /discover — Framework R&D para OpenClaw

Versión adaptada de praxis/discover para entornos OpenClaw.

## Diferencias con versión Claude Desktop

| Aspecto | Desktop | OpenClaw |
|---------|---------|----------|
| Almacenamiento | `.claude/rules/`, `lines/` | Workspace files (`discover/`) |
| Queries | `rootline query` | `glob` + `read` + `grep` |
| Historial | `backscroll search` | `memory_search` + session history |
| Investigación | Web search manual | `web_search`/`kimi_search` integrado |
| Persistencia | Local filesystem | OpenClaw workspace |

## Estructura en OpenClaw

```
workspace/
└── discover/                    # R&D project directory
    ├── .claude/
    │   └── current-state.md     # Estado actual del sistema
    ├── lines/                   # Líneas activas de investigación
    │   └── tema-x/
    │       ├── QUESTION.md      # Pregunta central
    │       └── FIELD-LOG.md     # Log de ciclos
    ├── paused/                  # Líneas pausadas
    ├── closed/                  # Líneas cerradas
    ├── theories/                # Teorías emergentes
    ├── intake/                  # Materiales externos
    └── backlog/                 # Preguntas pendientes
```

## Subcomandos

### init
Inicializa un proyecto R&D en el workspace.

```
/discover init mi-investigacion
```

### new-line
Crea una nueva línea de investigación.

```
/discover new-line kubernetes-networking
```

Proceso:
1. Anti-presupposition: detectar y reformular suposiciones
2. Crear QUESTION.md y FIELD-LOG.md
3. Documentar en current-state.md

### cycle
Documenta un ciclo Plan-Act-Observe-Reflect.

```
/discover cycle kubernetes-networking
```

### reflect
Reflexión estructurada sobre continuar/pausar/cerrar.

```
/discover reflect kubernetes-networking
```

### status
Muestra estado del sistema.

```
/discover status
```

### research
Investigación web con síntesis.

```
/discover research "service mesh comparison"
```

## Integración OpenClaw

### memory_search
Antes de iniciar nueva línea, buscar:
- ¿Se habló de este tema en sesiones previas?
- ¿Hay decisiones o hallazgos relacionados?

### web_search / kimi_search
Para investigación lateral durante ciclos:
```
/discover research "pattern X implementation"
```

### sessions_spawn
Para investigación paralela sin bloquear:
- Spawn sub-agent para research profundo
- Recolectar hallazgos al finalizar

## Workflow típico

```
# Iniciar investigación
/discover init mi-proyecto
/discover new-line arquitectura-alternativa

# Ciclo de investigación
[Usuario describe lo que hará]
/discover cycle arquitectura-alternativa

# Reflexión
[Después de varios ciclos]
/discover reflect arquitectura-alternativa
→ DECIDE: CONTINUE / PAUSE / CLOSE / FORK

# Documentar teoría
[Si emerge patrón]
/discover theory "pattern-name"
```

## Documentos clave

### QUESTION.md
```yaml
---
tipo: question
estado: In exploration
linea: kubernetes-networking
---
# Pregunta central

## Suposiciones detectadas
## Alternativas generadas
## Reformulación
```

### FIELD-LOG.md
```yaml
---
tipo: field-log
linea: kubernetes-networking
ciclos_registrados: 3
---
# Log de campo

## Cycle 1 — 2026-03-12
### Intención
### Qué hice
### Observaciones
### Reflexión
```

## Limitaciones

- Sin rootline: no validación automática de schema
- Sin backscroll: búsqueda en historial limitada a memory_search
- Sin CLI: todo a través de herramientas OpenClaw

## Beneficios de OpenClaw

- ✅ Sesiones persistentes (no dependen de máquina local)
- ✅ Web search integrado
- ✅ Spawn de sub-agentes para paralelismo
- ✅ Cron para recordatorios de seguimiento
- ✅ Git integration directa para PRs
