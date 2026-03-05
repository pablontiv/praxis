# Praxis — Framework de Investigación y Planificación

## Contexto del Sistema

Framework portable de investigación estructurada y planificación para Claude Code. Transforma señales crudas en conocimiento validado y acción concreta a través de fases de reducción de incertidumbre.

**Estado actual:** Ver `.claude/rules/current-state.md` (si existe)
**Conexiones:** Ver `.claude/rules/connections.md` (si existe)
**Reglas operativas:** Ver `.claude/rules/praxis-pipeline.md`

## Skills Disponibles

| Skill | Descripción |
|-------|-------------|
| `/praxis [input]` | Proxy inteligente: reconocimiento del entorno, detección de fase, delegación al skill correcto |
| `/discover [sub]` | R&D: init, new-line, cycle, reflect, theory, status, update-map, interlink, review-patterns, research, @file |
| `/hypothesize [tema]` | Investigación estructurada de 5 fases con trazabilidad lógica |
| `/roadmap [args]` | Planificación AI-native: epics → features → stories → tasks |
| `/sessions [keyword]` | Buscar en historial de sesiones de Claude Code |

## Agents Disponibles

- **grounded-theory-analyst**: Análisis GT (Glaser & Strauss). Read-only. Para datos cualitativos sin estructura previa.
- **sdd-validator**: Valida cadena de trazabilidad del roadmap (Epic→Feature→Story→Task).

## Dependencias Externas

- **`rootline` CLI**: Requerida por `/roadmap` (todos los subcomandos). Verificar con `command -v rootline` antes de ejecutar cualquier operación de roadmap. Si no está instalada → informar al usuario con instrucciones de instalación y **parar**. No simular rootline con lecturas manuales de archivos.

## Reglas de Edición

- **Skills**: Siempre editar en `.claude/skills/` del repo. NUNCA editar `~/.claude/skills/` — el pre-push hook sobrescribe ese directorio con la versión del repo en cada push.

## Comportamiento de Claude

- **Al iniciar sesión**: Ejecutar `/praxis` si existe MAP.md
- **Al explorar ideas**: Guiar con preguntas socráticas, no dar respuestas directas
- **Al detectar divergencia**: Activar fork-detector (integrado en `/discover`)
- **Al documentar**: Insistir en documentar en bitácora (FIELD-LOG.md)
- **Al reflexionar**: Buscar patrones, conexiones, teoría emergente

## Metodología de Investigación Empírica

Cuando se ejecutan tasks de investigación empírica (tipo `research-document`, `spike`, `evaluation`):

1. **Cada task = 1 entregable concreto** ejecutable por una persona externa sin conocer el framework lógico interno
2. **Lenguaje natural, no técnico**: "investigar qué plataformas ofrecen X", no "evaluar CAP-07 contra checklist de M6/M10"
3. **Incremental y descubrible**: solo crear tasks que sabemos necesitar AHORA — las siguientes emergen de los resultados
4. **1 task = 1 scope acotado**: no "probar 10 plataformas" sino "buscar qué plataformas existen" → luego "probar si la plataforma X funciona con Y"
5. **Cada task actualiza el documento de investigación fuente**: el entregable siempre es una actualización de la matriz de evidencia (falsear o validar cada premisa empírica)

**Anti-patrones**:
- Tasks que referencian IDs internos del framework (CAP-07, M6, CD-04) sin contexto humano
- Pre-planificar tasks que dependen de resultados desconocidos
- Tasks que cubren demasiado scope ("investigar y evaluar 10 plataformas")
- Separar "emitir veredicto" como task aislado — es parte natural del cierre de cada investigación

## Flujo del Sistema

```
/praxis [input] → /discover → /hypothesize → /roadmap → implement
```

Use `/praxis` como punto de entrada único. Reconoce el entorno, detecta la fase del input, y delega al skill correcto. Reinvocable sobre el mismo documento conforme avanza por las fases.

Cada fase es independiente pero se alimentan entre sí. No es obligatorio seguir el orden.
