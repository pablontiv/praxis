# Loop PAOR para investigación empírica de una CAP

Guía para investigar empíricamente una capability (CAP) usando el ciclo Plan→Act→Observe→Reflect adaptado de investigación-acción, al servicio de falsación.

## Contexto

Este loop se ejecuta cuando el routing (parsing-reference.md, Ruta C) selecciona una CAP pendiente. El objetivo es responder la pregunta de falsación de esa CAP con evidencia empírica.

## PLAN — Preparar la investigación

### 1. Extraer contexto de la CAP

Del documento de investigación, leer:

- **Sub-hipótesis** (tabla "Sub-hipótesis por CAP"): forma "Si (condición) entonces (efecto) porque (mecanismo)"
- **Pregunta de falsación** (tabla "Pregunta de falsación por CAP"): "¿Es falso que...?"
- **Señales de mercado** (si existen en "Señales de mercado" o como "Ref. externa" en Matriz Premisa-Evidencia)
- **Constraints aplicables**: cruzar la CAP con la tabla "Restricciones como axiomas" en Fase 4 (si existe) o con C1-Cn + CD-01 a CD-nn
- **Dependencias**: de la tabla "CAPs con método de prueba", columna Dependencias — verificar que las dependencias estén resueltas

### 2. Formular queries de búsqueda

Generar 3-5 queries para web search:

**Query principal**: búsqueda directa del claim
- Ejemplo: `"declarative orchestration LLM retry escalation service 2025 2026"`

**Query de contraste** (OBLIGATORIA — anti-presuposiciones):
- Buscar evidencia en contra: `"problems with declarative LLM orchestration"`, `"why LLM orchestration needs custom code"`, `"limitations of X"`
- Buscar alternativas: `"X vs Y"`, `"alternatives to X"`

**Query de constraints**: búsqueda filtrada por restricciones específicas
- Ejemplo: `"LLM orchestration self-hosted private data"` (por CD-05)

**Query de estado del arte**: qué dice la industria hoy
- Ejemplo: `"state of LLM orchestration 2026"`, `"X landscape 2026"`

### 3. Presentar plan al usuario

Antes de ejecutar, mostrar:

```
PLAN DE INVESTIGACIÓN — [CAP-NN: nombre]

Sub-hipótesis: [si/entonces/porque]
Pregunta de falsación: [¿es falso que...?]
Constraints relevantes: [C/CD que aplican]

Queries formuladas:
1. [query principal]
2. [query de contraste — anti-presuposición]
3. [query de constraints]
4. [query de estado del arte]

¿Proceder o ajustar queries?
```

## ACT — Ejecutar la investigación

### 1. Web search

Ejecutar queries (WebSearch o defuddle para páginas específicas). Para cada resultado:
- Anotar fuente (URL, tipo: doc oficial / paper / blog técnico / opinión / marketing)
- Extraer claim relevante
- Clasificar: confirma sub-hipótesis / refuta / parcial / no aplica

### 2. Análisis contra constraints

Para cada hallazgo positivo, verificar contra constraints:
- ¿Funciona bajo C1-C7?
- ¿Cumple CD-01 a CD-nn aplicables?
- ¿El modelo de despliegue es compatible (self-hosted si CD-05 lo requiere)?

### 3. Vendors/herramientas (si aplica)

Si el claim empírico requiere evaluar herramientas:
- Evaluar **capacidad**, no recomendar vendor
- Usar la tabla de CAPs como criterio, no features genéricas
- Registrar: ¿cubre la CAP bajo nuestros constraints? Sí/No/Parcial

## OBSERVE — Clasificar hallazgos

### 1. Clasificación de evidencia

Para cada hallazgo, clasificar:

| Clasificación | Criterio |
|--------------|---------|
| **Confirma** | Evidencia directa de que el claim es posible bajo constraints |
| **Refuta** | Evidencia directa de que el claim es imposible o impracticable |
| **Parcial** | Evidencia de que funciona pero con gaps o limitaciones |
| **Insuficiente** | No hay evidencia clara en ninguna dirección |

### 2. Calidad de evidencia

| Calidad | Fuente |
|---------|--------|
| **Alta** | Documentación oficial, paper peer-reviewed, benchmark reproducible |
| **Media** | Blog técnico con código/ejemplo, caso de uso documentado |
| **Baja** | Opinión, marketing, claim sin evidencia |
| **Ref. externa** | Investigación ajena con constraints diferentes (usar con caveat) |

### 3. Fork-detection

Durante la investigación, si emerge un tema fuera del scope de H1:

Aplicar la pregunta diagnóstica (de bifurcación consciente):

> "¿Este hallazgo es vivencia esencial de H1 (afecta directamente si la hipótesis es verdadera o falsa), o es contexto externo / curiosidad tangencial?"

| Categoría | Acción |
|-----------|--------|
| **Vivencia esencial** | Incorporar como evidencia para esta CAP o CAP relacionada |
| **Contexto externo** | Anotar brevemente en la fila de evidencia como nota, no perseguir |
| **Curiosidad tangencial** | Registrar en Open Items del documento si merece investigación futura, no perseguir ahora |

## REFLECT — Actualizar documento

Estos pasos son **obligatorios** (coacción estructural). No se puede "saltar" a la siguiente CAP sin completarlos.

### 1. Actualizar Matriz Premisa-Evidencia

Localizar la fila correspondiente a la CAP investigada. Actualizar columnas:

- **Evidencia**: resumen de hallazgos (1-2 líneas con lo sustancial)
- **Calidad**: Alta / Media / Baja / Ref. externa
- **Estado**: ✅ true / ❌ false / ⚠️ parcial / ❓ unknown (si evidencia insuficiente)

### 2. Actualizar Matriz de trazabilidad

Localizar la fila correspondiente a la CAP. Actualizar columnas:

- **Fase actual**: 3 (si se resuelve en investigación) o mantener 2 (si sigue pendiente)
- **Resultado**: descripción breve del hallazgo
- **Confianza**: Alta / Media / Baja
- **Decisión**: Go / Pivot / Stop / pendiente

### 3. Actualizar header del documento

Actualizar la línea `> Estado:` para reflejar progreso:

```
> Estado: Fase 3 en curso (N/M CAPs investigadas). Fases 4-5 en construcción.
```

### 4. Evaluar impacto en H1

**Si la CAP resulta ❌ false**:
- ¿Es CAP Crítica? → Si sí, evaluar: ¿H1 es falsada?
- ¿Hay mitigación posible? (Pivot: el claim falla pero hay alternativa bajo constraints)
- Presentar evaluación al usuario:

```
⚠ CAP-NN REFUTADA: [nombre]

Evidencia: [resumen]
Impacto en H1: [directo/indirecto]

OPCIONES:
├─ PIVOT: [descripción de alternativa si existe]
├─ STOP: H1 falsada — nueva investigación necesaria
└─ CONTINUAR: Investigar más antes de decidir

¿Qué decides?
```

**Si la CAP resulta ⚠️ parcial**:
- Documentar qué falta para completar
- ¿Es alcanzable con más investigación o requiere spike empírico (Fase 4)?

**Si la CAP resulta ✅ true**:
- Documentar evidencia y avanzar

### 5. Punto de reflexión

Después de actualizar, evaluar el estado global:

- ¿La evidencia acumulada (todas las CAPs resueltas hasta ahora) sigue apuntando a Go?
- ¿Algún hallazgo de esta CAP cambió la comprensión de otra CAP?
- ¿Hay suficiente información para tomar decisión Go/Pivot/Stop, o seguir investigando?

Presentar:

```
REFLEXIÓN POST-CAP

CAPs resueltas: N/M
├─ ✅ true:  N
├─ ⚠️ parcial: N
├─ ❌ false: N

Tendencia: [hacia Go / señales de Pivot / riesgo de Stop]

¿Continuar con siguiente CAP o evaluar decisión ahora?
```

### 6. Siguiente paso

Si el usuario elige continuar → volver al routing (parsing-reference.md, Paso 4, Ruta C) para seleccionar la siguiente CAP.

Si el usuario elige parar → dejar el documento actualizado con todo lo investigado hasta el momento. El progreso no se pierde.
