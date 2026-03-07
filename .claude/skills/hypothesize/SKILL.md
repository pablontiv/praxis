---
name: hypothesize
description: |
  Usar siempre que el usuario necesite tomar una decisión respaldada por
  evidencia — evaluar si una tecnología, migración, arquitectura o vendor
  vale la pena ANTES de comprometer recursos. Estructura claims en hipótesis
  falsificables, recopila evidencia a favor/en contra, y produce un veredicto
  Go/No-Go. Usar este skill siempre que el usuario presente una propuesta con
  claims, pregunte "deberíamos migrar/adoptar/reescribir X?", quiera comparar
  alternativas con evidencia, comparta un artículo o recomendación preguntando
  "que opinas?", o referencie un documento de investigación existente — incluso
  si no pide una evaluación estructurada e incluso si solo dice "vale la pena
  X?" o "is Y worth it?" o "should we do Z?".
  (No para: exploración abierta = discover, descomponer planes en tareas = roadmap.)
user-invocable: true
argument-hint: "[tema-corto] o [archivo-existente.md] o [contenido con claims a falsar]"
---

# Routing: detectar modo de operación

Determinar qué modo aplicar según la entrada del usuario (ver ARGUMENTS al final):

1. ¿Es un path a un archivo `.md` que existe en el working directory?
   - **SÍ** → **MODO SEGUIMIENTO** (ir a "Seguimiento de investigación existente")

2. ¿Es un tema corto (1-5 palabras, sin estructura ni claims detallados)?
   - **SÍ** → **MODO CREAR** (ir a "Crear investigación nueva" — flujo interactivo desde Paso 0)

3. ¿Contiene contenido sustancial (párrafos, claims, propuestas, recomendaciones, análisis)?
   - **SÍ** → **MODO DIRECTO** (ir a "Investigación directa desde contenido")

---

# Rootline Integration (optional data layer)

hypothesize can use rootline as its data layer for frontmatter validation. Rootline is optional — the skill works without it, but validation features are disabled.

## Gate check

After routing, check for rootline availability:

```bash
command -v rootline
```

If not found, skip all `rootline validate` steps below. All other behavior (phases, document structure, checklists) remains unchanged.

## Cross-referencing related work

When creating a new investigation (CREAR mode) or continuing one (SEGUIMIENTO mode), use rootline to find related existing work. This prevents duplicate investigations and surfaces relevant context:

```bash
# Find related discover lines by scanning question files
rootline query lines/ --where 'tipo == "question"' --output table 2>/dev/null

# Find existing hypothesize investigations
rootline query . --where 'metodo == "hypothesize"' --output table 2>/dev/null

# Find closed lines that may have covered this topic
rootline query closed/ --where 'tipo == "closure"' --output table 2>/dev/null

# Find related theories
rootline query theories/ --output table 2>/dev/null
```

If related work exists, inform the user before proceeding: show what was found, where it is, and ask whether to reference it or proceed independently.

## Frontmatter schema

Investigation documents should live in directories with a `.stem` schema that validates their frontmatter:

```yaml
version: 2
schema:
    estado:
        type: string
        required: true
    fecha:
        type: string
        required: true
    metodo:
        type: enum
        enum: [hypothesize]
    origen:
        type: string
    fase_actual:
        type: integer
```

## Frontmatter in investigation documents

Every investigation document includes YAML frontmatter as its structured metadata:

```yaml
---
estado: "Fase 1"
fecha: "YYYY-MM-DD"
metodo: hypothesize
origen: ""
fase_actual: 1
---
```

The frontmatter fields mirror the inline `> Estado: Fase N` header:
- `estado` and `fase_actual` track phase state in a rootline-queryable way
- `fecha` is the creation date
- `metodo` is always `hypothesize`
- `origen` links to the source document or line, if any

## Keeping frontmatter and inline header in sync

Whenever the inline `> Estado: Fase N [estado]` header changes (phase transition, status update), also update:
- `estado` in frontmatter (e.g., `estado: "Fase 3"`)
- `fase_actual` in frontmatter (e.g., `fase_actual: 3`)

Both representations must always agree. The frontmatter is the structured source of truth; the inline header is the human-readable display.

## Validation step

After creating or updating an investigation document, if rootline is available:

```bash
rootline validate [file]
```

This validates the frontmatter against the `.stem` schema. If validation fails, report the errors but do not block the investigation workflow.

---

## Ejecución por modo

Una vez determinado el modo, leer el archivo correspondiente y seguir sus instrucciones:

| Modo | Archivo | Cuándo |
|------|---------|--------|
| CREAR | [crear-mode.md](crear-mode.md) | Tema corto → flujo interactivo de 5 fases |
| DIRECTO | [directo-mode.md](directo-mode.md) | Contenido sustancial → extraer claims y analizar |
| SEGUIMIENTO | [seguimiento-mode.md](seguimiento-mode.md) | Archivo .md existente → parsear estado y continuar |
