# Praxis — Reglas Operativas

## Flujo del Sistema

```
/praxis [input] → /discover → /hypothesize → /roadmap → implement
```

0. **Praxis** (`/praxis`): Reconocimiento del entorno, detección de fase, delegación al skill correcto.
1. **Discover**: Exploración abierta. Líneas de investigación con ciclos PAOR.
2. **Hypothesize**: Investigación estructurada de 5 fases con trazabilidad lógica.
3. **Roadmap**: Descomposición en epics, features, stories, tasks.
4. **Implement**: Ejecución de tasks (ciclo normal de desarrollo).

No es obligatorio seguir el flujo completo. Cada skill es independiente. El flujo es una guía, no un pipeline rígido.

## Límites Operativos

- **Líneas activas**: máximo 2-3 simultáneas (exploración sin dispersión)
- **Construcciones activas**: máximo 1 (foco profundo)
- **Regla de oro**: documentar mientras se hace, no después

## Principios

- **Coacción estructural**: mejor que el proceso fuerce el comportamiento, no la voluntad
- **Anti-presuposiciones**: reformular preguntas en forma observacional antes de investigar
- **Bifurcación consciente**: cuando una línea diverge, el fork-detector lo señala
- **Fases, no cierres**: cuando una línea produce un artefacto, cambia de fase — no termina
- **Separación framework/datos**: la disciplina es portable (skills), el conocimiento es local (proyecto)

## Skills Disponibles

| Skill | Propósito |
|-------|-----------|
| `/praxis [input]` | Proxy: reconocimiento, detección de fase, delegación |
| `/discover [subcommand]` | Indagación: init, new-line, cycle, reflect, theory, status, update-map, interlink, review-patterns, research, @file |
| `/hypothesize [tema\|archivo]` | Investigación estructurada de 5 fases |
| `/roadmap [args]` | Planificación: descomponer en epics/features/stories/tasks |
