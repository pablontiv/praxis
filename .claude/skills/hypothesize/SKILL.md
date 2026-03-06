---
name: hypothesize
description: |
  Investigación estructurada de 5 fases con trazabilidad lógica para falsear
  claims, evaluar propuestas técnicas, y decidir Go/No-Go con evidencia.
  Tres modos: (1) CREAR nueva investigación desde un tema, (2) DIRECTO
  analizar claims/propuestas inline, (3) SEGUIMIENTO continuar un documento
  de investigación .md existente.
  Use when the user says "formular hipótesis", "hypothesize", "falsación",
  "falsear", "investigación estructurada", "5 fases", "Go/No-Go",
  "evaluar si vale la pena", "analizar claims", "decidir con evidencia".
  Also trigger when the user presents a proposal with claims to evaluate
  before committing resources, questions whether a migration/rewrite/adoption
  is worth it, references an existing research document (.md) to continue,
  or needs structured evidence to support a build-vs-buy decision.
user-invocable: true
argument-hint: "[tema-corto] o [archivo-existente.md] o [contenido con claims a falsar]"
---

# Routing: detectar modo de operación

Determinar qué modo aplicar según la entrada del usuario (ver ARGUMENTS al final):

1. ¿Es un path a un archivo `.md` que existe en el working directory?
   - **SÍ** → **MODO SEGUIMIENTO** (ir a "Seguimiento de investigación existente")

2. ¿Es un tema corto (1-5 palabras, sin estructura ni claims detallados)?
   - **SÍ** → **MODO CREAR** (ir a "Crear investigación nueva" — flujo interactivo desde Paso 0)

3. ¿Contiene contenido sustancial (párrafos, claims, propuestas, recomendaciones, análisis)?
   - **SÍ** → **MODO DIRECTO** (ir a "Investigación directa desde contenido")

---

# MODO CREAR — Nueva investigación

Vas a conducir una investigación estructurada sobre **el tema indicado por el usuario** usando el flujo de 5 fases. El resultado es un documento markdown con trazabilidad lógica completa.

El modelo es de hipótesis única (H1) con sub-hipótesis por capability (CAP).

## PRINCIPIOS OBLIGATORIOS

1. **Exploración antes de ejecución**: SIEMPRE preguntar antes de asumir. No inventar constraints ni decisiones.
2. **Análisis de falacias**: en cada afirmación del usuario, buscar ambigüedades, falsos dilemas, non sequiturs, equivocaciones semánticas. Resolverlas antes de avanzar.
3. **Track único con método**: cada claim se clasifica como lógico, empírico o mixto. No hay dual-track.
4. **Falsabilidad**: toda hipótesis debe poder ser falsa. Si no puede falsarse, no es hipótesis — es supuesto o axioma.
5. **Nada se pierde**: todo ID (C, D, M, INV, CD, TV, F, H, CAP, OI, R, S, T) debe ser trazable en el documento final.
6. **Tablas de verdad**: cuando haya variables booleanas interdependientes, construir tabla de verdad para validar consistencia.

## FLUJO DE INTERACCIÓN

### Paso 0: Contexto inicial

Pregunta al usuario:
- ¿Qué quieres investigar y por qué?
- ¿Qué ya sabes (hechos, restricciones, decisiones tomadas)?
- ¿Existe documentación previa o referencias externas?
- ¿Cuál es el resultado esperado de la investigación?

NO generes nada hasta tener respuestas. Si las respuestas son ambiguas, pregunta más.

### Paso 0.5: Anti-presuposiciones

Después de recibir las respuestas del usuario y ANTES de formular C/D/M:

1. **Detectar presuposiciones** en la formulación del usuario:
   - ¿Qué verbos presuponen estructura? (componentes, arquitectura, funciona, mejora)
   - ¿Qué categorías se asumen existentes?
   - ¿Qué expectativas implícitas hay?

2. **Proponer reformulación observacional** si se detectan presuposiciones significativas:

   | Presupone | Observacional |
   |-----------|--------------|
   | "¿Qué componentes tiene?" | "¿Qué encuentro cuando examino...?" |
   | "¿Cómo funciona X?" | "¿Qué observo que pasa cuando...?" |
   | "¿Por qué X mejora Y?" | "¿Qué cambia con/sin X?" |

3. **Documentar presuposiciones explícitas** — se integrarán como S1-Sn en Fase 1.

4. **Confirmar con usuario** antes de proceder.

### Paso 1: Fase 1 — Idea → Tesis (interactiva)

Construye iterativamente con el usuario:

1. **Extraer axiomas del entorno (C1-Cn)**: realidades que no se pueden cambiar. Pregunta: "¿Qué restricciones del entorno son inamovibles?" Para cada respuesta, busca ambigüedades y aclara.
2. **Extraer premisas de diseño (D1-Dn)**: decisiones del usuario. No negociables. Pregunta: "¿Qué decisiones ya tomaste que no están en discusión?"
3. **Extraer modelo deseado (M1-Mn)**: lo que se quiere lograr. Pregunta: "¿Qué capacidades necesitas que el sistema tenga?"
4. **Análisis de falacias (F1-Fn)**: revisa C+D+M buscando contradicciones, ambigüedades semánticas, falsos dilemas, non sequiturs. Presenta cada una al usuario para resolución.
5. **Tablas de verdad (TV-01+)**: si hay variables booleanas interdependientes, construir tabla para validar consistencia del sistema.
6. **Proposición central (P)**: formula como: "Existe [solución tipo] que [logra M1-Mn] bajo [C1-Cn] respetando [D1-Dn], sin [condición de falsación]."
7. **Mapa de inferencias**: árbol ASCII mostrando cómo C+D+M llevan a P. Marcar huecos de evidencia con ⚠.
8. **Supuestos explícitos (S1-Sn)**: extraer de C+D+M todo lo que NO es hecho verificado. Incluir las presuposiciones del Paso 0.5.

Cuando Fase 1 esté completa, pregunta al usuario si valida antes de continuar.

### Paso 2: Fase 2 — Tesis → Plan de investigación (derivada)

Derivar de Fase 1:

1. **Hipótesis testable H1**: formulación macro con condición de falsación explícita.
2. **Capabilities mínimas (CAP-01 a CAP-nn)**: capacidades necesarias para que H1 sea verdadera.
3. **Sub-hipótesis (H1-a a H1-n)**: una por CAP, forma: "Si (condición) entonces (efecto medible) porque (mecanismo)."
4. **Preguntas de falsación**: una por CAP, forma: "¿Es falso que [claim]?"
5. **CAPs expandidas**: tabla con columnas: ID | Capability | Método (lógico/empírico/mixto) | Dependencias | Prioridad | Crítica?
6. **Criterios de decisión**: definir umbrales Go/Pivot/Stop con definiciones de "pegamento" vs "servicio core".
7. **Reglas de parada (R1-Rn)**: invariantes de terminación para flujos iterativos.

Si hay señales de mercado de investigaciones externas, incluir sección "Señales de mercado (referencia externa)" con caveat explícito de constraints distintos.

### Paso 3: Fase 3 — Investigación → Argumento actualizado

Poblar con evidencia disponible:

1. **Invariantes (INV-01 a INV-nn)**: reglas que deben ser siempre ciertas. Derivar de C+D+M.
2. **Constraints derivados (CD-01 a CD-nn)**: consecuencias lógicas inevitables de C+D+M.
3. **Matriz Premisa-Evidencia**: tabla con columnas: Premisa | Método | Evidencia | Calidad | Estado (✅ true / ❌ false / ❓ unknown / ⚠️ parcial).
4. **Registro de incertidumbre**: lo que sigue "unknown" o "parcial" + impacto si resulta falso + severidad.
5. **Conclusión provisional**: dado la evidencia E1..Ek, ¿es razonable invertir en investigación empírica? Identificar cuello de botella.

### Paso 4: Fases 4-5 — Esqueletos con placeholders

**Fase 4: Argumento → Factibilidad**
- Restricciones como axiomas (referenciar C+CD, no duplicar)
- Claims técnicos (T-01 a T-nn): tabla con Claim | CAP | Spike necesario | Resultado | Estado
- Matriz riesgos vs mitigaciones: tabla con Riesgo | Premisa frágil | Impacto | Mitigación
- Regla Go/No-Go: condición formal para construir prototipo

**Fase 5: Factibilidad → Prototipo**
- Teorema de valor: qué demuestra y qué NO
- Especificación mínima: entradas, salidas, APIs, límites
- Instrumentación y métricas: tabla con Métrica | Cómo se mide | Umbral éxito | Umbral fallo
- Reporte de resultados: tabla con Claim | Validado | Refutado | Observaciones | Siguiente paso

### Paso 5: Matriz de trazabilidad transversal

Al final del documento. Tabla maestra:

| Claim | CAP | Fase actual | Método | Resultado | Confianza | Decisión |

Una fila por CAP. Poblar con lo conocido hasta el momento.

## ESTRUCTURA DEL DOCUMENTO DE SALIDA

```markdown
# [Tema] — Investigación Estructurada
> Estado: Fase N [estado]. Fases N+1 a 5 en construcción.

---
## Glosario de dominio
| Termino | Definicion |

---
## Fase 1: Idea → Tesis
### Anti-presuposiciones — si aplica
### Proposición central (P)
### Axiomas del entorno [ESTADO]
### Premisas de diseño [ESTADO]
### Modelo deseado [ESTADO]
### Flujo de autoridad
### Mapeo contra [referencia] — si aplica
### Clarificaciones (falacias resueltas)
### Mapa de inferencias
### Supuestos explícitos

---
## Fase 2: Tesis → Plan de investigación
### Preguntas de falsación
### Hipótesis testables (H1 + sub-hipótesis)
### CAPs con método de prueba
### Señales de mercado (referencia externa) — si aplica
### Criterios de decisión
### Reglas de parada

---
## Fase 3: Investigación → Argumento actualizado
### Matriz Premisa-Evidencia
### Evidencia lógica: Invariantes
### Evidencia lógica: Constraints derivados
### Evidencia lógica: Tablas de verdad — si aplica
### Registro de incertidumbre
### Conclusión provisional

---
## Fase 4: Argumento → Factibilidad
### Restricciones como axiomas
### Claims técnicos (T1-Tn)
### Matriz riesgos vs mitigaciones
### Regla Go/No-Go

---
## Fase 5: Factibilidad → Prototipo
### Teorema de valor
### Especificación mínima
### Instrumentación y métricas
### Reporte de resultados

---
## Pieza transversal: Matriz de trazabilidad
```

## CHECKLIST DE VERIFICACIÓN (antes de entregar)

- [ ] Todo ID existente (C, D, M, INV, CD, TV, F, H, CAP, S, R) aparece en el documento — nada se pierde
- [ ] La matriz de trazabilidad tiene una fila por cada CAP
- [ ] Cada CAP tiene sub-hipótesis (si/entonces/porque) y pregunta de falsación
- [ ] La Matriz Premisa-Evidencia clasifica toda evidencia con estado (true/false/unknown/parcial)
- [ ] Fases 4 y 5 tienen placeholders con estructura de tabla (no secciones vacías)
- [ ] Las falacias detectadas están resueltas o migradas como preguntas de falsación
- [ ] Los supuestos explícitos están separados de los hechos verificados
- [ ] El mapa de inferencias marca huecos de evidencia con ⚠

---

# MODO DIRECTO — Investigación desde contenido proporcionado

El usuario proporcionó contenido sustancial (propuestas, recomendaciones, claims técnicos, análisis). Este contenido ES el material a investigar — no preguntar "qué quieres investigar".

## Procedimiento

### Paso 0: OMITIDO
El contexto ya está en los ARGUMENTS. Extraer directamente del contenido proporcionado.

### Paso 0.5: Anti-presuposiciones (aplicar al contenido recibido)

1. **Extraer claims** del contenido como proposiciones explícitas (C1, C2, ...). Para cada claim:
   - ¿Asume que algo funciona sin evidencia?
   - ¿Presupone necesidad sin validar?
   - ¿Qué categorías se dan por existentes?

2. **Proponer reformulación observacional** para claims con presuposiciones significativas

3. **Presentar al usuario**:
   - Lista de claims extraídos
   - Presuposiciones detectadas
   - Reformulaciones propuestas

4. **Confirmar con usuario** antes de proceder

### Continuar con Paso 1 en adelante

Usar los claims extraídos como base para construir C/D/M y seguir el flujo normal de las 5 fases. Los PRINCIPIOS OBLIGATORIOS y el FLUJO DE INTERACCIÓN de MODO CREAR aplican desde Paso 1.

---

# MODO SEGUIMIENTO — Investigación existente

El archivo indicado es una investigación existente. Leer el documento, detectar estado, y actuar.

## Procedimiento

Seguir la guía de parseo en `parsing-reference.md`:

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

Cuando el routing selecciona una CAP pendiente, ejecutar el loop PAOR descrito en `empirical-loop.md`:

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
