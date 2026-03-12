# Contributing to {{PROJECT_NAME}}

## Development Setup

```bash
git clone https://github.com/{{OWNER}}/{{PROJECT_NAME}}.git
cd {{PROJECT_NAME}}

# Set up git hooks
git config core.hooksPath .githooks

# Verify environment
just check
just test
```

Requires {{MIN_VERSION}} and [just](https://github.com/casey/just).

## Just Recipes

Run `just --list` to see all available recipes. Key ones:

| Recipe | What it does |
|--------|-------------|
| `just check` | Format check + clippy + cargo check |
| `just test` | Run all tests |
| `just fmt` | Auto-format code |
| `just audit` | Dependency license/ban audit |
| `just sync-version` | Sync `Cargo.toml` version with latest git tag |
| `just release-patch` | Full release: check → test → bump patch → commit → tag → push |
| `just release-minor` | Same but bumps minor version |

## Workflow

1. Fork the repository
2. Create a feature branch from `master`
3. Make your changes
4. Run `just check` and `just test`
5. Commit using [Conventional Commits](https://www.conventionalcommits.org/)
6. Open a Pull Request

## Commit Convention

```
type(scope): description
```

| Type | When to use |
|------|-------------|
| `feat` | New user-facing functionality |
| `fix` | Bug fix |
| `refactor` | Internal restructuring, no behavior change |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `chore` | Build, CI, dependency updates |

Breaking changes use `!` suffix: `feat!: remove deprecated flag`

## Git Hooks

Hooks live in `.githooks/` and are activated with `git config core.hooksPath .githooks`.

| Hook | What it does |
|------|-------------|
| `pre-commit` | cargo fmt check, clippy, gitleaks secret scan |
| `commit-msg` | Validates conventional commit format |
| `pre-push` | Validates docs, checks code-docs drift, rebuilds binary |
| `post-merge` | Rebuilds binary, propagates doc aggregates |

## Quality Gates

All PRs must pass:
- `cargo fmt --all -- --check`
- `cargo clippy --all-targets --all-features -- -D warnings`
- `cargo test --all-features`
- `cargo deny check licenses bans advisories`

## Reporting Issues

- **Bugs**: Use the bug report template
- **Features**: Use the feature request template
- **Security**: See [SECURITY.md](SECURITY.md) for responsible disclosure
