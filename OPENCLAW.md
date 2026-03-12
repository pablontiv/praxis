# Praxis para OpenClaw

Adaptación del framework praxis para funcionar en entornos OpenClaw.

## Qué es esto

[Praxis](https://github.com/pablontiv/praxis) es un framework de productividad AI-native
desarrollado por pablontiv. Esta es una adaptación para que funcione en OpenClaw,
donde no hay acceso a herramientas CLI locales como `rootline` o `backscroll`.

## Skills adaptados

| Skill | Descripción | Archivo |
|-------|-------------|---------|
| `roadmap` | Planificación con descomposición en epics/features/stories/tasks | `.openclaw/skills/roadmap.md` |
| `discover` | Framework R&D con ciclos Plan-Act-Observe-Reflect | `.openclaw/skills/discover.md` |

## Skills no adaptados (funcionan nativamente)

| Skill | Notas |
|-------|-------|
| `test-loop` | Ya funciona con `exec` para ejecutar tests |
| `conform` | Depende de CI/GitHub Actions, no necesita adaptación |

## Principios de adaptación

1. **Sin dependencias CLI**: Todo via herramientas nativas de OpenClaw
2. **Estructura compatible**: Los archivos .md son idénticos a praxis original
3. **Aprovechar fortalezas de OpenClaw**:
   - `memory_search` para contexto de sesiones previas
   - `web_search`/`kimi_search` para investigación
   - `sessions_spawn` para paralelismo
   - `cron` para recordatorios
   - Git integration directa

## Instalación

Copiar la carpeta `.openclaw/` al workspace de OpenClaw:

```bash
# En tu repo homeserver o workspace personal
cp -r praxis/.openclaw/skills/* .openclaw/skills/
```

## Uso

### Roadmap

```
# Ver trabajo pendiente en docs/epics/
/roadmap pending

# Ver estado general
/roadmap status

# Planificar nuevo feature (modo autónomo)
Quiero construir un sistema de notificaciones...
→ /roadmap detecta modo autónomo y descompone
```

### Discover

```
# Iniciar investigación
/discover init mi-proyecto
/discover new-line tema-de-investigacion

# Ciclo de investigación
/discover cycle tema-de-investigacion

# Reflexión
/discover reflect tema-de-investigacion
```

## Estructura de archivos

### Roadmap (compatible con docs/epics/)

```
docs/epics/
├── .stem
├── E01-*/
│   ├── README.md
│   └── F01-*/
│       ├── README.md
│       └── S001-*/
│           ├── README.md
│           └── T001-*.md
```

### Discover (en workspace)

```
workspace/
└── discover/
    ├── lines/
    ├── paused/
    ├── closed/
    └── theories/
```

## Diferencias con praxis original

| Característica | Praxis (Desktop) | Praxis (OpenClaw) |
|----------------|------------------|-------------------|
| CLI tools | rootline, backscroll | bash, grep, glob |
| Búsqueda en historial | backscroll search | memory_search |
| Validación schema | rootline validate | Manual (lee .stem) |
| Tree view | rootline tree | bash + find |
| Persistencia | ~/.claude/ | OpenClaw workspace |
| Web search | Tool externa | kimi_search integrado |
| Sub-agentes | No disponible | sessions_spawn |

## Workflow recomendado

1. **Iniciar trabajo**: Usar `/discover` para investigación o `/roadmap` para construcción
2. **Documentar**: Los skills crean archivos .md con estructura praxis
3. **Ejecutar**: Usar `/roadmap loop` o manualmente con herramientas OpenClaw
4. **Sincronizar**: Git commit + PR al repo

## Contribuir

Esta adaptación mantiene compatibilidad upstream. Los archivos .md generados
son válidos tanto en praxis desktop como en OpenClaw.

Para mejoras:
1. Mantener compatibilidad de estructura de archivos
2. No agregar dependencias CLI que no estén en OpenClaw
3. Documentar adaptaciones específicas

## Licencia

Misma licencia que praxis original (PolyForm Noncommercial).
