---
source: pablontiv/praxis
name: roadmap
version: openclaw-adapted
description: |
  Framework de planificación adaptado para OpenClaw. Descompone proyectos en epics, 
  features, stories y tasks. Integra con la estructura docs/epics/ del repositorio.
  
  Uso: /roadmap [pending|plan|status] o describir features a construir para 
  descomposición autónoma.
user-invocable: true
argument-hint: "[pending|plan|status|loop] [args]"
requires:
  - filesystem access to docs/epics/
  - Read/Write/Edit tools
  - Bash for queries
---

# /roadmap — Framework de Planificación para OpenClaw

Versión adaptada de praxis/roadmap para entornos OpenClaw donde no hay acceso
a CLI tools locales como `rootline`.

## Modo de Operación en OpenClaw

### Bootstrap

1. **Detección de roadmap-root**: Buscar en `docs/epics/` o preguntar al usuario
2. **Lectura de esquema**: Leer `.stem` en `docs/epics/` para entender el schema
3. **Queries via grep/bash**: Usar herramientas nativas de OpenClaw (read, glob, bash)

### Subcomandos

| Subcomando | Descripción |
|------------|-------------|
| `pending` | Lista trabajo pendiente filtrado por estado |
| `status` | Resumen del estado del roadmap |
| `plan` | Materializa un plan en archivos .md |
| `loop` | Ejecuta tasks pendientes en secuencia |

## Adaptaciones para OpenClaw

### Queries sin rootline

En lugar de `rootline query`, usar:
- `glob` + `read` para encontrar archivos
- `grep` en bash para filtrar por frontmatter
- `memory_search` para contexto relevante

### Estructura esperada

```
docs/epics/
├── .stem                    # Schema de validación
├── E01-*/
│   ├── README.md            # Epic index
│   ├── F01-*/
│   │   ├── README.md        # Feature index
│   │   └── S001-*/
│   │       ├── README.md    # Story index
│   │       └── T001-*.md    # Tasks
```

### Estados por defecto (adaptable via .stem)

- `Pending` — No iniciado
- `Specified` — Especificado, listo para empezar  
- `In Progress` — En curso
- `Completado` — Terminado
- `Obsoleto` — Ya no aplica
- `Diferida` — Postergado
- `Bloqueada` — Bloqueado por dependencias

## Uso

### Ver trabajo pendiente

```
/roadmap pending
```

### Ver estado general

```
/roadmap status
```

### Planificar nueva feature

```
Quiero construir un sistema de notificaciones para el cluster
```
→ Detecta modo autónomo, descompone en epics/features/stories/tasks

## Integración con herramientas de OpenClaw

- Usa `memory_search` para recordar decisiones previas sobre el proyecto
- Usa `web_search` para investigar patrones/architecturas
- Usa `sessions_spawn` para tareas paralelas de investigación
- Usa `cron` para recordatorios de seguimiento

## Limitaciones vs versión Claude Desktop

- No validación automática de schema (sin rootline)
- No queries complejas con expr-lang
- No tree view automático
- Requiere bash/grep para búsquedas

## Decisiones de diseño

1. **Mantener compatibilidad de estructura**: Los archivos .md son idénticos a praxis
2. **Reemplazar rootline con herramientas nativas**: grep, glob, read
3. **Sin dependencias externas**: Todo dentro del sandbox de OpenClaw
4. **PR-friendly**: Genera cambios listos para PR via workflow estándar
