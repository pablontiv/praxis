# MODO SEGUIMIENTO — Investigación existente

El archivo indicado es una investigación existente. Leer el documento, detectar estado, y actuar.

## Procedimiento

Seguir la guía de parseo en [parsing-reference.md](parsing-reference.md):

1. **Leer el documento completo**
2. **Parsear estado** (header, fases, Matriz Premisa-Evidencia, CAPs, trazabilidad)
3. **Renderizar progreso** (siempre mostrar primero)
4. **Routing automático** — la primera ruta que coincida:

| Condición | Acción |
|-----------|--------|
| Fase 1 incompleta | Continuar construcción de tesis |
| Fase 2 incompleta | Derivar plan de investigación |
| Fase 3 tiene CAPs ❓/⚠️ | Mostrar árbol de decisión → seleccionar CAP → loop empírico |
| Fase 3 completa | Evaluar Go/Pivot/Stop → transicionar a Fase 4 |
| Fase 4 incompleta | Mostrar claims técnicos pendientes → ejecutar spikes |
| Fase 4 completa | Evaluar regla Go/No-Go → transicionar a Fase 5 |
| Investigación completa | Mostrar resumen final |

## Investigación empírica de CAPs

Cuando el routing selecciona una CAP pendiente, ejecutar el loop PAOR descrito en [empirical-loop.md](empirical-loop.md):

**PLAN** → preparar queries con anti-presuposiciones
**ACT** → web search + análisis contra constraints
**OBSERVE** → clasificar evidencia + fork-detection
**REFLECT** → actualizar documento (OBLIGATORIO: matrices + header + evaluación de impacto en H1)

### Actualizaciones obligatorias post-CAP (coacción estructural)

Después de investigar cada CAP, SIEMPRE:
1. Actualizar fila en Matriz Premisa-Evidencia
2. Actualizar fila en Matriz de trazabilidad
3. Actualizar header `> Estado:` del documento
4. Si ❌ false → evaluar impacto en H1
5. Mostrar reflexión post-CAP con tendencia Go/Pivot/Stop
