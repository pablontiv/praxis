---
titulo: "S12: Collaborator Audit"
estado: Pending
tipo: documentation
contribuye_a:
  - S001-repo-security-surface
---

# T004 — S12: Collaborator Audit

## Objetivo

Agregar check S12 al skill conform que lista collaborators de un repo
y detecta permisos excesivos.

## Archivos a modificar

- `/opt/praxis/.claude/skills/conform/SKILL.md`
- `/opt/praxis/.claude/skills/conform/checks-reference.md`

## Cambios en SKILL.md

### Tabla Security — agregar fila:
```
| S12 | Collaborator audit | `gh api .../collaborators` only owner or appropriate roles |
```

## Cambios en checks-reference.md

Agregar sección:

```markdown
### S12: Collaborator audit

**Why**: Collaborators with excessive permissions (admin on a repo they only need read access to)
increase risk. Regular auditing ensures least privilege.

**Detect**:
\`\`\`bash
gh api repos/$OWNER/$REPO/collaborators --jq '.[] | {login, role_name}'
\`\`\`
- PASS if only the owner has access
- PASS if all collaborators have role appropriate to their function
- WARN if any non-owner collaborator has `admin` role
- INFO: Always report collaborator list for awareness

**Remediate**: Informational only. Report collaborator list with roles.
Recommend reviewing access levels periodically. No auto-fix — removing
or downgrading access requires understanding each collaborator's needs.
```

## Criterios de aceptación

1. `grep -c 'S12' SKILL.md` >= 1
2. `grep -c 'S12' checks-reference.md` >= 1
3. Check reporta solo `pablontiv` como collaborator en homeserver (PASS)
