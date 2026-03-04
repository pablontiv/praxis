# Referencia de parseo — Documento de investigación

Guía para leer el estado de un documento de investigación estructurada y determinar qué acción tomar.

## Paso 1: Determinar si la entrada del usuario es archivo o tema nuevo

- Si la entrada del usuario (sección ARGUMENTS al final del prompt) termina en `.md` y el archivo existe → **MODO SEGUIMIENTO**
- Si no → **MODO CREAR** (flujo de 5 fases del SKILL.md principal)

## Paso 2: Parsear el documento

Leer el archivo completo y extraer:

### 2a. Header de estado

Buscar la línea que comienza con `> Estado:`. Formato esperado:

```
> Estado: Fase N [estado]. Fases N+1 a 5 en construcción.
```

Extraer:
- **Fase actual**: el número N
- **Estado de la fase**: texto entre corchetes (validada, en construcción, etc.)

### 2b. Fases completadas

Verificar existencia y contenido de cada sección `## Fase N`:

| Sección | Señal de completitud |
|---------|---------------------|
| Fase 1 | Tiene P formulada + C1-Cn + D1-Dn + M1-Mn + Mapa de inferencias |
| Fase 2 | Tiene H1 + CAPs con tabla + Sub-hipótesis + Preguntas de falsación |
| Fase 3 | Tiene Matriz Premisa-Evidencia poblada + INV + CD |
| Fase 4 | Tiene claims T-01..T-nn con Resultado (no solo "—") |
| Fase 5 | Tiene Reporte de resultados poblado |

Fase incompleta = sección existe pero tiene placeholders vacíos ("—") o falta contenido estructural.

### 2c. Matriz Premisa-Evidencia

Buscar la tabla bajo `### Matriz Premisa-Evidencia`. Para cada fila, extraer la columna **Estado**:

| Símbolo | Significado | Conteo |
|---------|-------------|--------|
| ✅ true | Evidencia confirma | Contar |
| ⚠️ parcial | Evidencia parcial | Contar |
| ❓ unknown | Sin evidencia | Contar |
| ❌ false | Evidencia refuta | Contar |

**Total claims** = suma de todas las filas.
**Claims resueltos** = filas con ✅ true o ❌ false.

### 2d. CAPs pendientes

Buscar la tabla bajo `### CAPs con método de prueba`. Para cada CAP:
1. Cruzar con la Matriz Premisa-Evidencia para obtener estado actual
2. Extraer columna **Prioridad** y **Critica?**
3. Extraer columna **Dependencias**

Clasificar:
- **Pendientes**: estado ❓ unknown o ⚠️ parcial
- **Resueltas**: estado ✅ true o ❌ false
- **Cuello de botella**: pendiente + Critica = Sí

### 2e. Matriz de trazabilidad

Buscar tabla bajo `## Pieza transversal: Matriz de trazabilidad`. Para cada fila:
- Extraer columna **Decisión** (vacía = pendiente)
- Extraer columna **Confianza**
- Extraer columna **Fase actual**

### 2f. Claims técnicos (si Fase 4 existe)

Buscar tabla bajo `### Claims técnicos`. Para cada fila:
- Extraer columna **Resultado** ("—" = pendiente)
- Extraer columna **Estado**

## Paso 3: Renderizar progreso

Siempre mostrar PRIMERO el estado visual antes de proponer acción:

```
PROGRESO — [Título del documento (línea 1 sin #)]
═══════════════════════════════════════════════════

Fases:  [barra] N/5 completadas
Claims: [barra] N/M resueltos

EVIDENCIA
├─ ✅ true:    N
├─ ⚠️ parcial: N
├─ ❓ unknown: N
└─ ❌ false:   N
```

Barra de progreso: usar █ para completado, ░ para pendiente. 10 caracteres de ancho.

Ejemplo: 3/5 fases → `██████░░░░`

## Paso 4: Routing por estado detectado

Evaluar en este orden (primera coincidencia gana):

### Ruta A: Fase 1 incompleta

**Condición**: Falta P, o faltan C/D/M, o mapa de inferencias ausente.

**Acción**:
```
SIGUIENTE PASO: Completar Fase 1 (Idea → Tesis)
Faltan: [listar elementos faltantes]
```
→ Retomar flujo interactivo de Fase 1 (Paso 1 del SKILL.md principal).

### Ruta B: Fase 2 incompleta

**Condición**: Fase 1 completa pero no hay H1, o no hay CAPs, o no hay preguntas de falsación.

**Acción**:
```
SIGUIENTE PASO: Derivar plan de investigación (Fase 2)
Fase 1 completa. Derivar H1, CAPs, sub-hipótesis y preguntas de falsación.
```
→ Ejecutar Paso 2 del SKILL.md principal.

### Ruta C: CAPs pendientes en Fase 3

**Condición**: Fase 2 completa y existen CAPs con estado ❓ unknown o ⚠️ parcial.

**Acción**: Mostrar árbol de decisión:

```
INVESTIGACIÓN PENDIENTE — N/M CAPs resueltas
│
├─► [CAP con mayor prioridad o Crítica]  [estado, prioridad — razón]
├─► [siguiente CAP]                       [estado, prioridad]
└─► ...

CRITERIOS DE DECISIÓN
├─ ¿Hay CAP Crítica sin resolver?
│  └─ SÍ → Investigar primero (fail-fast: si cae, H1 es falsa)
├─ ¿Hay CAP parcial completable?
│  └─ SÍ → Completar la parcial (menos esfuerzo → más progreso)
└─ ¿Hay dependencias entre CAPs?
   └─ SÍ → Resolver bloqueante primero

SUGERENCIA: Investigar [CAP-NN] — [razón]
¿Proceder con esta CAP o elegir otra?
```

→ Una vez seleccionada, ejecutar loop PAOR (ver empirical-loop.md).

### Ruta D: Fase 3 completa → transición a Fase 4

**Condición**: Todas las CAPs tienen estado ✅ o ❌ (ninguna ❓/⚠️).

**Acción**:
- Evaluar criterios Go/Pivot/Stop (de la sección "Criterios de decisión" del documento)
- Contar CAPs ❌ false y evaluar impacto
- Presentar evaluación:

```
EVALUACIÓN — Todas las CAPs investigadas

✅ true:  N CAPs confirmadas
❌ false: N CAPs refutadas
  [listar CAPs false y su impacto en H1]

DECISIÓN SEGÚN CRITERIOS:
[Go / Pivot / Stop — con justificación basada en los umbrales definidos]
```

Si Go → poblar Fase 4 (claims técnicos T-01..T-nn desde resultados de CAPs).

### Ruta E: Fase 4 incompleta

**Condición**: Claims técnicos T-nn existen pero tienen Resultado "—".

**Acción**:
```
FACTIBILIDAD — N/M claims técnicos validados

PENDIENTES:
├─► T-NN: [claim]  [spike necesario]
└─► ...

SIGUIENTE: Ejecutar spike para T-NN
```

### Ruta F: Fase 4 completa → Go/No-Go

**Condición**: Todos los T-nn tienen resultado.

**Acción**: Evaluar regla Go/No-Go del documento.
- Si Go → transicionar a Fase 5 (especificación de prototipo)
- Si No-Go → presentar qué claims fallaron y por qué

### Ruta G: Investigación completa

**Condición**: Fase 5 tiene reporte de resultados poblado.

**Acción**:
```
INVESTIGACIÓN COMPLETA — [Tema]

Decisión final: [Go/Pivot/Stop]
Confianza: [Alta/Media/Baja]

RESUMEN DE TRAZABILIDAD:
[tabla condensada de la Matriz de trazabilidad]
```
