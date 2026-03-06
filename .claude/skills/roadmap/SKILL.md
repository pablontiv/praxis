---
name: roadmap
description: |
  Use when the user knows WHAT to build and needs to plan HOW — decomposing
  a project into structured, executable work items. Breaks systems down into
  epics, features, stories, and tasks with technical specs, acceptance criteria,
  and dependency tracking. Subcommands: pending (show remaining work), loop
  (execute tasks sequentially), plan (materialize approved decomposition).
  Without arguments shows a decision tree for prioritization.
  Trigger when the user: describes a system with multiple features/components
  and needs them organized before coding, asks "how should I structure this
  project", wants to check roadmap progress or remaining tasks, needs to
  execute pending tasks in order, or wants to convert approved research
  results into an implementation plan.
  Trigger phrases: "descomponer", "roadmap", "tasks pendientes", "loop",
  "planificar implementacion", "que falta", "estructura de trabajo",
  "ejecutar pendientes", "materializar plan", "ver progreso".
  DO NOT use when the user is still evaluating IF something is worth doing
  (that's hypothesize) or exploring a topic without clear requirements
  (that's discover).
argument-hint: "<texto libre> | [pending|loop|plan] [args]"
allowed-tools:
  - Write
  - Read
  - Grep
  - Glob
  - Bash
  - TaskCreate
  - TaskList
  - TaskUpdate
  - TaskGet
  - Skill
  - AskUserQuestion
  - ExitPlanMode
---
<!-- No editar. Fuente: repo pablontiv/praxis -->

# /roadmap — Framework de Planificación AI-Native

## Configuración del Proyecto — Bootstrap Obligatorio

**PRIMER PASO de CUALQUIER operación** (pending, loop, plan, sin argumentos, modo autónomo). Ejecutar SIEMPRE, ANTES de cualquier otra acción — incluyendo antes del gate check de rootline. Este paso NO requiere rootline.

1. Leer `.claude/roadmap.local.md`. Si no existe:
   - Preguntar al usuario: ¿Dónde vive el roadmap? (ej: `docs/epics`)
   - Crear `.claude/roadmap.local.md` con el frontmatter mínimo (ver template abajo)
2. Extraer `roadmap-root` del frontmatter. Si falta → preguntar y actualizar el archivo.
3. Extraer filtros (ver tabla). Si faltan → usar defaults, NO preguntar.
4. Pre-computar expresiones helper (una vez, reusar en todos los comandos).

**Template mínimo** (crear si no existe):

```yaml
---
roadmap-root: # preguntar al usuario
done-statuses: ['Completed', 'Obsolete']
active-statuses: ['Pending', 'Specified', 'In Progress']
leaf-filter: 'isIndex == false'
story-close-verify: []
---
```

En todo este documento, `<roadmap-root>` se refiere al valor configurado.

### Configuración de Filtros

| Config key | Default | Placeholder |
|------------|---------|-------------|
| `done-statuses` | `['Completed', 'Obsolete']` | `<done-statuses>` |
| `active-statuses` | `['Pending', 'Specified', 'In Progress']` | `<active-statuses>` |
| `leaf-filter` | `'isIndex == false'` | `<leaf-filter>` |
| `story-close-verify` | `[]` | `<story-close-cmds>` |

Expresiones helper (pre-computar una vez, reusar en todos los comandos):

- `<where-not-done>`: `not (estado in <done-statuses>)`
- `<where-active>`: `estado in <active-statuses>`
- `<where-leaf>`: `<leaf-filter>`

---

## Dependencia: rootline CLI

**Requerida para materialización y queries** (`pending`, `loop`, `plan` post-aprobación). NO requerida para generar planes de descomposición.

Instalación:
```bash
curl -fsSL https://raw.githubusercontent.com/pablontiv/rootline/master/install.sh | bash
```

**Gate check**: Antes de ejecutar comandos `rootline` (crear archivos, queries, validación), verificar:
```bash
command -v rootline
```
Si no está disponible → informar al usuario:
> `rootline` no está instalado. Es requerido para materializar el roadmap.
> Instalar con: `curl -fsSL https://raw.githubusercontent.com/pablontiv/rootline/master/install.sh | bash`

**Alcance del gate**: Solo bloquea operaciones que ejecutan rootline (scaffolding, validate, query, tree, graph). La generación de planes de descomposición (modo autónomo, Paso 1-6) NO requiere rootline y puede proceder normalmente.

---

## Modo de Operación

Este skill es **plan-mode aware**. Cuando `defaultMode: "plan"` está activo:

### Fase 1: Planificación (automática en plan mode)
1. Parsear `$ARGUMENTS` para determinar subcomando
2. Leer el guide file correspondiente
3. Ejecutar discovery y generar contenido completo en el plan file
4. Llamar `ExitPlanMode` para aprobación

### Fase 2: Post-aprobación

Después de que el usuario aprueba el plan, informarle que puede ejecutar `/roadmap plan` para crear los archivos del roadmap.

---

## Routing por Subcomando

Una vez completado el bootstrap, determinar el modo según `$ARGUMENTS` y leer el archivo correspondiente:

| $ARGUMENTS | Archivo | Descripción |
|------------|---------|-------------|
| `pending` | [pending-subcommand.md](pending-subcommand.md) | Vista jerárquica de trabajo pendiente |
| `plan` | [plan-subcommand.md](plan-subcommand.md) | Materializar plan de conversación en archivos .md |
| *(sin argumentos)* | [decision-tree-subcommand.md](decision-tree-subcommand.md) | Árbol de decisión para priorizar ramas |
| `loop [--filter] [--max]` | [loop-subcommand.md](loop-subcommand.md) | Ejecutar tasks pendientes en loop con confirmación |
| *(texto libre)* | [autonomous-mode.md](autonomous-mode.md) | Descomposición autónoma de proyecto |

**Regla de dispatch**: Si `$ARGUMENTS` empieza con `pending`, `loop`, o `plan` → subcomando. Si está vacío → decision tree. Si es texto libre → modo autónomo.

---

## Lógica Común

### Auto-numbering

Para cada nivel, usar `rootline describe` con el campo `schema.id.next`:

```bash
# Requiere .stem con id: {type: sequence, prefix: X, digits: N} en cada nivel

# Epics: próximo EXX
rootline describe <roadmap-root>/ --field schema.id.next

# Features: próximo FXX dentro del Epic
rootline describe <roadmap-root>/EXX-name/ --field schema.id.next

# Stories: próximo SXXX dentro del Feature
rootline describe <roadmap-root>/.../FXX-name/ --field schema.id.next

# Tasks: próximo TXXX dentro de la Story
rootline describe <roadmap-root>/.../SXXX-name/ --field schema.id.next
```

El comando retorna el próximo identificador directamente (ej: `"T004"`).

### Verificación de Padre

SIEMPRE verificar que el directorio padre existe antes de crear un artefacto:
- Verificar con `rootline describe <roadmap-root>/<path>/` que el directorio destino existe

Si no existe → informar al usuario y sugerir crearlo primero.

### Cascading Links

Después de crear un artefacto, actualizar la tabla en el README padre:
- Task creado → agregar fila en la tabla "Tasks" del Story README (solo Task + Descripcion, sin Estado)
- Story creada → agregar fila en la sección "Stories" del Feature README (sin Estado)

**Nota**: Las tablas NO incluyen columna Estado. El estado se lee del YAML frontmatter de cada Task y se deriva para Stories/Features en `/roadmap`.

---

## Comandos Rootline de Referencia

| Comando | Cuándo usarlo en el skill |
|---------|--------------------------|
| `rootline init <path>` | Bootstrap: inferir .stem schema de archivos existentes. `--dry-run` para preview |
| `rootline validate <path>` | Después de crear/editar archivos .md — verificar contra .stem |
| `rootline fix <path>` | Cuando validate falla — corregir automáticamente |
| `rootline describe <dir> --field schema.id.next` | Auto-numbering: obtener próximo ID en cualquier nivel |
| `rootline new <path>` | Scaffolding: crear archivo con frontmatter correcto según .stem |
| `rootline query <path> --where "expr"` | Discovery: buscar records por frontmatter (estado, tipo, etc.) |
| `rootline tree <path> --where "expr" --output table\|json` | Vista jerárquica con conteos completed/total por nodo (reemplaza stats) |
| `rootline graph <path> --where "expr" --check` | Grafo de dependencias filtrado |

**Nota**: `rootline stats` es redundante — `rootline tree` ya incluye completed/total. NO usar stats por separado.

## Referencia

- Ver [framework-reference.md](framework-reference.md) para el documento completo del marco de trabajo
- Templates canónicos: primer Epic materializado en `<roadmap-root>/`
