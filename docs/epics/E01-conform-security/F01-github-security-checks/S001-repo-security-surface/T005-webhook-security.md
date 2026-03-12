---
titulo: "S13: Webhook Security"
estado: Pending
tipo: documentation
contribuye_a:
  - S001-repo-security-surface
---

# T005 — S13: Webhook Security

## Objetivo

Agregar check S13 al skill conform que audita webhooks de un repo,
detectando configuraciones inseguras (HTTP, SSL disabled).

## Archivos a modificar

- `/opt/praxis/.claude/skills/conform/SKILL.md`
- `/opt/praxis/.claude/skills/conform/checks-reference.md`

## Cambios en SKILL.md

### Tabla Security — agregar fila:
```
| S13 | Webhook security | `gh api .../hooks` all HTTPS + insecure_ssl=0 |
```

## Cambios en checks-reference.md

Agregar sección:

```markdown
### S13: Webhook security

**Why**: Webhooks send repo events (pushes, PRs, etc.) to external URLs. Insecure
webhooks (HTTP or SSL verification disabled) can leak sensitive data in transit or
be intercepted via MITM.

**Detect**:
\`\`\`bash
gh api repos/$OWNER/$REPO/hooks --jq '.[] | {id, name, active, config: {url, insecure_ssl}}'
\`\`\`
- PASS if no webhooks exist
- PASS if all webhooks use HTTPS URLs + `insecure_ssl: "0"`
- FAIL if any webhook uses HTTP URL
- FAIL if any webhook has `insecure_ssl: "1"`
- INFO: Report active webhook count and URLs (domain only, not full path)

Note: Webhook secrets are not returned by the API, so we cannot verify if
a secret is configured. Report this as a limitation.

**Remediate**: Report insecure webhooks with details. No auto-fix —
modifying webhooks can break integrations. Recommend updating to HTTPS
and enabling SSL verification.
```

## Criterios de aceptación

1. `grep -c 'S13' SKILL.md` >= 1
2. `grep -c 'S13' checks-reference.md` >= 1
3. Check reporta 0 webhooks en homeserver (PASS — no webhooks configured)
