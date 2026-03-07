---
name: praxis
description: |
  SIEMPRE usar este skill como punto de entrada por defecto cuando la intención
  del usuario no es clara o podría involucrar investigación, evaluación o
  planificación. Clasifica el input y delega al skill correcto: discover
  (exploración), hypothesize (decisiones con evidencia), o roadmap
  (descomposición de proyecto). Usar este skill siempre que el usuario
  proporcione un archivo para analizar, pregunte qué hacer a continuación,
  mencione continuar trabajo previo, pida un status general, o dé instrucciones
  ambiguas — incluso si no menciona "praxis" ni ningún skill específico, e
  incluso si parece una pregunta simple. Triggers: "que sigue", "siguiente paso",
  "status", "continuar", "retomar", "por donde empiezo", "what should I do",
  "next step", "resume", "en que va".
  (No para: tareas directas de código como refactoring, bug fixes, o config.)
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

Cuando el input es FILE, leer el archivo. Rutear por frontmatter primero (rootline-aware), marcadores inline como fallback:

**Si rootline esta disponible** (`command -v rootline`), leer metadata estructurada:
```bash
rootline query [file-dir] --where 'path == "[filename]"' --output json 2>/dev/null
```

Rutear segun campo `tipo` / `metodo` del frontmatter:

| Frontmatter | Fase | Accion |
|-------------|------|--------|
| `metodo == "hypothesize"` | Investigacion en curso | -> `Skill: hypothesize $ARGUMENTS` |
| `tipo == "question"` o `tipo == "field-log"` | Linea discover activa | -> `Skill: discover cycle [nombre-linea]` |
| `tipo` con valores roadmap (epic, feature, story, task) | Artefacto roadmap | -> `Skill: roadmap pending` o `roadmap loop` |
| Sin frontmatter reconocido | Archivo externo nuevo | -> Caer a Tier 1 |

**Fallback** (sin rootline): buscar marcadores inline:

| Marcador | Fase | Accion |
|----------|------|--------|
| `> Estado: Fase N` | Investigacion hypothesize en curso | -> `Skill: hypothesize $ARGUMENTS` |
| Template markers de QUESTION.md / FIELD-LOG.md | Linea discover activa | -> `Skill: discover cycle [nombre-linea]` |
| Frontmatter con `tipo:`, `estado:`, `epic:` | Artefacto roadmap | Verificar rootline (`command -v rootline`). Si OK -> `Skill: roadmap pending`. Si no -> informar instalacion y PARAR. |

Si se detecta un marcador: mostrar al usuario que se detecto, que skill se invoca, y delegar. **No escanear repo, no revisar estado del framework.**

Si NO se detecta ningun marcador: el archivo es externo o desconocido. Caer a Tier 1 para obtener contexto antes de clasificar.

### Tier 1 — Estado del framework (lightweight)

Aplica cuando: input es EMPTY, TOPIC, o FILE sin marcadores.

Leer en paralelo (solo lo que existe):
- `.claude/rules/current-state.md` — estado actual
- Existencia de `MAP.md` — discover inicializado?
- Existencia de `.claude/roadmap.local.md` — roadmap configurado?
- rootline CLI disponible? (`command -v rootline`)

Si rootline esta disponible, usarlo como mecanismo primario de deteccion:
```bash
# Lineas discover activas y pausadas
rootline query lines/ --where 'tipo == "question"' --count 2>/dev/null
rootline query paused/ --where 'tipo == "question"' --count 2>/dev/null
# Teorias
rootline query theories/ --count 2>/dev/null
# Investigaciones hypothesize
rootline query --where 'metodo == "hypothesize"' --output table 2>/dev/null
# Artefactos roadmap
rootline query --where 'isIndex == false' --count 2>/dev/null
```

**Fallback** (si rootline no disponible): escanear `lines/`, `theories/` manualmente, buscar `> Estado: Fase` en *.md, verificar MAP.md.

#### Si EMPTY:
Presentar estado del framework (current-state.md + rootline data):
- Lineas activas/pausadas y su fase
- Investigaciones en curso y su fase
- Roadmap: configurado? items pendientes?
- Sugerir siguiente accion basada en el estado

No delegar. Responder directamente.

#### Si TOPIC:
Buscar trabajo existente sobre el tema:
1. `rootline query lines/ --where 'tipo == "question"' --output table 2>/dev/null` — buscar linea con nombre similar
2. `rootline query theories/ --output table 2>/dev/null` — buscar teoria relacionada
3. `rootline query --where 'metodo == "hypothesize"' --output table 2>/dev/null` — investigaciones sobre el tema
4. **Fallback** (sin rootline): buscar en `lines/`, `theories/`, y `> Estado: Fase` en *.md
5. Si existe -> preguntar al usuario: continuar existente o crear nuevo?
6. Si no existe -> caer a Tier 2

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
