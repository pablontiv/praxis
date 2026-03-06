---
name: praxis
description: |
  Intelligent router for the research-to-implementation pipeline. Classifies
  any input (file, topic, or empty) and delegates to the right skill: discover
  for open exploration, hypothesize for evidence-based evaluation, or roadmap
  for project decomposition. Use this skill when the user wants to process a
  document or topic through a structured workflow, check project status, resume
  previous work, or figure out what to do next. Trigger on: "praxis", "procesar",
  "evaluar", "siguiente paso", "en que va", "continuar", "retomar", "que sigue",
  or when the user provides a file or topic and it's unclear which specific skill
  applies. Also use when the user asks for a general status overview of their
  research/planning state. Do NOT use for direct coding tasks (refactoring, tests,
  bug fixes, config) — those don't need skill routing.
user-invocable: true
argument-hint: "[archivo.md] | [tema] | (vacio = auto-detect)"
---

# /praxis — Proxy del Flujo

## Paso 0: Clasificar el input

Antes de cualquier I/O, determinar el tipo de input por inspeccion textual:

| Condicion | Tipo |
|-----------|------|
| `$ARGUMENTS` vacio | EMPTY |
| `$ARGUMENTS` termina en `.md` y el archivo existe | FILE |
| `$ARGUMENTS` empieza con `@` y el archivo (sin `@`) existe | FILE (strip `@`) |
| Cualquier otro caso | TOPIC |

## Paso 1: Reconocimiento por niveles

El reconocimiento es proporcional a la ambiguedad del input. No escanear mas de lo necesario.

### Tier 0 — FILE con marcadores (fast-path)

Cuando el input es FILE, leer el archivo y buscar marcadores conocidos:

| Marcador | Fase | Accion |
|----------|------|--------|
| `> Estado: Fase N` | Investigacion hypothesize en curso | -> `Skill: hypothesize $ARGUMENTS` |
| Template markers de QUESTION.md / FIELD-LOG.md | Linea discover activa | -> `Skill: discover cycle [nombre-linea]` |
| Frontmatter con `tipo:`, `estado:`, `epic:` | Artefacto roadmap | Verificar rootline (`command -v rootline`). Si OK -> `Skill: roadmap pending`. Si no -> informar instalacion y PARAR. |

Si se detecta un marcador: mostrar al usuario que se detecto, que skill se invoca, y delegar. **No escanear repo, no revisar estado del framework.** El marcador es suficiente.

Si NO se detecta ningun marcador: el archivo es externo o desconocido. Caer a Tier 1 para obtener contexto antes de clasificar.

### Tier 1 — Estado del framework (lightweight)

Aplica cuando: input es EMPTY, TOPIC, o FILE sin marcadores.

Leer en paralelo (solo lo que existe):
- `.claude/rules/current-state.md` — estado actual
- Existencia de `MAP.md` — discover inicializado?
- Contenido de `lines/` — lineas activas (nombres y QUESTION.md)
- Contenido de `theories/` — teorias existentes
- Existencia de `.claude/roadmap.local.md` — roadmap configurado?

#### Si EMPTY:
Presentar estado del framework:
- Lineas activas y su fase
- Investigaciones en curso (buscar `> Estado: Fase` en *.md del root)
- Roadmap: configurado? items pendientes?
- Sugerir siguiente accion basada en el estado

No delegar. Responder directamente.

#### Si TOPIC:
Buscar trabajo existente sobre el tema:
1. Buscar en `lines/` carpeta con nombre similar
2. Buscar en `theories/` documento relacionado
3. Buscar investigaciones (`> Estado: Fase`) sobre el tema
4. Si existe -> preguntar al usuario: continuar existente o crear nuevo?
5. Si no existe -> caer a Tier 2

#### Si FILE sin marcadores:
Caer a Tier 2 para clasificacion completa.

### Tier 2 — Reconocimiento completo (solo cuando necesario)

Aplica cuando: TOPIC sin trabajo previo, o FILE sin marcadores.

Ejecutar en paralelo:

**Repo y proyecto:**
- Estructura del proyecto (Glob: top-level patterns)
- Dependencias (package.json, Cargo.toml, requirements.txt, etc.)
- README principal
- Branch actual y estado de git

**Online (solo si el input involucra un tema nuevo):**
- Buscar estado del arte, documentacion oficial, alternativas
- Anclar en evidencia externa antes de proceder

Luego proceder a Paso 2 con el contexto completo.

## Paso 2: Clasificar y delegar

Para archivos sin marcadores o temas nuevos, clasificar usando senales de intake
(structure, assertions, evidence, actionability, domain, completeness).

Mapear a skill y **ejecutar directamente** (no solo sugerir):

| Clasificacion | Skill invocado | Contexto que recibe |
|---------------|---------------|---------------------|
| Idea exploratoria (bajo en assertions, sin evidencia) | `Skill: discover new-line [tema]` | Reconocimiento del Tier 1/2 |
| Claims sin validar (alto en assertions, sin/poca evidencia) | `Skill: hypothesize [contenido]` | Reconocimiento + busqueda online |
| Investigacion con evidencia | `Skill: hypothesize [archivo]` | Reconocimiento del Tier 1/2 |
| Specs/requirements listos para descomponer | `Skill: roadmap [contenido]` | Reconocimiento + docs del repo |
| Codigo/datos | Sugerir attach a linea existente | — |

Antes de delegar, mostrar al usuario:
- Que se detecto (fase, clasificacion)
- Que skill se va a invocar y por que
- Resumen del contexto relevante (proporcional al tier usado)

Preguntar confirmacion solo si la clasificacion tiene confianza < alta.
