---
name: praxis
description: |
  Proxy inteligente para el flujo discover → hypothesize → roadmap.
  Hace reconocimiento del entorno, detecta fase del input, y delega al skill correcto.
  Reinvocable sobre el mismo documento en cualquier etapa.
  Use when the user says "praxis", "procesar", "evaluar", "siguiente paso",
  "en qué va", "continuar", or provides a file/topic to process through the flow.
user-invocable: true
argument-hint: "[archivo.md] | [tema] | (vacío = auto-detect)"
---

# /praxis — Proxy del Flujo

## Paso 1: Reconocimiento del entorno

Antes de evaluar el input, investigar el contexto real. Ejecutar en paralelo:

### Repo y proyecto
- Estructura del proyecto (`Glob: **/*.{py,ts,js,go,rs,tf,yaml}` — solo top-level patterns)
- Dependencias (package.json, Cargo.toml, requirements.txt, go.mod, etc.)
- README principal — leer para entender el dominio
- Branch actual y estado de git

### Estado del framework
- ¿Existe MAP.md? → discover inicializado
- ¿Existe `.claude/rules/current-state.md`? → leer estado actual
- ¿Existe `.claude/roadmap.local.md`? → roadmap configurado
- rootline CLI disponible? (`command -v rootline`)
- Investigaciones existentes (buscar `> Estado: Fase` en *.md)
- Líneas activas en `lines/`, teorías en `theories/`

### Online (solo si el input involucra un tema nuevo)
- Buscar estado del arte, documentación oficial, alternativas
- Anclar en evidencia externa antes de proceder

## Paso 2: Evaluar el input

### Si $ARGUMENTS es un archivo .md que existe:

Leer el archivo y detectar fase por marcadores:

| Marcador | Fase | Acción |
|----------|------|--------|
| `> Estado: Fase N` | Investigación en curso | → `Skill: hypothesize $ARGUMENTS` |
| QUESTION.md / FIELD-LOG.md markers | Línea discover activa | → `Skill: discover cycle [nombre-línea]` |
| Frontmatter con `tipo:`, `estado:`, `epic:` | Artefacto roadmap | → `Skill: roadmap pending` o `roadmap loop` |
| Ningún marcador conocido | Archivo externo nuevo | → Clasificar con señales (ver Paso 3) |

### Si $ARGUMENTS es un tema corto (1-5 palabras):

Verificar si ya existe trabajo sobre este tema:
1. Buscar en `lines/` carpeta con nombre similar
2. Buscar en `theories/` documento relacionado
3. Buscar investigaciones (`> Estado: Fase`) sobre el tema
4. Si existe → preguntar al usuario: ¿continuar existente o crear nuevo?
5. Si no existe → Clasificar como idea nueva (ver Paso 3)

### Si $ARGUMENTS está vacío:

Leer `.claude/rules/current-state.md` y presentar:
- Estado actual del framework
- Líneas activas y su fase
- Investigaciones en curso y su fase
- Sugerir siguiente acción basada en el estado

## Paso 3: Clasificar y delegar

Para archivos nuevos o temas nuevos, clasificar usando las señales de intake
(structure, assertions, evidence, actionability, domain, completeness).

Mapear a skill y **ejecutar directamente** (no solo sugerir):

| Clasificación | Skill invocado | Contexto que recibe |
|---------------|---------------|---------------------|
| Idea exploratoria (bajo en assertions, sin evidencia) | `Skill: discover new-line [tema]` | Reconocimiento del paso 1 |
| Claims sin validar (alto en assertions, sin/poca evidencia) | `Skill: hypothesize [contenido]` | Reconocimiento + búsqueda online del paso 1 |
| Investigación con evidencia | `Skill: hypothesize [archivo]` | Reconocimiento del paso 1 |
| Specs/requirements listos para descomponer | `Skill: roadmap [contenido]` | Reconocimiento + docs del repo |
| Código/datos | Sugerir attach a línea existente | — |

Antes de delegar, mostrar al usuario:
- Qué se detectó (fase, clasificación)
- Qué skill se va a invocar y por qué
- El contexto del reconocimiento (resumen)

Preguntar confirmación solo si la clasificación tiene confianza < alta.
