---
titulo: "S9: Deploy Key Audit"
estado: Pending
tipo: documentation
contribuye_a:
  - S001-repo-security-surface
---

# T001 — S9: Deploy Key Audit

## Objetivo

Agregar check S9 al skill conform que audita deploy keys de un repo GitHub,
detectando keys con write access innecesario.

## Archivos a modificar

- `/opt/praxis/.claude/skills/conform/SKILL.md`
- `/opt/praxis/.claude/skills/conform/checks-reference.md`

## Cambios en SKILL.md

### Tabla Security — agregar fila:
```
| S9  | Deploy keys audit | `gh api .../keys` all read_only or none |
```

### Phase 2 GitHub API calls — agregar nota:
S9 es informativo. No auto-fix (regenerar deploy key rompe el servicio que la usa).

## Cambios en checks-reference.md

Agregar sección después de S8:

```markdown
### S9: Deploy keys audit

**Why**: Deploy keys con write access expanden la superficie de ataque. Si se comprometen,
pueden pushear código malicioso. La mayoría de deploy keys solo necesitan read (git pull).

**Detect**:
\`\`\`bash
gh api repos/$OWNER/$REPO/keys --jq '.[] | {title, read_only, created_at}'
\`\`\`
- PASS if no deploy keys exist, or all have `read_only: true`
- WARN if any key has `read_only: false`

**Remediate**: Report keys with write access. Recommend regenerating as read-only.
No auto-fix — changing a deploy key requires updating the service that uses it.
```

## Criterios de aceptación

1. `grep -c 'S9' SKILL.md` >= 1
2. `grep -c 'S9' checks-reference.md` >= 1
3. Check detecta `flux-cd-homeserver` con `read_only: false` en homeserver
