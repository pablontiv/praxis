---
name: sessions
description: Buscar y analizar sesiones anteriores de Claude Code para recuperar contexto entre sesiones
user-invocable: true
disable-model-invocation: false
argument-hint: "[keyword] | --topics | --recent N"
allowed-tools: Bash, Read
---

# Skill: Sessions

## Contexto
Este skill busca en las sesiones anteriores de Claude Code del proyecto actual. Permite recuperar discusiones previas, encontrar contexto perdido entre sesiones, y analizar qué temas se han discutido.

## Proceso

### 1. Derivar directorio de sesiones

El directorio de sesiones se calcula desde el cwd:
```
~/.claude/projects/<slug>/
```
Donde `<slug>` es el path del proyecto con `/` reemplazado por `-` (ej: `/home/user/my-project` → `-home-user-my-project`).

Usar Bash para verificar que el directorio existe:
```bash
SESSION_DIR="$HOME/.claude/projects/$(pwd | tr '/' '-')/"
ls "$SESSION_DIR"/*.jsonl 2>/dev/null | head -5
```

Si no existe o está vacío, informar al usuario.

### 2. Listar sesiones

Listar archivos `.jsonl` ordenados por fecha, excluyendo subagentes:
```bash
ls -lt "$SESSION_DIR"/*.jsonl 2>/dev/null | grep -v agent- | head -N
```

### 3. Leer y parsear sesiones

Para cada sesión relevante, usar Read para cargar el archivo `.jsonl`. Cada línea es un objeto JSON con:
- `type`: "user" o "assistant" (ignorar otros tipos)
- `message.content`: texto del mensaje (puede ser string o array de bloques)
- `timestamp`: fecha del mensaje

**Filtrar ruido** — ignorar mensajes que empiecen con:
- `<system-reminder>`
- `Contents of /`
- `<command`
- `Caveat:`

### 4. Aplicar filtro según argumento

| Argumento | Acción |
|-----------|--------|
| (vacío) | Listar las 10 sesiones más recientes con resumen |
| `[keyword]` | Filtrar sesiones que contengan el keyword, mostrar extractos |
| `--topics` | Analizar contenido y agrupar por temas frecuentes |
| `--recent N` | Listar las N sesiones más recientes |
| `--context` | Query rootline session-state (see Rootline Integration section) |

### 5. Presentar resultados

Para cada sesión mostrar:
- Fecha y hora
- ID de sesión (primeros 12 caracteres)
- Conteo de mensajes (usuario / asistente)
- Primeras 3-5 líneas significativas del usuario
- Si hay keyword: extractos con contexto alrededor de la coincidencia

## Rootline Integration (optional)

If rootline and `/context-save` are available, sessions can also query structured session state:

```bash
command -v rootline 2>/dev/null
```

If rootline is available and `.claude/session-state/` exists with a `.stem` schema:

```bash
# List saved session contexts for this project
rootline query .claude/session-state/ --where "proyecto == '$(basename $(pwd))'" --output table

# Most recent saved context
rootline query .claude/session-state/ --where "proyecto == '$(basename $(pwd))'" --output table --limit 1
```

This supplements (not replaces) the .jsonl session search. Rootline session-state has structured metadata (branch, active work, decisions, next steps) while .jsonl has full conversation history.

## Modos de uso

| Comando | Descripción |
|---------|-------------|
| `/sessions` | Lista las 10 sesiones más recientes |
| `/sessions [keyword]` | Filtra sesiones que contengan el keyword |
| `/sessions --topics` | Distribución de temas discutidos |
| `/sessions --recent N` | Lista las N sesiones más recientes |
| `/sessions --context` | Buscar contexto guardado via rootline (requiere /context-save) |

## Cuándo usar

- **Recuperar contexto**: "¿Qué discutimos sobre X en sesiones anteriores?"
- **Continuidad**: Antes de retomar una línea, buscar qué se avanzó
- **Conexiones**: Descubrir que un tema se discutió en múltiples sesiones
- **Al inicio de sesión**: Si el estado no es suficiente para recuperar contexto

## Notas

- Solo lee datos — no modifica ningún archivo
- Ignora sesiones de subagentes (archivos `agent-*.jsonl`)
- Filtra automáticamente system-reminders y metadata de comandos
