---
titulo: Conform Security Coverage
estado: Pending
tipo: epic
---

# E01 — Conform Security Coverage

## Objetivo

Que `/conform` audite **todas** las superficies de seguridad GitHub accesibles via `gh api`,
cerrando los gaps identificados en la auditoría del 2026-03-11.

## Contexto

El skill conform cubre hardening de repositorio (S1-S8, branch protection, CodeQL, Dependabot, etc.)
pero no audita deploy keys, vulnerability alerts, Actions permissions, collaborators, ni webhooks.
Estos son vectores de ataque reales que `gh api` puede verificar.

## Postcondiciones

1. Conform reporta deploy keys con write access como WARNING
2. Conform verifica y habilita vulnerability alerts automáticamente
3. Conform reporta Actions con permissions "all" como WARNING
4. Conform lista collaborators con roles para awareness
5. Conform detecta webhooks con SSL inseguro o HTTP
