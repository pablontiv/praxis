# Skill Distribution — Read-Only Copies

Skills en `~/.claude/skills/` con campo `source:` en su frontmatter YAML son
copias distribuidas desde un repo fuente. Se sincronizan automáticamente en
cada push vía pre-push hook.

Editar la copia en `~/.claude/skills/` no tiene efecto — se sobreescribe en
el próximo sync. Para modificar un skill distribuido, editar en el repo fuente.

| source | Repo fuente | Path |
|--------|-------------|------|
| `pablontiv/praxis` | `/opt/praxis` | `.claude/skills/<skill>/` |

Cuando un skill tiene `source:` en frontmatter y necesitas modificarlo:
1. Editar en `/opt/<repo>/.claude/skills/<skill>/`
2. Commit + push desde el repo fuente
3. El pre-push hook sincroniza a `~/.claude/skills/`
