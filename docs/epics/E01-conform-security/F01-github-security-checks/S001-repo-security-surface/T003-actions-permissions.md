---
titulo: "S11: Actions Permissions Scope"
estado: Pending
tipo: documentation
contribuye_a:
  - S001-repo-security-surface
---

# T003 — S11: Actions Permissions Scope

## Objetivo

Agregar check S11 al skill conform que verifica si GitHub Actions permite correr
cualquier action o está restringido a actions aprobadas.

## Archivos a modificar

- `/opt/praxis/.claude/skills/conform/SKILL.md`
- `/opt/praxis/.claude/skills/conform/checks-reference.md`

## Cambios en SKILL.md

### Tabla Security — agregar fila:
```
| S11 | Actions permissions | `gh api .../actions/permissions` allowed_actions != "all" |
```

## Cambios en checks-reference.md

Agregar sección:

```markdown
### S11: Actions permissions scoped

**Why**: `allowed_actions: "all"` means any GitHub Action (including compromised ones)
can run in your workflows. Restricting to "selected" limits the supply chain attack surface.

**Detect**:
\`\`\`bash
gh api repos/$OWNER/$REPO/actions/permissions --jq '.allowed_actions'
\`\`\`
- PASS if `"selected"` (only approved actions)
- WARN if `"all"` (unrestricted)
- SKIP if Actions not enabled

**Remediate**: Informational only. Restricting to "selected" requires configuring
an allowlist of approved actions, which is project-specific. Report as WARN with
recommendation to review.
```

## Criterios de aceptación

1. `grep -c 'S11' SKILL.md` >= 1
2. `grep -c 'S11' checks-reference.md` >= 1
3. Check detecta `allowed_actions: "all"` en homeserver como WARN
