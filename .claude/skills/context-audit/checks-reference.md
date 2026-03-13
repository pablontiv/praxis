# Checks Reference — Context Audit

Referencia tecnica para los 8 checks. Cada check tiene: Why (evidencia),
Detect (heuristica), Remediate (accion).

---

## C1: Redundancy

**Aplica a**: context, rule

**Why**: (F5, F6) Los context files son altamente redundantes con documentacion
existente. Solo ayudan +2.7% cuando son la unica fuente de informacion.

**Detect**:
1. Leer el context file seccion por seccion (split por `##`)
2. Para cada seccion, extraer claims/instrucciones clave
3. Buscar las mismas frases en README.md, docs/*.md, y config files:
```bash
grep -rl "KEYWORD" README.md docs/ *.toml *.json 2>/dev/null
```
4. REDUNDANT si >60% del contenido de la seccion aparece en otro archivo

**PASS**: <2 secciones redundantes. **FAIL**: >=2 secciones redundantes.

**Remediate**: Eliminar secciones redundantes. Si la seccion tiene 1 instruccion
unica mezclada, extraer solo esa instruccion y descartar el resto.

---

## C2: Overview Bloat

**Aplica a**: context, skill

**Why**: (F3) Overviews de codebase no mejoran file discovery. El agente tiene
ls, find, grep. 100% de context files Sonnet-4.5 incluyen overviews sin
beneficio medible.

**Detect**: Buscar patrones de overview:
```bash
# Arboles de directorios
grep -cE '^\s*(\xe2\x94\x9c|\xe2\x94\x94|\xe2\x94\x82|\xe2\x94\x80|\.\.\.|\.\./|src/|lib/|cmd/)' FILE

# Headers de overview
grep -ciE '^#{1,3}\s*(project structure|directory|architecture|overview|codebase|layout|file structure|folder)' FILE

# Listados de paths
grep -cE '^\s*[-*]\s*`?[\w/]+\.(ts|js|py|go|rs|toml|json|yaml|yml)`?\s*([-:]|$)' FILE
```

**PASS**: 0 matches. **WARN**: 1-3 matches. **FAIL**: >3 matches.

**Remediate**: Eliminar la seccion completa. No reemplazar con nada — el agente
descubre estructura solo. Si hay instrucciones de comportamiento mezcladas,
extraerlas y descartar el overview.

---

## C3: Vague Instructions

**Aplica a**: todos los tipos

**Why**: (F2, F7) Los comandos especificos son adoptados 160x mas que las
descripciones. Las instrucciones vagas se siguen fielmente pero cuestan tokens
sin ROI.

**Detect**: Para cada linea con lenguaje directivo (Use, Always, Never, Prefer,
Make sure, Ensure, Run, Should, Must):
1. Tiene un comando en backticks? -> especifica
2. Referencia un path concreto? -> especifica
3. Menciona una herramienta con su invocacion? -> especifica
4. Ninguno de los anteriores -> vaga

**PASS**: >80% especificas. **WARN**: 60-80%. **FAIL**: <60%.

**Remediate**: Investigar el repo para encontrar el comando real:
```bash
grep -rn "TOOL_NAME" Makefile Justfile package.json .github/workflows/ scripts/ 2>/dev/null | head -5
```
Reescribir: "Use the project's linter" -> "`cargo clippy --all-targets -- -D warnings`"

---

## C4: Instruction Density

**Aplica a**: todos los tipos

**Why**: (F1, F4, F8) +20% costo por context files verbosos. +10-22% reasoning
tokens por instrucciones innecesarias. Mas contexto no es mejor.

**Detect**:
1. Contar total de lineas no-vacias
2. Contar lineas "accionables": contienen backtick-command, directiva
   imperativa con objeto especifico, o regla do/don't explicita
3. Ratio = accionables / total

**PASS**: >60%. **WARN**: 40-60%. **FAIL**: <40%.

**Remediate**: Eliminar filler: parrafos explicativos sin instruccion, historia
del proyecto, restatements de la misma regla. Mantener solo lineas que pasan
el test "el agente haria algo diferente sin esto?"

---

## C5: Tooling Specificity

**Aplica a**: context, rule

**Why**: (F7) Hallazgo de mayor impacto del paper. Herramientas mencionadas con
comando exacto son adoptadas 160x mas. "pytest" es bueno; `uv run pytest
tests/ -x --tb=short` es 160x mejor.

**Detect**: Buscar menciones de herramientas conocidas (pytest, jest, vitest,
cargo, npm, yarn, pnpm, bun, uv, pip, go, make, just, docker, kubectl, etc.)
y verificar si tienen un comando asociado en backticks dentro de 3 lineas.

**PASS**: >80% con comando. **WARN**: 50-80%. **FAIL**: <50%.

**Remediate**: Para cada mencion sin comando, investigar uso real en el proyecto:
```bash
grep -rn "TOOL" Makefile Justfile package.json scripts/ .github/workflows/ 2>/dev/null
```
Agregar el comando exacto como se usa en el proyecto.

---

## C6: Linter-Enforced Rules

**Aplica a**: context, rule

**Why**: (F4) Si un linter enforce una regla, documentarla en el context file
fuerza al agente a procesarla dos veces: una por la instruccion, otra por el
feedback del linter. Desperdicio puro de tokens.

**Detect**:
1. Identificar reglas de estilo/formato en el context file (indentacion, quotes,
   semicolons, naming, import ordering, line length, etc.)
2. Verificar si existen configs de linter correspondientes:
```bash
for f in .eslintrc* .prettierrc* biome.json .clippy.toml .golangci.yml \
         pyproject.toml .ruff.toml ruff.toml .pre-commit-config.yaml; do
  test -f "$f" && echo "LINTER:$f"
done
```
3. Si una regla de estilo en el context file corresponde a una categoria
   cubierta por un linter existente -> innecesaria

**PASS**: 0 reglas redundantes. **WARN**: 1-2. **FAIL**: >=3.

**Remediate**: Eliminar reglas redundantes. Reemplazar con una linea:
`Lint: [comando exacto del linter]. Pre-commit verifica automaticamente.`

---

## C7: Length

**Aplica a**: todos los tipos (con targets diferenciados)

**Why**: (F1, F2, F4) El paper muestra que developer-written files promedian 641
palabras pero solo mejoran ~4%. El sweet spot esta en archivos cortos donde
solo sobreviven instrucciones de alto valor.

**Targets por tipo**:

| Tipo | PASS | WARN | FAIL |
|------|------|------|------|
| context (CLAUDE.md) | <=300 words | 301-500 | >500 |
| rule (.claude/rules/) | <=150 words | 151-250 | >250 |
| skill (SKILL.md) | <=500 lines | 501-700 | >700 |
| agent (.claude/agents/) | <=300 words | 301-500 | >500 |

**Detect**:
```bash
wc -w FILE    # para context, rule, agent
wc -l FILE    # para skill
```

**Remediate**: Aplicar C1-C6 y C8 primero (suelen reducir suficiente).
Si aun excede, sugerir split: CLAUDE.md (critico, <150w) + .claude/rules/
(reglas por dominio). Priorizar: comandos de tooling (C5) > restricciones
unicas > todo lo demas.

---

## C8: Non-Actionable Sections

**Aplica a**: todos los tipos

**Why**: (F3, F4) Secciones que no cambian comportamiento del agente son
desperdicio puro. Overviews, historia del proyecto, filosofia del equipo,
contexto que no condiciona una accion.

**Detect**: Clasificar cada seccion (por `##` header):

| Clasificacion | Criterio | Accionable? |
|---------------|----------|-------------|
| COMMAND | Contiene comandos en backticks | Si |
| CONSTRAINT | Contiene always/never/must/must not/do not | Si |
| PREFERENCE | Contiene prefer/when possible/try to + trigger especifico | Si |
| KNOWLEDGE | Descripcion sin lenguaje imperativo | No |
| OVERVIEW | Descripcion de estructura/arquitectura | No |

**PASS**: <=1 seccion no-accionable. **WARN**: 2-3. **FAIL**: >=4.

**Remediate**:
- OVERVIEW: eliminar completamente (cubierto por C2)
- KNOWLEDGE: eliminar, o reformular como constraint si contiene info critica.
  Ej: "Este proyecto usa monorepo con packages/" -> eliminar (ls existe).
  Pero: "La API usa snake_case en DB — nunca camelCase en SQL" -> mantener
  (es CONSTRAINT disfrazado de KNOWLEDGE).
- PREFERENCE vaga: hacer especifica o eliminar

---

# Memory Checks (M1-M4)

Checks especificos para archivos de memoria (`~/.claude/projects/*/memory/`).
Las memorias se cargan automaticamente en cada sesion de un proyecto y pueden
acumular deuda de contexto con el tiempo.

---

## M1: Staleness

**Aplica a**: memory

**Why**: Las memorias referencian estado que cambia: branches, tasks en progreso,
decisiones temporales. Una memoria que dice "branch feature-x en progreso"
cuando ese branch ya se mergeó es ruido que ocupa tokens.

**Detect**:
1. Leer cada memory file
2. Buscar referencias a estado temporal:
   - Branches: verificar si existen con `git branch -a` en el repo asociado
   - Tasks/status: frases como "en progreso", "pendiente", "next step"
     que pueden ser obsoletas
   - Fechas relativas ya pasadas
3. Verificar campo `type: project` en frontmatter — estos son los mas
   propensos a staleness

**PASS**: Sin referencias a estado obsoleto. **FAIL**: >=1 referencia stale.

**Remediate**: Eliminar la memoria stale, o actualizarla si el contenido base
sigue siendo relevante. Si el proyecto al que refiere ya no existe o cambio
significativamente, eliminar.

---

## M2: Cross-Project Redundancy

**Aplica a**: memory

**Why**: El mismo usuario puede tener la misma preferencia guardada en multiples
project memories (ej: "user prefers conventional commits" en 3 proyectos).
Esto ocupa tokens N veces. Preferencias globales deben vivir en user-level
(`~/.claude/CLAUDE.md` o `~/.claude/rules/`), no replicadas por proyecto.

**Detect**:
1. Leer todas las memorias across projects
2. Agrupar por tipo (user, feedback, project, reference)
3. Para memorias tipo `user` y `feedback`: buscar contenido semanticamente
   duplicado entre proyectos
4. Una memoria aparece en >=2 proyectos con contenido similar -> redundante

**PASS**: Sin duplicados cross-project. **WARN**: 1-2 duplicados. **FAIL**: >=3.

**Remediate**: Mover la memoria duplicada a `~/.claude/CLAUDE.md` o
`~/.claude/rules/` (user-level) y eliminar las copias por proyecto.
Preferencias del usuario son globales, no project-scoped.

---

## M3: Index Bloat

**Aplica a**: memory-index (MEMORY.md)

**Why**: MEMORY.md se carga siempre en contexto y lineas despues de 200 se
truncan (segun la documentacion del sistema de memoria). Un indice largo
pierde entradas al final.

**Detect**:
```bash
wc -l MEMORY.md
```

**PASS**: <=100 lines. **WARN**: 101-200 lines. **FAIL**: >200 lines.

**Remediate**: Consolidar entradas relacionadas. Eliminar punteros a memorias
que ya no existen. Reorganizar por relevancia (lo mas importante primero,
ya que el truncamiento corta desde el final).

---

## M4: Wrong Type

**Aplica a**: memory

**Why**: El sistema de memoria define explicitamente que NO se debe guardar:
code patterns, conventions, architecture, file paths, project structure,
git history, debugging solutions. Esta informacion es derivable del codigo
o git y guardarla como memoria es desperdicio.

**Detect**: Verificar si el contenido de la memoria cae en categorias prohibidas:
1. **Code patterns/conventions**: menciona patrones de codigo, naming conventions,
   o estructura de archivos del proyecto
2. **Git history**: referencias a commits, who-changed-what, recent changes
3. **Debugging solutions**: fix recipes, workarounds para bugs ya resueltos
4. **Info ya en CLAUDE.md**: contenido duplicado con CLAUDE.md del proyecto

Cross-reference con el campo `type` en frontmatter:
- `type: user` -> debe ser sobre el usuario, no sobre el codigo
- `type: feedback` -> debe ser guia de comportamiento, no debug info
- `type: project` -> debe ser decisiones/contexto no derivable, no estructura
- `type: reference` -> debe ser puntero externo, no documentacion inline

**PASS**: Contenido alineado con su tipo. **FAIL**: Contenido derivable del codigo/git.

**Remediate**: Eliminar la memoria. Si contiene algo de valor, moverlo al
lugar correcto (CLAUDE.md para convenciones, el codigo mismo para patterns).
