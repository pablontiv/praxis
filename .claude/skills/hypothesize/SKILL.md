---
name: hypothesize
description: |
  Use when the user needs to make a decision backed by evidence — evaluating
  whether a technology, migration, architecture change, or vendor is worth
  adopting BEFORE committing resources. This skill structures claims into
  falsifiable hypotheses, gathers evidence for/against each, and produces
  a Go/No-Go verdict.
  Three modes: (1) CREAR — new investigation from a topic or proposal,
  (2) DIRECTO — analyze claims/proposals inline, (3) SEGUIMIENTO — continue
  an existing .md investigation document.
  Trigger when the user: presents a proposal with claims to evaluate ("should
  we migrate to X?", "is Y worth it?"), wants to decide build-vs-buy with
  evidence, needs to falsify specific technical claims before a commitment,
  questions whether a rewrite/migration/adoption makes sense, or references
  an existing investigation document to continue.
  Trigger phrases: "hypothesize", "falsear", "Go/No-Go", "evaluar si vale",
  "decidir con evidencia", "analizar claims", "investigacion estructurada".
  DO NOT use for open-ended exploration without specific claims (that's
  discover) or for breaking approved plans into tasks (that's roadmap).
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

## Ejecución por modo

Una vez determinado el modo, leer el archivo correspondiente y seguir sus instrucciones:

| Modo | Archivo | Cuándo |
|------|---------|--------|
| CREAR | [crear-mode.md](crear-mode.md) | Tema corto → flujo interactivo de 5 fases |
| DIRECTO | [directo-mode.md](directo-mode.md) | Contenido sustancial → extraer claims y analizar |
| SEGUIMIENTO | [seguimiento-mode.md](seguimiento-mode.md) | Archivo .md existente → parsear estado y continuar |
