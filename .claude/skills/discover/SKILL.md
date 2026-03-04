---
name: discover
description: |
  Structured R&D framework for lines of inquiry. Supports Plan-Act-Observe-Reflect cycles,
  grounded theory, anti-presupposition process, and knowledge connections.

  Subcommands: init, new-line, cycle, reflect, theory, status, update-map,
  interlink, review-patterns, research. Use @file to analyze an external file.
  Without arguments shows system status.

  Use when the user says "nueva línea", "new line", "descubrir", "discover",
  "ciclo", "cycle", "reflexión", "reflect", "teoría", "theory",
  "estado", "status", "inicializar", "init", "actualizar mapa",
  "interconectar", "revisar patrones", "investigar", or wants to
  manage lines of inquiry, document cycles, or track emergent patterns.
  Also use when the user provides an external file to analyze with "@file".
user-invocable: true
argument-hint: "<subcommand> [args] | @file — subcommands: init, new-line, cycle, reflect, theory, status, update-map, interlink, review-patterns, research"
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
| `@path/to/file` | → **intake** | file path (without `@`) |

**`@` detection**: If `$ARGUMENTS` starts with `@`, strip the `@` prefix and route to **intake** with the remaining path as the file argument.

**Fork detector**: Not a subcommand — it's a behavior. Claude should proactively detect forks during any subcommand (see "Fork Detection" section at the end).

---

## Subcommand: init

Initialize an R&D project in the current directory.

### Process

1. **Validate**: Check if `MAP.md` already exists. If yes, warn and ask to confirm overwrite.

2. **Create directory structure**:
```
intake/
backlog/
lines/
theories/
paused/
closed/
shared/code/
shared/patterns/
shared/templates/
.claude/rules/
```

**intake/** is the reference library for the discover framework. Files arrive here via `/discover @file` and stay while they're being investigated. Lines, backlog items, and theories reference intake docs via `[[intake/name]]` wikilinks. A file leaves `intake/` only when it graduates out of discover entirely — to `/hypothesize` (formal falsification) or `/roadmap` (implementation decomposition).

3. **Copy templates** from [templates/](templates/) to `shared/templates/`:
   - [QUESTION.md](templates/QUESTION.md)
   - [FIELD-LOG.md](templates/FIELD-LOG.md)
   - [CLOSURE.md](templates/CLOSURE.md)
   - [THEORY.md](templates/THEORY.md)

4. **Generate FRAMEWORK.md**: Copy [FRAMEWORK.md](templates/FRAMEWORK.md) to project root.

5. **Suggest CLAUDE.md setup**: If the project doesn't have a CLAUDE.md, suggest the user create one referencing the generated `.claude/rules/` files. Do not auto-generate — users should own their CLAUDE.md.

6. **Generate state files**:

   `.claude/rules/current-state.md`:
   ```markdown
   # Current State
   > Last updated: [today's date]
   ## Active Lines
   (none yet)
   ## Paused Lines
   (none)
   ## Closed Lines
   (none)
   ## Last Session
   - [today's date]: Project initialized
   ```

   `.claude/rules/connections.md`:
   ```markdown
   # Discovered Connections
   ## Between Lines
   (no connections yet)
   ## Emergent Patterns
   (no patterns yet)
   ## Connections with Theories
   (none yet)
   ```

7. **Generate MAP.md** at project root:
   ```markdown
   # System Map
   > Last updated: [today's date]
   ## Structure
   ### /intake (Reference library)
   | Document | Classification | Referenced by |
   |----------|---------------|---------------|
   (empty)
   ### /backlog (Unexplored questions)
   | Question | Topic |
   |----------|-------|
   (empty)
   ### /lines (Active lines of inquiry)
   | Line | Central question | Cycles | Status |
   |------|-----------------|--------|--------|
   (none yet)
   ### /theories (Emergent theories)
   | Theory | Confidence | Connections |
   |--------|-----------|-------------|
   (none yet)
   ### /paused
   (none)
   ### /closed
   (none)
   ### /shared (Reusable artifacts)
   - /code: [empty]
   - /patterns: [empty]
   - /templates: QUESTION.md, FIELD-LOG.md, CLOSURE.md, THEORY.md
   ## Known Connections
   (none yet)
   ## Emergent Patterns
   (none yet)
   ## Current Context
   - **Active lines**: 0/3
   - **Last session**: [today's date] — Project initialized
   ```

8. **Confirm** to user with summary of what was created and next steps: `/discover new-line [name]`, `/discover status`.

**Notes**: Only creates structure — never overwrites existing line data. Templates are copied to the project so they can be customized per-project.

---

## Subcommand: new-line

Create a new line of inquiry with anti-presupposition process.

**Args**: `[name]` — kebab-case name for the line.

### Process

1. **Validate**:
   - No line with this name in `lines/`
   - Count active lines (max 2-3). If 3+, ask which to pause first.
   - Name must be kebab-case.

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

5. **Update system**: Update `.claude/rules/current-state.md`. MAP.md update deferred to `/discover update-map`.

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
   - PAUSE → move folder to `paused/`, update state
   - CLOSE → **automatically run review-patterns first**, then create CLOSURE.md from [template](templates/CLOSURE.md), move to `closed/`, update state
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

1. **Read**: `.claude/rules/current-state.md` + `MAP.md`

2. **Display**:
   ```
   ## FORGE — System Status

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

1. **Scan**: intake/ (reference docs), backlog/ (questions), lines/ (active + cycles), theories/ (confidence), paused/ (reasons), closed/ (dates + theories), shared/ (artifacts).

2. **Connections**: Search for `[[name]]` wikilinks, review connections.md.

3. **Regenerate MAP.md** with current state.

**When to run**: After new-line, cycle, reflect (PAUSE/CLOSE), theory, or at start of long sessions.

---

## Subcommand: interlink

Scan system and add wikilinks `[[name]]` where mentions are detected.

### Process

1. **Build entity list**: folder names from lines/, theories/, backlog/.

2. **Search**: For each .md file, find mentions NOT already inside `[[...]]`. Exclude code blocks, URLs, file paths.

3. **Propose changes**: Show summary with file, line, and proposed wikilink. Ask: apply all / review one by one / cancel.

4. **Apply**: Edit files, report changes, suggest `/discover update-map`.

5. **Orphan concepts** (optional): If frequent mentions of concepts without files, ask about creating stubs.

**Don't modify**: skill directories, templates.

---

## Subcommand: review-patterns

Evaluate maturity of emergent patterns.

### Process

1. **Extract patterns** from `connections.md` "Emergent Patterns" section.

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

Analyze an external file and classify it into the appropriate flow entry point.

**Trigger**: `$ARGUMENTS` starts with `@`. Strip the `@` to get the file path.

### Process

1. **Read the file** completely. If it doesn't exist, inform the user.

2. **Fast-path check**: If the file has markers from existing skills, it's NOT external — redirect:
   - `> Estado: Fase N` → already a `/hypothesize` document → suggest `/hypothesize [file]`
   - QUESTION.md/FIELD-LOG.md template markers → already a `/discover` artifact → suggest the appropriate subcommand
   - Roadmap frontmatter (`tipo:`, `estado:`, `epic:`) → already a `/roadmap` artifact → suggest `/roadmap pending` or `/roadmap loop`

3. **Extract 7 signals**: See [intake-signals.md](intake-signals.md) — "Signal Extraction" section.
   Each signal is deterministic and observable — count sections, scan for patterns, check extension. No interpretation.

4. **Classify**: Map signals to entry point using the mapping table in [intake-signals.md](intake-signals.md) — "Entry Point Mapping" section. If ambiguous, apply **Glaser Test** (same section).

5. **Anti-presupposition scan**: Run the anti-presupposition process on the file content.
   See [anti-presupposition.md](anti-presupposition.md) — steps 2-3 (detect presuppositions + observational reformulation).
   Focus on: what does the document assume without validating?

6. **Suggest adaptations**: Based on entry point, describe what the file needs to enter the flow.
   See [intake-signals.md](intake-signals.md) — "Adaptation Templates" section.

7. **Present results**: Show signal profile, classification, presuppositions, adaptations, and recommended command. Always include alternatives so the user can override.

### Output format

```
INTAKE — [filename]
═══════════════════

SIGNALS:
  Format:        [value]
  Structure:     [value] ([detail])
  Assertions:    [value] ([count] claims, [count] questions)
  Evidence:      [value] ([detail])
  Actionability: [value] ([detail])
  Domain:        [value] ([named items])
  Completeness:  [value] ([detail])

CLASSIFICATION: [entry point]
Confidence: [high/medium/low]

PRESUPPOSITIONS DETECTED:
├─ "[claim]" — [why it's a presupposition]
├─ "[claim]" — [why]
└─ "[claim]" — [why]

SUGGESTED ADAPTATIONS:
1. [adaptation]
2. [adaptation]
N. [adaptation]

COMMAND: [recommended command]

ALTERNATIVES:
  [alternative 1] — [when to choose this instead]
  [alternative 2] — [when to choose this instead]
```

### Edge cases

- **Binary files** (images, PDFs): Format = binary → always CONTEXTO
- **Very short files** (<5 lines): Treat as a topic → BACKLOG
- **Empty files**: Inform user, suggest starting with `/discover new-line` instead
- **Code files**: Classification = CONTEXTO — suggest attaching as evidence to an existing line

**Notes**: Intake never auto-executes a skill — it classifies, suggests, and hands off. The user decides.

**File lifecycle**: After classification, the original file stays in `intake/`. Generated artifacts (lines, backlog entries) reference it via `[[intake/name]]` wikilinks. The file leaves `intake/` only when the research graduates to `/hypothesize` or `/roadmap`. One intake file can generate multiple artifacts (lines, backlog items, theories) — this is expected.

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
