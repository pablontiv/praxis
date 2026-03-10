---
name: discover
description: |
  Usar para exploración abierta cuando el usuario quiere investigar, aprender,
  o mapear un dominio que no entiende completamente todavía. Gestiona líneas
  de investigación con ciclos Plan-Act-Observe-Reflect, grounded theory, y
  conexiones de conocimiento entre temas. Usar este skill siempre que el
  usuario exprese curiosidad sobre un tema, quiera explorar o investigar algo,
  haga preguntas abiertas y amplias, mencione iniciar una nueva investigación,
  o quiera documentar observaciones y patrones — incluso si no dice "discover"
  ni "nueva línea", incluso si la pregunta parece simple de responder
  directamente, e incluso si solo dice "quiero investigar sobre X" o "I want
  to look into Y."
  (No para: evaluar claims específicos = hypothesize, planificar tareas = roadmap.)
user-invocable: true
argument-hint: "<subcommand> [args] | @file — subcommands: init, new-line, cycle, reflect, theory, status, update-map, interlink, review-patterns, research, resume"
---

# /discover — Structured R&D Framework

## Routing

Parse `$ARGUMENTS` to determine subcommand. First token = subcommand, rest = args.

| Input | Subcommand | Args |
|-------|-----------|------|
| (empty) | → **status** | — |
| `init my-project` | → **init** | `my-project` |
| `new-line topic-name` | → **new-line** | `topic-name` |
| `cycle line-name` | → **cycle** | `line-name` |
| `reflect line-name` | → **reflect** | `line-name` |
| `theory theory-name` | → **theory** | `theory-name` |
| `status` | → **status** | — |
| `update-map` | → **update-map** | — |
| `interlink` | → **interlink** | — |
| `review-patterns` | → **review-patterns** | — |
| `research topic [--deep]` | → **research** | `topic [--deep]` |
| `resume line-name` | → **resume** | `line-name` |
| `@path/to/file` | → **intake** | file path (without `@`) |

**`@` detection**: If `$ARGUMENTS` starts with `@`, strip the `@` prefix and route to **intake** with the remaining path as the file argument.

**Fork detector**: Not a subcommand — it's a behavior. Claude should proactively detect forks during any subcommand (see "Fork Detection" section at the end).

---

## Dependencia: rootline CLI

**Requerida para queries, validacion y grafos**. NO requerida para creating/editing markdown files directly.

Instalacion:
```bash
curl -fsSL https://raw.githubusercontent.com/pablontiv/rootline/master/install.sh | bash
```

**Gate check**: Antes de ejecutar comandos `rootline`, verificar:
```bash
command -v rootline
```
Si no esta disponible -> informar al usuario:
> `rootline` no esta instalado. Es requerido para queries y validacion en discover.
> Instalar con: `curl -fsSL https://raw.githubusercontent.com/pablontiv/rootline/master/install.sh | bash`

**Alcance del gate**: Solo bloquea operaciones que ejecutan rootline (validate, query, tree, graph). La creacion y edicion directa de archivos .md (new-line, cycle, theory) puede proceder sin rootline — solo las validaciones post-creacion y las queries requieren rootline.

---

## Rootline Integration

Rootline is the data layer for discover. It reads YAML frontmatter from .md files, validates against `.stem` schemas, and supports structured queries.

### Key concepts

1. **`.stem` schemas** exist in each discover directory: `lines/.stem`, `closed/.stem`, `paused/.stem`, `theories/.stem`, `backlog/.stem`, `intake/.stem`. These define required frontmatter fields per directory.

2. **`isIndex` field**: Rootline's built-in field distinguishes index records (README.md) from content records. Use `isIndex == false` to query only content documents.

3. **YAML frontmatter**: All documents have frontmatter with at minimum a `tipo` field:
   - `tipo: question` — QUESTION.md files in lines/paused/
   - `tipo: field-log` — FIELD-LOG.md files
   - `tipo: closure` — CLOSURE.md files in closed/
   - `tipo: theory` — theory documents in theories/
   - `tipo: backlog-question` — backlog entries
   - Other fields: `estado`, `fecha_inicio`, `linea`, `ciclos_registrados`, `confianza`, etc.

4. **Use rootline commands instead of manual grep/file scanning**:
   - `rootline query <path> --where "expr" --output table` — search records by frontmatter
   - `rootline tree <path> --output table|json` — hierarchical view with counts
   - `rootline validate <path>` — check document against .stem schema
   - `rootline validate --all <path>` — validate all documents in a directory
   - `rootline graph <path> --format mermaid` — connection/link graph
   - `rootline graph <path> --check` — validate wikilinks and detect broken/orphaned links

5. **current-state.md and connections.md are kept** — they serve as rules files loaded into Claude's context. Rootline queries supplement but don't replace context injection.

---

## Subcommand: init

Initialize an R&D project in the current directory. Creates directory structure (intake/, backlog/, lines/, theories/, paused/, closed/, shared/), copies templates, generates MAP.md and state files.

**Args**: `[project-name]` — optional.

See [ref-init.md](ref-init.md) for the full procedure.

---

## Subcommand: new-line

Create a new line of inquiry with anti-presupposition process.

**Args**: `[name]` — kebab-case name for the line.

### Process

1. **Validate**:
   - No line with this name in `lines/`
   - Count active lines (max 2-3). If 3+, ask which to pause first.
   - Name must be kebab-case.

1.5. **Prior work check** (si `command -v backscroll >/dev/null 2>&1`):
   ```bash
   backscroll search "[line-topic]" --robot --max-tokens 2000
   ```
   Si hay resultados, mostrar al usuario: sesiones previas discutieron este tema. Preguntar: referenciar esos hallazgos o empezar desde cero?

2. **Create structure**: `lines/[name]/` with:
   - `QUESTION.md` — from `shared/templates/QUESTION.md`
   - `FIELD-LOG.md` — from `shared/templates/FIELD-LOG.md`

3. **Guide QUESTION.md** completion:
   - Central question (open form)
   - Why does this matter?
   - Type of understanding: Describe / Understand / Explore / Build
   - Initial context
   - Status: "In exploration"

4. **Anti-presupposition process**: Detect presuppositions, reformulate observationally, generate alternatives.
   See [anti-presupposition.md](anti-presupposition.md) — "In new-line" section (full process).
   Document results in QUESTION.md: presuppositions, alternatives, reformulated question.

5. **Validate with rootline** (if available):
   ```bash
   rootline validate lines/[name]/QUESTION.md lines/[name]/FIELD-LOG.md
   ```

6. **Update system**: Update `.claude/rules/current-state.md`. MAP.md update deferred to `/discover update-map`.

---

## Subcommand: cycle

Document a Plan-Act-Observe-Reflect cycle for a line.

**Args**: `[line-name]` — name of line in `lines/`.

### Process

1. **Prepare**: Open `lines/[name]/FIELD-LOG.md`, determine cycle number, create section `## Cycle N — [today's date]`.

2. **PLAN phase**: Ask what they'll do and what they expect. Document in `### Cycle intention`.

3. **Presupposition validation**: Check if QUESTION.md has anti-presupposition sections and review/update.
   See [anti-presupposition.md](anti-presupposition.md) — "In cycle" section.

4. **ACT phase**: Document concrete actions, references, code, decisions in `### What I did`.
   - Si `command -v backscroll >/dev/null 2>&1`, buscar observaciones previas: `backscroll search "TOPIC" --robot --max-tokens 2000` para evitar re-recorrer terreno cubierto en sesiones pasadas.

5. **OBSERVE phase**: Ask what happened, what surprised, what wasn't understood. Document in `### Observations`.

6. **REFLECT phase**: Ask what was learned, what it means for the central question, what patterns emerge. Document in `### Reflection`.

7. **Closure**: Document emerging questions in `### Emerging questions`. Ask: next cycle, reflection point, or pause? Document in `### Next cycle`.

8. **Update system**: Update `.claude/rules/current-state.md` and `connections.md` if connections emerge.

---

## Subcommand: reflect

Structured reflection to evaluate continue/pause/close a line.

**Args**: `[line-name]` — if omitted, check active lines and ask.

### Process

1. **Read state**: Open FIELD-LOG.md, count cycles, review latest reflections.

2. **Guide reflection**:
   - **Saturation**: Did last cycles contribute new insights?
   - **Question**: Is the original question still the same?
   - **Emergent Theory**: Can you articulate a pattern/principle?
   - **Energy**: Does this give energy or drain it?

3. **Present decisions**:

   | Decision | When | Action |
   |----------|------|--------|
   | CONTINUE | More to explore | Next cycle |
   | PAUSE | Low energy or urgent | Move to `paused/` |
   | CLOSE | Saturation reached | Theory review → document → move to `closed/` |
   | FORK | New question emerged | Run `/discover new-line` |

4. **Execute**:
   - CONTINUE → ask intention for next cycle
   - PAUSE → move folder to `paused/`, update state. To resume later: `/discover resume [name]`
   - CLOSE → **automatically run review-patterns first**, then create CLOSURE.md from [template](templates/CLOSURE.md), move to `closed/`, update state. Then validate with rootline (if available):
     ```bash
     rootline validate closed/[name]/CLOSURE.md
     rootline validate --all closed/[name]/
     ```
     Check if any `intake/` files referenced by this line should graduate to `/hypothesize` or `/roadmap` — suggest next step for each.
   - FORK → run new-line, document connection

**Validations**: Line must exist. Don't allow closing without at least 2 cycles (unless explicit).

---

## Subcommand: theory

Document an emergent theory in `theories/`.

**Args**: `[theory-name]` — kebab-case.

### Process

1. **Create** `theories/[name].md` from [THEORY.md template](templates/THEORY.md).

2. **Guide documentation**:
   - **Origin**: Which line(s)? Which cycle(s)?
   - **Pattern**: 2-3 sentence description + essence phrase (max 10 words)
   - **Evidence**: Specific observations, frequency
   - **Conditions**: When it applies, when it does NOT
   - **Connections**: Other theories, external knowledge
   - **Artifacts**: Code, prototypes, tools

3. **Confidence level**: Emergent / Developing / Consolidated
   - Developing requires ≥ 2 evidence pieces
   - Consolidated requires ≥ 3 tested contexts

4. **Update system**: Update `connections.md`, link from originating line(s).

---

## Subcommand: status

Show system state. Read-only.

### Process

1. **Read state**: `.claude/rules/current-state.md` for context injection, then query rootline for live data:
   ```bash
   # Active lines
   rootline query lines/ --where 'tipo == "question"' --output table
   # Paused lines
   rootline query paused/ --where 'tipo == "question"' --output table
   # Closed lines
   rootline query closed/ --where 'tipo == "closure"' --output table
   # Theories
   rootline query theories/ --output table
   # Backlog count
   rootline query backlog/ --count
   # Full tree view
   rootline tree lines/ --output table
   ```
   If rootline unavailable, fall back to reading `.claude/rules/current-state.md` + `MAP.md` manually.

2. **Display**:
   ```
   ## Discover — System Status

   ### Active Lines
   [List with name and current cycle]

   ### Backlog
   [Count]

   ### Theories
   [Count]

   ### Workflow
   /discover status → /discover new-line → [inquire] → /discover cycle → /discover reflect
                                                                          │
                                       ┌──────────────────────────────────┼────────────────────┐
                                       │                                  │                    │
                                   CONTINUE                            PAUSE                 CLOSE
                                (back to inquire)                                  (/discover theory if pattern)

   ### Last Session
   [Summary]
   ```

3. **Additional**: Report paused lines, emergent patterns, inconsistencies (>3 active lines).

**Sync rule**: Only `/discover update-map` touches MAP.md. Other subcommands update `current-state.md` and `connections.md`.

---

## Subcommand: update-map

Scan entire system and regenerate MAP.md.

### Process

1. **Scan via rootline** (if available):
   ```bash
   # Generate full system view (content docs only, excludes README.md index files)
   rootline tree . --where 'isIndex == false' --output table
   # Check connections via graph
   rootline graph . --format mermaid
   # Validate all schemas across the project
   rootline validate --all
   ```
   If rootline unavailable, fall back to manually scanning: intake/ (reference docs), backlog/ (questions), lines/ (active + cycles), theories/ (confidence), paused/ (reasons), closed/ (dates + theories), shared/ (artifacts).

2. **Connections**: Use `rootline graph . --check` to detect wikilinks and broken references. Supplement with `connections.md` review.

3. **Regenerate MAP.md** with data from rootline queries.

**When to run**: After new-line, cycle, reflect (PAUSE/CLOSE), theory, or at start of long sessions.

**Intake audit**: During update-map, check for `intake/` files not referenced by any active line or backlog item. Report orphaned files and suggest: graduate to `/hypothesize` or `/roadmap`, attach to an existing line, or archive.

---

## Subcommand: interlink

Scan system and add wikilinks `[[name]]` where mentions are detected.

### Process

1. **Check existing links via rootline** (if available):
   ```bash
   rootline graph . --check
   ```

2. **Build entity list**: folder names from lines/, theories/, backlog/.

3. **Search**: For each .md file, find mentions NOT already inside `[[...]]`. Exclude code blocks, URLs, file paths.

4. **Propose changes**: Show summary with file, line, and proposed wikilink. Ask: apply all / review one by one / cancel.

5. **Apply**: Edit files, report changes, suggest `/discover update-map`.

6. **Orphan concepts** (optional): If frequent mentions of concepts without files, ask about creating stubs.

**Don't modify**: skill directories, templates.

---

## Subcommand: review-patterns

Evaluate maturity of emergent patterns.

### Process

1. **Extract patterns**: Query rootline for theories by confidence level (if available), then supplement with `connections.md` "Emergent Patterns" section:
   ```bash
   rootline query theories/ --where 'confianza == "emergent"' --output table
   rootline query theories/ --where 'confianza == "developing"' --output table
   rootline query theories/ --where 'confianza == "consolidated"' --output table
   ```
   If rootline unavailable, extract patterns from `connections.md` manually.

2. **Quantitative score**:
   | Criterion | Points |
   |-----------|--------|
   | Mention in different cycle | +1 |
   | Mention in different line | +2 |
   | Appears in CLOSURE.md | +3 |

3. **Qualitative maturity** (for score ≥ 5):
   | Criterion | Question |
   |-----------|----------|
   | Clear conditions | When does it apply / NOT apply? |
   | Counter-examples | Cases where it failed? |
   | External connection | Papers, books, frameworks? |
   | Explanatory mechanism | WHY it works, not just THAT it works? |
   | Prediction | Can it anticipate new results? |

   Classification: 4-5 criteria = Theory, 2-3 = Principle, 0-1 = Observation.

4. **Show results** and ask: formalize with `/discover theory`, continue, or add to backlog.

**Key principle**: Many mentions ≠ mature theory. High score is a proxy, not proof.

---

## Subcommand: resume

Resume a paused line of inquiry.

**Args**: `[line-name]` — name of line in `paused/`.

### Process

1. **Validate**: Check that `paused/[name]/` exists. If not, list available paused lines.

2. **Move**: Move `paused/[name]/` back to `lines/[name]/`.

3. **Check capacity**: If already 3 active lines, warn and ask which to pause first.

4. **Review state**: Read QUESTION.md and latest cycle in FIELD-LOG.md. Present a summary so the user can re-orient.

4.5. **Session history** (si `command -v backscroll >/dev/null 2>&1`):
   `backscroll search "[line-name]" --robot --max-tokens 2000`
   Mostrar hallazgos relevantes junto con el review de QUESTION.md/FIELD-LOG.md.

5. **Update system**: Update `.claude/rules/current-state.md` — move line from "Paused" to "Active".

6. **Next step**: Ask: "Ready for a new cycle? (`/discover cycle [name]`)" or "Want to review the question first?"

---

## Subcommand: research

Research a topic using web search and synthesize.

**Args**: `[topic] [--deep]` — `--deep` = 8-10 sources, default = 3-5.

### Process

1. **Presupposition validation**: Analyze topic for presuppositions, propose broader reformulation, generate alternative queries.
   See [anti-presupposition.md](anti-presupposition.md) — "In research" section.

2. **Execute search**: WebSearch for each query. Filter by relevance and authority.

3. **Synthesize**:
   ```markdown
   ## Research: [topic]
   **Sources consulted:** [N]
   ### Definition/Concept
   ### Key Points
   ### Applications/Examples
   ### Limitations/Criticisms
   ### Connection with central question
   ### Topic presuppositions
   ### Sources
   ```

4. **Document**: If active line exists, add "### Lateral research" in FIELD-LOG.md.

5. **Next step**: "Does this change your understanding?" / "Explore further?" / "Continue with cycle?"

**When Claude can offer**: User mentions not understanding something, conceptual gap blocking progress, during reflect when saturated.

---

## Subcommand: intake

Analyze an external file (`@path/to/file`) and classify it into the appropriate flow entry point (discover line, backlog, hypothesize, roadmap). Extracts 7 signals, runs anti-presupposition scan, suggests adaptations.

**Trigger**: `$ARGUMENTS` starts with `@`. Strip the `@` to get the file path.

See [ref-intake.md](ref-intake.md) for the full procedure, output format, and edge cases.

---

## Fork Detection (proactive behavior)

Not a subcommand — Claude applies this during any interaction.

### When to detect

- Responding about a topic NOT the central question of the active line
- A concept/tool/question emerged that deserves its own exploration
- User expressed interest in something tangential
- Research revealed something broadening the scope

### Diagnostic question

> "Is this new element part of the essential experience of the phenomenon we're exploring, or is it external context or theoretical curiosity?"

| Category | Action |
|----------|--------|
| Essential experience | Incorporate without asking |
| External context | Mention, maybe to backlog |
| Theoretical curiosity | To backlog or discard |

### If significant divergence

Present:
```
**Possible fork detected**
Current topic: [describe]
Active line: [[line-name]] — [central question]
My assessment: [category]
Options:
1. Continue here — part of current exploration
2. New line — deserves its own inquiry (/discover new-line [name])
3. To backlog — interesting but not urgent
```

### Glaser Test (if in doubt)

| Criterion | Question |
|-----------|----------|
| Fit | Connects with what we know about this line? |
| Work | Explains or resolves something about the central question? |
| Relevance | Addresses real concerns in this line? |
| Grab | Substantial magnetism? |

3+ yes = essential, 2 = context, 0-1 = curiosity.
