---
titulo: GitHub Security Checks
estado: Pending
tipo: feature
satisface:
  - E01-conform-security
---

# F01 — GitHub Security Checks

## Descripción

5 checks nuevos (S9-S13) en la sección Security del skill conform.
Cada check usa `gh api` para auditar una superficie de seguridad a nivel repositorio.

## Checks

| Check | Superficie | Auto-fix |
|-------|-----------|----------|
| S9 | Deploy keys | No |
| S10 | Vulnerability alerts | Sí |
| S11 | Actions permissions | No |
| S12 | Collaborators | No |
| S13 | Webhooks | No |
