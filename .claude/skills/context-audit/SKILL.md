---
source: pablontiv/praxis
name: context-audit
description: |
  Auditar, optimizar, y guiar la creacion/modificacion de archivos de contexto
  para agentes de codigo: CLAUDE.md, AGENTS.md, rules (.claude/rules/), skills
  (.claude/skills/), agent definitions (.claude/agents/), y memory files
  (~/.claude/projects/*/memory/). Aplica 12 checks basados en evidencia empirica
  (paper "Evaluating AGENTS.md", Gloaguen et al., 2026) para detectar redundancia,
  bloat, instrucciones vagas, baja densidad accionable, y falta de especificidad.
  Soporta sweep cross-repo y auditoria de superficie user-level (~/.claude/).
  Usar este skill siempre que el usuario quiera: auditar o mejorar context files
  existentes, crear o agregar rules/skills/agents con calidad validada, revisar
  si sus instrucciones son efectivas, reducir tokens de contexto, limpiar memory
  files obsoletas, detectar redundancia entre archivos, evaluar si un README o
  CLAUDE.md está desactualizado respecto al codigo, o hacer sweep de toda la
  superficie de contexto. Triggers: "optimizar CLAUDE.md", "review agents.md",
  "reducir contexto", "mi CLAUDE.md es muy largo", "audit context", "shrink",
  "too many tokens", "review my instructions", "are my rules effective",
  "audit skills", "sweep context", "evaluar contexto", "context bloat",
  "agregar regla", "crear skill", "memory cleanup", "is my CLAUDE.md any good?",
  "README desactualizado" — incluso si no dice "context-audit".
  (No para: conform = repo infrastructure, hypothesize = decisiones con evidencia,
  discover = exploración abierta.)
user-invocable: true
argument-hint: "[--audit-only] [--sweep] [--apply] [path|repo]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

# /context-audit — Evidence-Based Context File Optimization

Aplica 8 checks derivados de investigacion empirica (arXiv:2602.11988v1) que
demostro que los context files mal escritos reducen rendimiento de agentes entre
0.5-3% e incrementan costo de inferencia ~20%.

## Routing

Parse `$ARGUMENTS`:

| Input | Mode | Behavior |
|-------|------|----------|
| (empty) | **auto** | Descubrir context files del proyecto actual, auditar, proponer |
| `--audit-only` | **audit** | Solo reporte, no tocar nada |
| `--audit-only [path]` | **targeted audit** | Auditar solo ese archivo |
| `--apply` | **apply** | Auditar y aplicar sin confirmaciones individuales |
| `--sweep` | **sweep** | Auditar todos los repos en `/home/shared/*/` + `~/.claude/` |
| `[path]` | **targeted** | Auditar solo el archivo o directorio especificado |

## Phase 1: Discover & Audit

### Step 1: Locate context files

**Modo auto** (proyecto actual):
```bash
# Context files del proyecto
for f in CLAUDE.md AGENTS.md; do test -f "$f" && echo "CTX:$f"; done
ls .claude/rules/*.md 2>/dev/null | while read f; do echo "RULE:$f"; done
ls .claude/skills/*/SKILL.md 2>/dev/null | while read f; do echo "SKILL:$f"; done
ls .claude/agents/*.md 2>/dev/null | while read f; do echo "AGENT:$f"; done
```

**Modo sweep** (cross-repo):
```bash
# Repos de proyecto
for repo in /home/shared/*/; do
  test -d "$repo/.claude" -o -f "$repo/CLAUDE.md" && echo "REPO:$repo"
done

# User-level (inyectado en TODA sesion)
test -f ~/.claude/CLAUDE.md && echo "CTX:~/.claude/CLAUDE.md"
ls ~/.claude/rules/*.md 2>/dev/null | while read f; do echo "RULE:$f"; done
ls ~/.claude/agents/*.md 2>/dev/null | while read f; do echo "AGENT:$f"; done

# Memory (proponer, no entrar automaticamente)
MEMORY_DIRS=$(ls -d ~/.claude/projects/*/memory/ 2>/dev/null)
if [ -n "$MEMORY_DIRS" ]; then
  MEMORY_COUNT=$(echo "$MEMORY_DIRS" | wc -l)
  echo "MEMORY_FOUND:$MEMORY_COUNT project memories"
  # -> Usar AskUserQuestion para preguntar si incluir memory en el audit
fi
```

**Memory discovery**: cuando se detectan directorios de memoria, **proponer** al
usuario via `AskUserQuestion` antes de escanearlos. Ejemplo:
> "Encontre N directorios de memory en ~/.claude/projects/. Quieres incluirlos en la auditoria?"

Si acepta:
```bash
ls ~/.claude/projects/*/memory/MEMORY.md 2>/dev/null | while read f; do echo "MEMIDX:$f"; done
# Para cada proyecto, archivos de memoria (excluyendo el indice)
for dir in ~/.claude/projects/*/memory/; do
  ls "$dir"/*.md 2>/dev/null | grep -v MEMORY.md | while read f; do echo "MEM:$f"; done
done
```

Para cada archivo descubierto, clasificar su tipo:

| Pattern | Tipo | Word target |
|---------|------|-------------|
| `CLAUDE.md`, `AGENTS.md` | context | <=300 words |
| `.claude/rules/*.md` | rule | <=150 words |
| `.claude/skills/*/SKILL.md` | skill | <=500 lines |
| `.claude/agents/*.md` | agent | <=300 words |
| `projects/*/memory/MEMORY.md` | memory-index | <=200 lines (se trunca) |
| `projects/*/memory/*.md` (excl index) | memory | <=50 words/entry |

### Step 2: Gather comparison sources

Para cada proyecto, identificar fuentes contra las que medir redundancia:

```bash
# Documentacion existente
test -f README.md && echo "REF:README.md"
ls docs/*.md 2>/dev/null | head -10

# Configs de linters (para check C6)
for f in .eslintrc* .prettierrc* biome.json .clippy.toml .golangci.yml \
         .golangci.yaml pyproject.toml .flake8 .ruff.toml ruff.toml \
         .pre-commit-config.yaml; do
  test -f "$f" && echo "LINTER:$f"
done

# Package configs
for f in package.json Cargo.toml go.mod pyproject.toml; do
  test -f "$f" && echo "PKG:$f"
done

# CI workflows
ls .github/workflows/*.yml 2>/dev/null
```

### Step 3: Run checks

Para cada archivo, ejecutar los checks aplicables. Consultar `checks-reference.md`
para la logica detallada de deteccion y remediacion de cada check.

**Matriz de applicabilidad por tipo:**

| Check | context | rule | skill | agent | mem-idx | memory |
|-------|---------|------|-------|-------|---------|--------|
| C1 Redundancy | X | X | - | - | - | - |
| C2 Overview bloat | X | - | X | - | - | - |
| C3 Vague instructions | X | X | X | X | - | - |
| C4 Instruction density | X | X | X | X | - | - |
| C5 Tooling specificity | X | X | - | - | - | - |
| C6 Linter-enforced | X | X | - | - | - | - |
| C7 Length | X | X | X | X | X | X |
| C8 Non-actionable | X | X | X | X | - | - |
| M1 Staleness | - | - | - | - | - | X |
| M2 Cross-project redundancy | - | - | - | - | - | X |
| M3 Index bloat | - | - | - | - | X | - |
| M4 Wrong type | - | - | - | - | - | X |

`-` = skip check para ese tipo.

### Step 4: Output report

Formato por archivo:

```
CONTEXT-AUDIT — [filename]
══════════════════════════════════════
Type: [context|rule|skill|agent]  Words: [N]  Sections: [N]

REDUNDANCY
──────────
[PASS|FAIL|SKIP] C1  [detail]
[PASS|FAIL|SKIP] C2  [detail]

SPECIFICITY
───────────
[PASS|FAIL|SKIP] C3  [detail]
[PASS|FAIL|SKIP] C5  [detail]

EFFICIENCY
──────────
[PASS|FAIL|SKIP] C4  [detail]
[PASS|FAIL|SKIP] C6  [detail]
[PASS|FAIL|SKIP] C7  [detail]
[PASS|FAIL|SKIP] C8  [detail]

SCORE: [N]/[applicable] checks passing ([%])
TOKEN WASTE EST: ~[N] tokens/invocation ([%] of file)
```

**En modo sweep**, agregar resumen al final:

```
SWEEP SUMMARY
═════════════
Repos audited: [N]
Files audited: [N]
Total context words: [N]
Estimated token waste: ~[N] tokens ([%])

Top offenders:
  1. [file] — [score] — [primary issue]
  2. [file] — [score] — [primary issue]
  3. [file] — [score] — [primary issue]
```

## Phase 2: Propose

Para cada archivo con FAIL checks:

1. **Leer** el archivo completo
2. **Aplicar remediaciones** en orden: C1 (eliminar redundancia) -> C2 (eliminar
   overviews) -> C6 (eliminar reglas de linter) -> C8 (eliminar no-accionable) ->
   C3 (hacer instrucciones especificas) -> C5 (agregar comandos de tooling) ->
   C4 (verificar densidad) -> C7 (verificar longitud)
3. **Generar version optimizada** del archivo completo
4. **Mostrar diff summary**: secciones eliminadas, reescritas, y mantenidas

Principio rector: **substractivo, no aditivo**. El objetivo es eliminar, no agregar.
Cada linea que sobrevive debe pasar el test: "el agente fallaria sin esto?"

En modo `--audit-only`, parar aqui. Mostrar solo las propuestas sin aplicar.

## Phase 3: Apply

Si no es `--audit-only`:

1. Para cada archivo con propuesta, mostrar el diff
2. Si no es `--apply`, pedir confirmacion con `AskUserQuestion` antes de cada archivo
3. **Archivos de usuario** (`~/.claude/*`) siempre requieren confirmacion explicita,
   incluso en modo `--apply`
4. Aplicar cambios via `Edit`
5. Re-ejecutar checks en el archivo modificado
6. Mostrar before/after:

```
POST-OPTIMIZATION — [filename]
═══════════════════════════════
Score: [N]/[M] -> [N']/[M'] ([%] -> [%'])
Words: [before] -> [after] (saved [N] words)
Token savings: ~[N] tokens/invocation
```

## Important Guidelines

- **Nunca commitear automaticamente** — los cambios quedan unstaged
- **Substractivo por defecto** — el objetivo es ELIMINAR, no agregar
- **Respetar conocimiento tacito** — si una instruccion contiene info que no esta
  en ningun otro archivo del repo, mantenerla (probablemente es conocimiento
  del desarrollador)
- **No auditar evals/** — los directorios de evaluacion de skills no son context files
- **Boundary con update-docs**: update-docs verifica precision factual (code drift).
  context-audit verifica efectividad agentica (es necesaria esta instruccion?).
  Son complementarios: primero update-docs (sync), luego context-audit (optimize).
- **Ownership**: despues de modificar archivos en `/home/shared/`, ejecutar
  `chown -R pones:dev /home/shared/<repo>`

## Evidence Base (arXiv:2602.11988v1)

Los 8 checks se derivan de estos hallazgos empiricos:

| # | Hallazgo | Impacto | Checks |
|---|----------|---------|--------|
| F1 | LLM-generated context files reducen rendimiento | -0.5 a -3%, +20% costo | C4, C7 |
| F2 | Developer-written solo mejoran ~4% | ROI bajo si no es especifico | C3, C5 |
| F3 | Overviews de codebase son inutiles | 0% mejora en file discovery | C2, C8 |
| F4 | Instrucciones se siguen pero cuestan tokens | +10-22% reasoning tokens | C1, C4, C6, C8 |
| F5 | Context files redundantes con docs existentes | Duplicacion sin valor | C1 |
| F6 | Sin docs, LLM context files ayudan +2.7% | Solo utiles como unica fuente | C1 |
| F7 | Comandos especificos adoptados 160x mas | Maximo ROI por linea | C3, C5 |
| F8 | Modelos fuertes no generan mejor contexto | El problema es seleccion, no generacion | C4 |

**Perfil optimo derivado**: <300 palabras, solo comandos exactos y restricciones
duras, zero overviews, zero redundancia con docs/configs, cada linea cambia
comportamiento del agente.
