# Praxis

Framework de investigación estructurada y planificación para Claude Code. Transforma señales crudas en conocimiento validado y acción concreta.

## Flujo

```
                        /praxis [input]
                             │
                    ┌────────┴────────┐
                    │  Reconocimiento  │
                    │  (repo, tools,   │
                    │   online)        │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │ Detección de     │
                    │ fase             │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        /discover      /hypothesize    /roadmap
        Exploración    Investigación   Planificación
        abierta        5 fases         epics→tasks
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                        Implementación
```

Cada fase es independiente. `/praxis` detecta en qué fase está el input y delega al skill correcto. Reinvocable sobre el mismo documento conforme avanza.

## Instalación

```bash
git clone https://github.com/pablontiv/praxis.git /home/praxis
cd /home/praxis
git config core.hooksPath .hooks

# Sincronizar skills globalmente
.hooks/pre-push
```

Esto copia los skills a `~/.claude/skills/`, haciéndolos disponibles en cualquier proyecto de Claude Code. El hook `pre-push` también ejecuta esta sincronización automáticamente en cada push.

### Dependencias

| Dependencia | Requerida por | Instalación |
|-------------|---------------|-------------|
| [`rootline`](https://github.com/pablontiv/rootline) | `/roadmap` (todos los subcomandos) | `curl -fsSL https://raw.githubusercontent.com/pablontiv/rootline/master/install.sh \| bash` |
| [`backscroll`](https://github.com/pablontiv/backscroll) | `/backscroll` (búsqueda de sesiones) | `cd /opt/backscroll && cargo build --release && cp target/release/backscroll /usr/local/bin/` |

`rootline` es un motor de base de datos sobre filesystem que trata directorios como tablas, archivos como records, y YAML frontmatter como metadata. `/roadmap` lo usa para validación, queries, auto-numbering, scaffolding y grafos de dependencia.

## Quick Start

```bash
# Ver estado actual del framework
/praxis

# Iniciar flujo con un tema nuevo
/praxis nombre-del-tema

# Continuar un documento existente (detecta fase automáticamente)
/praxis docs/research/mi-investigacion.md

# Usar skills directamente (sin proxy)
/discover init mi-proyecto
/hypothesize tema-a-investigar
/roadmap texto libre para descomponer
```

## Skills

| Skill | Descripción | Cuándo se invoca |
|-------|-------------|------------------|
| `/praxis [input]` | Proxy inteligente. Reconoce entorno, detecta fase, delega. | Punto de entrada principal. Usar siempre que no se sepa qué skill invocar. |
| `/discover [sub]` | Exploración abierta con ciclos Plan-Act-Observe-Reflect. | Ideas nuevas, preguntas abiertas, exploración sin hipótesis previa. |
| `/hypothesize [tema]` | Investigación estructurada de 5 fases con trazabilidad lógica. | Claims que necesitan validación, investigación con método, falsación. |
| `/roadmap [args]` | Descomposición en epics → features → stories → tasks. | Specs listos para planificar, trabajo listo para ejecutar. |
| `/backscroll [query]` | Búsqueda full-text en historial de sesiones (FTS5 + BM25). | Recuperar contexto de sesiones anteriores. |

### /praxis — Proxy del Flujo

Punto de entrada único. Antes de delegar:
1. **Reconoce el entorno**: estructura del repo, dependencias, git, framework state, búsqueda online
2. **Detecta la fase del input**: marcadores de investigación, artefactos roadmap, líneas discover
3. **Delega al skill correcto** con todo el contexto recolectado

Acepta: archivo `.md`, tema corto, o vacío (muestra estado).

### /discover — Exploración Abierta

Framework de R&D con líneas de investigación independientes.

| Subcomando | Qué hace |
|------------|----------|
| `init` | Inicializa el framework (MAP.md, directorios, templates) |
| `new-line [nombre]` | Crea nueva línea de investigación |
| `cycle [línea]` | Ejecuta un ciclo PAOR en una línea |
| `reflect [línea]` | Reflexión sobre ciclos acumulados |
| `theory [nombre]` | Documenta una teoría emergente |
| `status` | Muestra estado actual del framework |
| `update-map` | Actualiza MAP.md con estado real |
| `interlink` | Busca conexiones entre líneas |
| `review-patterns` | Revisa patrones emergentes |
| `research [tema]` | Investigación con anti-presuposiciones |
| `@file` | Analiza archivo externo (intake) |

### /hypothesize — Investigación Estructurada

Investigación de 5 fases con trazabilidad lógica completa:

1. **Fase 1**: Idea → Tesis (axiomas, decisiones, modelo deseado)
2. **Fase 2**: Tesis → Plan de investigación (hipótesis, CAPs, criterios)
3. **Fase 3**: Investigación → Argumento actualizado (matriz premisa-evidencia)
4. **Fase 4**: Argumento → Factibilidad (claims técnicos, Go/No-Go)
5. **Fase 5**: Factibilidad → Prototipo (validación operacional)

Tres modos de entrada:
- **CREAR**: tema nuevo → flujo interactivo desde Paso 0
- **SEGUIMIENTO**: archivo existente → detecta fase y continúa
- **DIRECTO**: contenido con claims → extrae y estructura

### /roadmap — Planificación AI-Native

Descomposición jerárquica: Epic > Feature > Story > Task.

| Subcomando | Qué hace |
|------------|----------|
| *(texto libre)* | Descomposición autónoma desde descripción |
| `pending` | Muestra tasks pendientes |
| `loop` | Ejecuta tasks secuencialmente |
| `plan` | Genera plan desde contexto de conversación |

Requiere [`rootline` CLI](#dependencias) — no opera sin ella.

### /backscroll — Historial

Busca en sesiones anteriores de Claude Code usando backscroll (FTS5 full-text search con ranking BM25). Resultados rankeados por relevancia, no solo coincidencia textual.

## Agents

| Agent | Descripción |
|-------|-------------|
| **grounded-theory-analyst** | Análisis Grounded Theory (Glaser & Strauss). Read-only. Para datos cualitativos sin estructura previa. |
| **sdd-validator** | Valida cadena de trazabilidad del roadmap (Epic→Feature→Story→Task). Lee `roadmap-root` desde `.claude/roadmap.local.md`. |

## Configuración por Proyecto

### roadmap-root

Crear `.claude/roadmap.local.md` en el proyecto:

```yaml
---
roadmap-root: docs/epics
---
```

Define dónde vive la jerarquía del roadmap. Usado por `/roadmap` y `sdd-validator`.

### State files (generados automáticamente)

| Archivo | Generado por | Propósito |
|---------|-------------|-----------|
| `MAP.md` | `/discover init` | Mapa general del framework |
| `.claude/rules/current-state.md` | `/discover` | Estado actual de líneas y fases |
| `.claude/rules/connections.md` | `/discover interlink` | Conexiones entre líneas |

## Estructura del Repo

```
.claude/
├── skills/
│   ├── praxis/           ← proxy inteligente
│   ├── discover/         ← exploración + templates
│   ├── hypothesize/      ← investigación 5 fases
│   ├── roadmap/          ← planificación + guías
│   └── backscroll/       ← historial (FTS5 via backscroll)
├── agents/               ← grounded-theory, sdd-validator
├── rules/                ← praxis-pipeline.md
└── hooks/                ← SessionStart hook
.hooks/
├── pre-push              ← sincroniza skills en push
└── post-merge            ← sincroniza skills en pull
```
