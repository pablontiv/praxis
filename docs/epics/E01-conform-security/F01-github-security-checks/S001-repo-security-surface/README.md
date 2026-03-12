---
titulo: Repo Security Surface Audit
estado: Pending
tipo: story
cubre:
  - F01-github-security-checks
---

# S001 — Repo Security Surface Audit

## Capacidad

Conform audita deploy keys, vulnerability alerts, Actions permissions, collaborators,
y webhooks de cualquier repo GitHub, reportando hallazgos en el formato estándar del skill.

## Cliente

Platform Owner (pablontiv)

## Alcance

**In**: Checks S9-S13 en SKILL.md y checks-reference.md
**Out**: Account-level security (2FA, sessions, PATs — no accesible via repo API)

## Estado inicial

- Conform tiene checks S1-S8
- APIs verificadas: keys, vulnerability-alerts, actions/permissions, collaborators, hooks

## Resultado esperado

- `/conform --audit-only --component security` reporta S9-S13 en cualquier repo
- S10 (vulnerability alerts) es auto-fixeable
- S9, S11, S12, S13 son informativos

## Criterios de aceptación

1. `grep -c 'S[0-9]' checks-reference.md` retorna 13 (S1-S13)
2. `/conform --audit-only --component security` en homeserver muestra S9 WARN (deploy key write)
3. `/conform --audit-only --component security` en homeserver muestra S10 FAIL (vuln alerts disabled)
