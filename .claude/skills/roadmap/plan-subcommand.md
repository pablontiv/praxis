# /roadmap plan

Tomar el plan de la conversacion actual y descomponerlo en estructura de roadmap.

**Cuando usar**: Despues de que una sesion produce un plan tecnico (investigacion, analisis, fix propuesto, etc.) y se quiere estructurar como roadmap.

**Fuente del plan** (orden de prioridad):
1. Contexto de la conversacion actual (preferido)
2. Fallback: plan file de `~/.claude/plans/${CLAUDE_SESSION_ID}.md`
   (plan files son globales — usar `${CLAUDE_SESSION_ID}` para garantizar que sea de esta sesion)

## Fase 1: Descomposicion

1. Identificar el plan mas reciente:
   a. Buscar en el contexto de conversacion actual (plan tecnico, analisis, propuesta, etc.)
   b. Si la conversacion fue compactada o no tiene plan visible → leer plan file de
      `~/.claude/plans/${CLAUDE_SESSION_ID}.md`
   c. Si no hay plan en ninguna fuente → informar: "No hay plan en esta conversacion.
      Primero investigar/planificar, luego ejecutar `/roadmap plan`." → STOP
3. Absorber contexto: leer documentacion existente del area afectada en `<roadmap-root>/`
4. Aplicar framework de descomposicion (mismos criterios que Modo Autonomo):
   - Leer [framework-reference.md](framework-reference.md)
   - Criterios de escala: 3-5 Features/Epic, 1-4 Stories/Feature, 1-5 Tasks/Story
   - Constraint Map (postcondiciones + invariantes)
   - Validacion de completitud (Paso 4.5 del Modo Autonomo en [autonomous-mode.md](autonomous-mode.md))
5. **OBLIGATORIO**: Descomposicion DEBE llegar hasta nivel Task para TODOS los Stories.
   Cada Task con: nombre, tipo, descripcion de 1 linea.

## Fase 2: Presentacion para aprobacion

6. Presentar arbol jerarquico completo + Constraint Map
7. Pedir aprobacion con `AskUserQuestion` (NO usar `ExitPlanMode` — ese es para plan mode
   del sistema, no para aprobaciones internas de un skill)
8. **STOP y esperar aprobacion. NO crear archivos sin aprobacion.**

## Fase 3: Materializacion (post-aprobacion)

**MATERIALIZAR ≠ IMPLEMENTAR.** En esta fase se crean SOLAMENTE archivos `.md` del roadmap
dentro de `<roadmap-root>/` (Feature READMEs, Story READMEs, Task .md files).
Estos archivos DESCRIBEN el trabajo a realizar — NO lo ejecutan.
NUNCA escribir codigo, scripts, configs, hooks, ni ningun archivo fuera de `<roadmap-root>/`.
La implementacion ocurre despues via `/roadmap loop`.

9. Para cada nivel de la jerarquia (Epic, Feature, Story, Task), crear archivos .md usando los templates de:
   - [epic-guide.md](epic-guide.md) para READMEs de Epic y Feature
   - [story-guide.md](story-guide.md) para READMEs de Story
   - [task-guide.md](task-guide.md) para archivos de Task
10. Despues de cada Write, ejecutar `rootline validate <path>`
11. Si falla, `rootline fix <path>` como fallback
12. Actualizar tablas en READMEs padre (cascading links)
13. **Validacion batch final**: Ejecutar `rootline validate --all <roadmap-root>/`
   - Si hay errores → `rootline fix --all <roadmap-root>/`
   - Reportar resultado final al usuario
14. **Commit+Push** archivos de planificacion creados:
   - `git add` todos los archivos .md creados (especificos, no `git add .`)
   - `git commit` con mensaje: `chore(roadmap): create {descripcion breve} planning docs`
   - `git push`

**STOP OBLIGATORIO**: Despues de commit+push, DETENERSE COMPLETAMENTE.
Informar: "Archivos de planificacion creados. Ejecutar `/roadmap loop` cuando este listo
para implementar."
NO continuar. NO invocar `/roadmap loop`. NO leer tasks para implementar.
NO escribir archivos de implementacion (codigo, scripts, configs, hooks, units, etc.).
