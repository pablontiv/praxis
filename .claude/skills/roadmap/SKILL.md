---
name: roadmap
description: |
  AI-native planning framework for autonomous project decomposition.
  Accepts free text to decompose into epics, features, stories, and tasks.
  Subcommands: pending, loop, plan. Without arguments shows decision tree.
  Tasks are self-contained units with technical specs and binary acceptance criteria.
  This skill should be used when the user says "descomponer en features",
  "crear roadmap de X", "estructura de X",
  "planificar implementación de X", "qué sigue", "ver roadmap",
  "ver progreso", "qué falta", "tasks pendientes",
  "loop de tasks", "ejecutar pendientes", "implementar tasks",
  "roadmap loop", "ejecutar roadmap",
  "crear roadmap del plan", "materializar plan",
  or provides free text describing work to decompose.
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

## Dependencias

**Requerida: `rootline` CLI** — motor de base de datos sobre filesystem que este skill usa para validación, queries, auto-numbering, scaffolding y grafos de dependencia.

Instalación:
```bash
curl -fsSL https://raw.githubusercontent.com/pablontiv/rootline/master/install.sh | bash
```

**Gate check obligatorio**: Al inicio de CUALQUIER subcomando (`pending`, `loop`, `plan`, o sin argumentos), ejecutar:
```bash
command -v rootline
```
Si no está disponible → informar al usuario:
> `rootline` no está instalado. Es requerido por `/roadmap`.
> Instalar con: `curl -fsSL https://raw.githubusercontent.com/pablontiv/rootline/master/install.sh | bash`

**PARAR. No proceder manualmente ni intentar simular rootline con lecturas directas de archivos.**

---

## Configuración del Proyecto

El path raíz del roadmap se define en `.claude/roadmap.local.md` del proyecto:

```yaml
---
roadmap-root: docs/epics
---
```

Si `.claude/roadmap.local.md` no existe o no tiene `roadmap-root`, preguntar al usuario dónde vive el roadmap. **No asumir `docs/epics/`.**

En todo este documento, `<roadmap-root>` se refiere al valor configurado.

### Configuración de Filtros

Leer `.claude/roadmap.local.md` YAML frontmatter para estos campos adicionales.
Si un campo no existe, usar los defaults indicados:

| Config key | Default | Placeholder |
|------------|---------|-------------|
| `done-statuses` | `['Completed', 'Obsolete']` | `<done-statuses>` |
| `active-statuses` | `['Pending', 'Specified', 'In Progress']` | `<active-statuses>` |
| `container-types` | `['feature', 'historia']` | `<container-types>` |
| `story-close-verify` | `[]` | `<story-close-cmds>` |

Expresiones helper (pre-computar una vez, reusar en todos los comandos):

- `<where-not-done>`: `not (estado in <done-statuses>)`
- `<where-active>`: `estado in <active-statuses>`
- `<where-leaf>`: `tipo not in <container-types>`

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

## Modo Autónomo (default — sin subcomando explícito)

Cuando `$ARGUMENTS` NO empieza con `pending|loop|plan`, activar modo de evaluación autónoma.

### Paso 1: Análisis de Intención

Leer `$ARGUMENTS` y determinar:
- **Qué proyecto/componente** se menciona
- **Qué profundidad** se pide (solo epics? hasta tasks?)
- **Qué documentación existe** del proyecto (README, intent docs, research, código)

### Paso 2: Absorber Contexto del Proyecto

Leer TODA la documentación disponible del proyecto mencionado:
- READMEs, intent docs, research docs
- Código existente (para dimensionar scope real)
- Dependencias y relaciones

Esto es fundamental — sin entender el proyecto completo, la descomposición será artificial.

### Paso 2.5: Formalizar Contratos

**ANTES de descomponer**, para cada Epic identificado, definir:

1. **Postcondiciones** (2-3 constraints observables): Condiciones que serán verdad cuando el Epic se complete. Deben ser verificables con comandos o inspección directa.
2. **Invariantes**: Reglas que ningún Feature/Story/Task puede violar durante su ejecución. Ejemplo: *"Los workflows existentes siguen funcionando sin regresión"*.
3. **Out of scope**: Límites explícitos que previenen scope creep.

**Formato en plan file — Constraint Map:**

```markdown
## Constraint Map

| Postcondición | Features que la satisfacen | Descripción |
|---------------|---------------------------|-------------|
| P1: ...       | F01, F03                  | ...         |
| P2: ...       | F02                       | ...         |

## Invariantes

- INV1: ...
- INV2: ...
```

**Validación bidireccional** (obligatoria):
- Toda postcondición tiene al menos un Feature que la satisface
- Todo Feature satisface al menos una postcondición
- Si algún Feature no satisface ninguna postcondición → eliminar o reubicar
- Si alguna postcondición no tiene Feature → crear Feature faltante

### Paso 3: Aplicar Framework Autónomamente

**CRÍTICO**: El agente DEBE tomar decisiones usando los criterios del framework. NO preguntar al usuario cosas que el framework ya define.

Leer [framework-reference.md](framework-reference.md) y aplicar estos criterios de decisión:

| Nivel | Pregunta de corte | Criterio |
|-------|-------------------|----------|
| Epic | ¿Cuántos objetivos sistémicos distintos tiene? | Múltiples dominios → múltiples Epics |
| Feature | ¿Qué bloques pueden cerrarse independientemente? Satisface >= 1 postcondición del Epic | Milestone técnico real (anti-inflación: 3-5 Features, no 10) |
| Story | ¿Qué capacidades nuevas existen? | Antes/después claro, testeable, no ejecutable en 1 sesión |
| Task | ¿Qué puede hacer un agente en 1 sesión? | 6 condiciones de task-guide.md |

Apply the **scale criteria and decision tree** from [framework-reference.md](framework-reference.md) — targets: 3-5 Features/Epic, 1-4 Stories/Feature, 1-5 Tasks/Story. Split when exceeding limits, absorb when only 1 child exists.

### Paso 4: Generar Descomposición en Plan File

Presentar la estructura completa propuesta con árbol jerárquico:

```
E01: [Objetivo sistémico 1]
├── F01: [Milestone]
│   ├── S001: [Capacidad]
│   │   ├── T001: [tarea atómica] (tipo: X)
│   │   └── T002: [tarea atómica] (tipo: X)
│   └── S002: [Capacidad]
│       └── T001: [tarea atómica] (tipo: X)
└── F02: [Milestone]
    └── S001: [Capacidad]
        └── T001: [tarea atómica] (tipo: X)

E02: [Objetivo sistémico 2]
└── ...
```

Para cada Task incluir: nombre, tipo, descripción de 1 línea.

**Constraint Map** (obligatorio en plan file):

```markdown
## Constraint Map

| Postcondición Epic | Features | Descripción |
|----|----------|-------------|
| P1: ... | F01, F03 | ... |
| P2: ... | F02 | ... |
```

### Paso 4.5: Validación de Completitud

**OBLIGATORIO** antes de presentar. Verificar:

1. **Traceability ascendente**: Cada Task → contribuye a su Story "Después"
   → cada Story → contribuye a su Feature Objetivo
   → cada Feature → avanza la Intención del Epic.
   Si un Task no traza a ningún objetivo superior → eliminar o reubicar.

2. **Completeness por contratos**: Cada postcondición del Epic tiene >= 1 Feature que la satisface. Cada milestone de Feature tiene >= 1 Story que lo cubre. Cada criterio de Story tiene >= 1 Task AC que lo implementa. Si algún nivel no tiene cobertura → crear artefacto faltante.

3. **No-overlap**: ¿Dos Features o Stories cubren lo mismo? → fusionar.

4. **Dependency chain**: ¿Features tienen dependencias entre sí?
   → Documentar orden de ejecución en el plan.

5. **Sanity check numérico**: Verificar contra criterios de escala (Paso 3).

6. **Invariant propagation check**: Invariantes del Epic aparecen en sus Features (heredados). Invariantes de Features fluyen a sus Stories. Tasks los preservan via sección "Preserva". Si un invariante no se propaga → agregarlo al nivel faltante.

### Paso 5: Presentar para Aprobación (NO para definición)

El plan se presenta como **propuesta fundamentada**, no como pregunta abierta.
- El agente YA tomó las decisiones de granularidad
- El usuario aprueba, ajusta, o rechaza — pero no define desde cero
- Si hay ambigüedad REAL (no resuelta por el framework), ENTONCES preguntar

### Anti-patrones

- ❌ "¿Debería haber 1 Epic o varios?" — El framework ya define cuándo
- ❌ "¿Qué opina de esta estructura?" — Presentar la estructura, no pedir que la diseñe
- ❌ Proponer 1 Epic para un producto completo — Escala mal
- ❌ Preguntar por cada nivel — Generar TODO y presentar junto

### Paso 6: Informar siguiente paso

Después de la aprobación, informar al usuario que puede ejecutar `/roadmap plan` para materializar la estructura como archivos .md.

---

## Subcomandos

### `/roadmap pending`

Vista jerárquica filtrada: solo Features con trabajo pendiente.

**Procedimiento**:
1. Ejecutar `rootline tree <roadmap-root>/ --where '<where-leaf> && <where-not-done>' --output table`
2. Ejecutar `rootline stats <roadmap-root>/ --where '<where-leaf> && <where-not-done>' --output table`

Presenta ambos outputs al usuario.

---

### `/roadmap plan`

Tomar el plan de la conversación actual y descomponerlo en estructura de roadmap.

**Cuándo usar**: Después de que una sesión produce un plan técnico (investigación, análisis,
fix propuesto, etc.) y se quiere estructurar como roadmap.

**Fuente del plan** (orden de prioridad):
1. Contexto de la conversación actual (preferido)
2. Fallback: plan file de `~/.claude/plans/${CLAUDE_SESSION_ID}.md`
   (plan files son globales — usar `${CLAUDE_SESSION_ID}` para garantizar que sea de esta sesión)

**Procedimiento**:

#### Fase 1: Descomposición

1. Identificar el plan más reciente:
   a. Buscar en el contexto de conversación actual (plan técnico, análisis, propuesta, etc.)
   b. Si la conversación fue compactada o no tiene plan visible → leer plan file de
      `~/.claude/plans/${CLAUDE_SESSION_ID}.md`
   c. Si no hay plan en ninguna fuente → informar: "No hay plan en esta conversación.
      Primero investigar/planificar, luego ejecutar `/roadmap plan`." → STOP
3. Absorber contexto: leer documentación existente del área afectada en `<roadmap-root>/`
4. Aplicar framework de descomposición (mismos criterios que Modo Autónomo):
   - Leer [framework-reference.md](framework-reference.md)
   - Criterios de escala: 3-5 Features/Epic, 1-4 Stories/Feature, 1-5 Tasks/Story
   - Constraint Map (postcondiciones + invariantes)
   - Validación de completitud (Paso 4.5 del Modo Autónomo)
5. **OBLIGATORIO**: Descomposición DEBE llegar hasta nivel Task para TODOS los Stories.
   Cada Task con: nombre, tipo, descripción de 1 línea.

#### Fase 2: Presentación para aprobación

6. Presentar árbol jerárquico completo + Constraint Map
7. Pedir aprobación con `AskUserQuestion` (NO usar `ExitPlanMode` — ese es para plan mode
   del sistema, no para aprobaciones internas de un skill)
8. **STOP y esperar aprobación. NO crear archivos sin aprobación.**

#### Fase 3: Materialización (post-aprobación)

9. Para cada artefacto, crear archivos .md usando los templates de:
   - [epic-guide.md](epic-guide.md) para READMEs de Epic y Feature
   - [story-guide.md](story-guide.md) para READMEs de Story
   - [task-guide.md](task-guide.md) para archivos de Task
10. Después de cada Write, ejecutar `rootline validate <path>`
11. Si falla, `rootline fix <path>` como fallback
12. Actualizar tablas en READMEs padre (cascading links)
13. **Validación batch final**: Ejecutar `rootline validate --all <roadmap-root>/`
   - Si hay errores → `rootline fix --all <roadmap-root>/`
   - Reportar resultado final al usuario
14. **Commit+Push** archivos de planificación creados:
   - `git add` todos los archivos .md creados (específicos, no `git add .`)
   - `git commit` con mensaje: `chore(roadmap): create {descripción breve} planning docs`
   - `git push`

**STOP OBLIGATORIO**: Después de commit+push, DETENERSE COMPLETAMENTE.
Informar: "Archivos de planificación creados. Ejecutar `/roadmap loop` cuando esté listo
para implementar."
NO continuar. NO invocar `/roadmap loop`. NO leer tasks para implementar.

---

### `/roadmap` (sin argumentos)

Generar **árbol de decisión** que muestre ramas ejecutables, cadenas de dependencia, y bloqueos para decidir qué loop implementar.

**Procedimiento**:

#### Paso 1: Recopilar datos (3 comandos en paralelo)

Ejecutar en paralelo:
1. `rootline tree <roadmap-root>/ --where "<where-not-done>" --output json` — árbol jerárquico con paths, estados y conteos completed/total (~2 KB, reemplaza stats + query)
2. `rootline graph <roadmap-root>/ --where "<where-not-done>" --output json` — grafo de dependencias entre pendientes (~3 KB)
3. `git log -5 --format='%h %s'` — últimos commits para proximidad

**IMPORTANTE**: Después de Paso 1, NO ejecutar más comandos bash. Los Pasos 2-5 procesan los JSONs obtenidos.

#### Paso 2: Agrupar en ramas (procesamiento de datos, SIN comandos adicionales)

Usar los outputs JSON de Paso 1 para construir las ramas:

1. **Feature path**: Extraer de `root.children[].children[].path` del tree JSON (cmd 1) — la jerarquía ya agrupa por Epic/Feature/Story/Task
2. **Dependencias intra-story**: Extraer de `edges[]` del graph JSON (cmd 2) — cada edge tiene `source`, `target`, y `type: "blocks"`
3. **Conteos**: Cada nodo del tree tiene `completed` y `total` — usar para progreso por rama
4. **Estado**: Cada hoja del tree tiene `estado` — usar para clasificar tasks

NO ejecutar comandos adicionales. Todo se extrae de los 3 outputs del Paso 1.

#### Paso 3: Clasificar ramas (procesamiento de datos, SIN comandos adicionales)

Usando `estado` de cada hoja del tree JSON (cmd 1):

- **Ejecutables**: todas las tasks tienen estado en `<active-statuses>`, sin dependencias insatisfechas (verificar contra `edges[]` del graph, cmd 2)
- **Bloqueadas**: al menos una task tiene `estado: Blocked` o dependencia cross-feature con estado no en `<done-statuses>`

Dentro de ejecutables, identificar **quick wins** (ramas con 1 solo task).

#### Anti-patrones de eficiencia

- ❌ Loops `for f in ...; do grep/head; done` — usar JSON de rootline
- ❌ Queries adicionales post-Paso 1 — toda la data necesaria está en los 3 outputs
- ❌ Usar `rootline query` para listados — `rootline tree` da estructura + estados + conteos en un solo comando
- ❌ Usar `rootline stats` por separado — tree ya incluye completed/total por nodo
- ❌ Buscar `[[blocks:]]` con grep — rootline graph ya parsea wiki-links
- ✅ Máximo 3 comandos (Paso 1), todos en paralelo, ~5.5 KB total, el resto es procesamiento de datos

#### Paso 4: Renderizar árbol de decisión

Formato de salida:

```
ROADMAP DECISION TREE — N/M completados (X%)
══════════════════════════════════════════════

¿Qué objetivo priorizar?
│
├─► RAMA: Feature Name (Epic) — N tasks, tipo dominante
│   │
│   T001: nombre                    [estado, tipo]
│   │   ↓ desbloquea
│   T002: nombre                    [estado, tipo]
│       ↓ CIERRA [qué capacidad]
│
├─► RAMA: ...
│
└─► QUICK WIN — task aislado
    T001: nombre                    [estado, tipo]

BLOQUEADAS SIN CAMINO DIRECTO
│
├── TXXX: nombre    [blocker: descripción]
└── TXXX: nombre    [blocker: descripción]
```

Reglas de renderizado:
- Usar `├─►` para ramas ejecutables, `├──` para bloqueadas
- `↓ desbloquea` entre tasks con dependencia `[[blocks:]]`
- `↓ CIERRA [capacidad]` en el último task de la rama (extraer del nombre del nodo Feature en el tree JSON)
- Marcar tasks cuya dependencia ya está en `<done-statuses>` pero siguen en Blocked como `[stale?]`
- Ordenar ramas ejecutables por proximidad al último commit (extraer de `git log` del Paso 1)

#### Paso 5: Renderizar criterios de decisión

Al final del árbol, agregar flowchart de decisión:

```
CRITERIOS DE DECISION
│
├─ ¿Hay rama en progreso (último commit)?
│  ├─ SI → Cerrar esa rama primero
│  └─ NO ↓
├─ ¿Hay deuda técnica que bloquea futuro trabajo?
│  ├─ SI → Rama que desbloquea más dependientes
│  └─ NO ↓
├─ ¿Quiero progreso rápido?
│  ├─ SI → Quick win o rama más corta
│  └─ NO → Rama con mayor impacto arquitectural
```

Adaptar el flowchart al estado real (referenciar ramas concretas en cada hoja).

---

### `/roadmap loop [--filter PATTERN] [--max N]`

Ejecutar Tasks pendientes en loop con confirmación entre cada uno.

**Opciones**:
- `--filter PATTERN`: Filtrar por path (ej: `E02/F04`, `E01`)
- `--max N`: Limitar a N tasks
- `--checkpoint-interval N`: Intervalo de tasks entre checkpoints de calidad (default 5)
- `--skip-reviews`: Desactivar quality gates (security review y checkpoint review)

**Procedimiento**:

#### Fase 1: Discovery

1. Ejecutar `rootline graph --check <roadmap-root>/` para validar dependencias antes de empezar
   - Si hay ciclos → reportar y **parar** (dependencias circulares impiden ejecución)
   - Si hay broken links → reportar como warning (pueden ser tasks aún no creados)
2. Ejecutar `rootline query <roadmap-root>/ --where "<where-leaf>" --where "<where-active>" --output table` para obtener tasks pendientes
3. Si `--filter PATTERN` proporcionado, filtrar resultados por Epic/Feature path match
4. Si `--max N`, tomar solo los primeros N tasks
5. Mostrar tabla de tasks encontradas al usuario

#### Fase 2: TodoList Setup

Para cada task encontrada, crear entrada con `TaskCreate`:
- **subject**: `TXXX: título`
- **description**: `Path: <filepath> | Tipo: <tipo>`
- **activeForm**: `Implementando TXXX`

Mostrar TodoList con `TaskList`.

#### Fase 3: Loop de Ejecución

**Variables de estado del loop:**
- `checkpoint_commit`: SHA del último checkpoint (inicializar con HEAD al inicio)
- `checkpoint_task_count`: Contador de tasks desde último checkpoint (inicializar en 0)
- `current_story_path`: Path de la Story actual (para detectar cambio de contexto)
- `checkpoint_interval`: Intervalo entre checkpoints (default 5, configurable con --checkpoint-interval)

Para cada task en orden:

1. **Verificar dependencias**: Leer el archivo .md del task y buscar `[[blocks:TXXX-name]]` en el body.
   Para cada dependencia encontrada:
   - Buscar el task referenciado y verificar que su frontmatter tiene `estado` con valor en `<done-statuses>`
   - Si alguna dependencia no está en `<done-statuses>` → **skip** con mensaje: `⏭️ Bloqueado por: TXXX (estado: <valor>)`
   - Tasks bloqueados se reintentarán al final de la cola

2. **Marcar inicio**: `TaskUpdate` → status: `in_progress`

3. **Leer Task**: `Read` del archivo .md completo para entender qué pide

4. **Implementar**:
   - Si el Task tiene `tipo:` en frontmatter que corresponde a un skill
     conocido del proyecto, invocarlo via `Skill` tool
   - Si no tiene skill asociado, implementar directamente siguiendo
     las instrucciones del Task
   - Consultar `.claude/roadmap.local.md` (si existe) para templates de
     especificación técnica del proyecto, o [type-specs.md](type-specs.md) como fallback

5. **Verificar ACs**:
   - Leer sección "Criterios de Aceptación" del Task .md
   - Ejecutar CADA verificación documentada (comandos, checks, observables)
   - Reportar resultado por AC: ✅ PASS / ❌ FAIL
   - Si algún AC falla → reportar y **parar** (bug encontrado)
   - Leer sección "Preserva" del Task .md (si existe)
   - Para cada invariante listado en Preserva: ejecutar su comando/procedimiento de verificación
   - Reportar resultado: INV1 HOLDS / INV2 VIOLATED
   - Si algún invariante se viola → **parar** (igual que AC fail)

6. **Verificación de cierre de Story** (si es el último task de la Story):
   - Determinar si es el último task: no quedan tasks pendientes en la misma Story (todas las demás están en `<done-statuses>`)
   - Leer criterios semánticos (sección "Criterios de Aceptación" o "Después") del README.md de la Story padre
   - Ejecutar `<story-close-cmds>` de `roadmap.local.md` (si existen)
   - Reportar resultado por comando: ✅ PASS / ⚠️ FAIL
   - **Warning informativo, no bloquea** el loop — el usuario decide si actuar

7. **Security Review** (selectivo, post-ACs, pre-commit):
   - Aplica si: archivos modificados incluyen patterns sensibles (`**/secret*`, `**/*credentials*`, `**/.env*`, `**/auth*`, `**/crypto*`) O si el tipo de task lo requiere
   - Si aplica: ejecutar `/security-review` sobre archivos modificados
   - Si findings HIGH → **parar** (vulnerabilidad pre-push). Reportar findings y detener loop
   - Si findings MEDIUM → warning informativo, continuar
   - Si nada o no aplica → continuar silenciosamente

8. **Commit+Push** (centralizado, NO delegado a skills hijos):
   - Identificar archivos modificados/creados por la implementación
   - `git add` archivos relevantes (específicos, no `git add .`)
   - `git commit` con mensaje en formato **conventional commits**: `type(scope): description`
     - Elegir `type` según el contenido del task: `feat` (nueva funcionalidad), `fix` (corrección), `test` (tests), `docs` (documentación), `refactor` (reestructuración), `ci` (CI/CD), `chore` (mantenimiento), `perf` (rendimiento), `style` (formato)
     - El hook `.githooks/commit-msg` rechazará mensajes que no sigan el formato
   - `git push`

9. **Marcar completado**: `TaskUpdate` → status: `completed`

10. **Resumen de iteración**:
   ```
   📊 ITERACIÓN N/TOTAL
   ├─ Task: TXXX - título
   ├─ Resultado: ✅/❌
   ├─ ACs: N/M passed
   ├─ Commit: hash
   └─ Siguiente: TXXX+1 - título
   ```

11. **Checkpoint Detection** (post-resumen, pre-confirmación):
   - Incrementar `checkpoint_task_count`
   - Triggers (OR — cualquiera activa el checkpoint):
     a) **Story context change**: siguiente task pertenece a otra Story (`current_story_path` diferente)
     b) **Safety net**: `checkpoint_task_count >= checkpoint_interval` (default 5)
     c) **Loop interrumpido**: usuario elige "Parar" en la confirmación
   - Al activar checkpoint:
     1. Calcular diff acumulado: `git diff <checkpoint_commit>..HEAD`
     2. Ejecutar `/review` sobre el diff acumulado
     3. Reportar findings (informativos, **no bloquean** el loop)
     4. Registrar nuevo checkpoint: `checkpoint_commit = HEAD`, `checkpoint_task_count = 0`

12. **Confirmar**: `AskUserQuestion` con opciones:
   - Sí, continuar (Recommended)
   - Saltar siguiente y continuar
   - Parar aquí

13. **Reintentar bloqueados**: Al terminar la cola, si quedan tasks que fueron skipped por dependencias bloqueadas y ahora sus dependencias están Completadas → reintentar. Si ningún task progresó en la pasada → parar (deadlock de dependencias).

#### Fase 4: Resumen Final

Al terminar todas las tasks o al parar:

```
📊 RESUMEN LOOP
├─ Tasks completadas: N/TOTAL
├─ Tasks saltadas: M
├─ ACs: total passed / total
├─ Security reviews: N ejecutados, M findings (H: X, M: Y)
├─ Quality checkpoints: N ejecutados, M findings
├─ Commits: lista de hashes
└─ Tasks restantes: lista (si las hay)
```

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
| `rootline validate <path>` | Después de crear/editar archivos .md — verificar contra .stem |
| `rootline fix <path>` | Cuando validate falla — corregir automáticamente |
| `rootline describe <dir> --field schema.id.next` | Auto-numbering: obtener próximo ID en cualquier nivel |
| `rootline new <path>` | Scaffolding: crear archivo con frontmatter correcto según .stem |
| `rootline query <path> --where "expr"` | Discovery: buscar records por frontmatter (estado, tipo, etc.) |
| `rootline tree <path> --where "expr" --output table` | Vista jerárquica filtrada: `/roadmap pending` |
| `rootline stats <path> --where "expr" --output table` | Resumen estadístico filtrado por expresión |
| `rootline graph <path> --where "expr" --check` | Grafo de dependencias filtrado |

## Referencia

- Ver [framework-reference.md](framework-reference.md) para el documento completo del marco de trabajo
- Templates canónicos: primer Epic materializado en `<roadmap-root>/`
