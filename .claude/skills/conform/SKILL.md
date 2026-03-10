---
name: conform
description: |
  Auditar y estandarizar la infraestructura completa de un repositorio de
  producción: seguridad, git hooks, CI/CD pipelines, versionado, Justfile,
  y configuración de código. Funciona en repos nuevos o existentes en
  cualquier momento. Usar este skill siempre que el usuario diga
  "estandarizar", "conform", "preparar repo", "harden", "security audit",
  "add git hooks", "setup CI", "standardize", "conventional commits",
  "auto-tag", "hacer público", "preparar para open source", "revisar
  seguridad del repo", "endurecer", "public release checklist" — incluso
  si no dice "conform" e incluso si solo pregunta "está listo para ser
  público?" o "what do I need before open-sourcing?" o "estandarizar este
  repo".
  (No para: pentesting, vulnerability research, code review de lógica.)
user-invocable: true
argument-hint: "[--audit-only] [--apply] [--component hooks|ci|security|config]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

# /conform — Production Repository Standardization

## Routing

Parse `$ARGUMENTS`:

| Input | Mode | Behavior |
|-------|------|----------|
| (empty) | **audit + apply** | Audit, show report, apply fixes with confirmation |
| `--audit-only` | **audit** | Only show the report, don't touch anything |
| `--apply` | **apply** | Audit and apply without individual confirmations (still confirms gh api) |
| `--component X` | **filtered** | Only audit/apply checks for component X (hooks, ci, security, config) |

## Dependencies

### Required: gh CLI

**Needed for**: branch protection, repo settings, secret scanning verification.
**NOT needed for**: file-based checks (CI, hooks, governance, dependabot).

Gate check:
```bash
command -v gh && gh auth status
```
If unavailable, skip GitHub API checks and note them as "unable to verify".

### Optional: gitleaks

**Needed for**: secret scanning of git history.
```bash
command -v gitleaks
```
If unavailable, note and continue.

### Optional: rootline

**Needed for**: docs/epics validation checks in hooks and CI.
```bash
command -v rootline
```
If unavailable, skip docs-related checks.

## Phase 1: Detect & Audit

### Step 1: Detect ecosystem

Check for marker files in the repo root:

| File | Ecosystem | Language |
|------|-----------|----------|
| `Cargo.toml` | cargo | Rust |
| `go.mod` | gomod | Go |
| `package.json` | npm | Node/JS |
| `pyproject.toml` or `setup.py` | pip | Python |

If multiple found, use first match in order above. Store as `$ECOSYSTEM` and `$LANGUAGE`.

Read ecosystem metadata from this skill's `templates/ecosystems/$LANGUAGE.yml` for parameterization values.

### Step 2: Detect GitHub remote

```bash
git remote get-url origin 2>/dev/null
```

Extract `$OWNER/$REPO` from the URL. If no remote, skip all gh api checks.

### Step 3: Run audit checklist

For every check, determine status: PASS, FAIL, or SKIP.

See [checks-reference.md](checks-reference.md) for detailed detection logic per check.

**Hooks checks** (skip if `--component` != hooks):

| # | Check | How to detect |
|---|-------|---------------|
| H1 | .githooks/ exists + core.hooksPath set | `.githooks/` dir exists AND `git config core.hooksPath` == `.githooks` |
| H2 | Pre-commit: format + lint + gitleaks | `.githooks/pre-commit` has gitleaks + format/lint (in-hook or via `.pre-commit-config.yaml`) |
| H3 | Commit-msg: conventional commits | `.githooks/commit-msg` contains conventional commit regex pattern |
| H4 | Pre-push: docs validate + drift + build + sync | `.githooks/pre-push` contains rootline validate + drift detection + build + skill sync |
| H5 | Post-merge: sync + build + rootline fix | `.githooks/post-merge` contains skill sync + build + rootline fix |

**CI/CD checks** (skip if `--component` != ci):

| # | Check | How to detect |
|---|-------|---------------|
| C1 | CI workflow with quality gates | `.github/workflows/*.yml` has lint + test + vuln + gitleaks jobs |
| C2 | Auto-tag job | CI workflow has conventional commit → semver auto-tag logic |
| C3 | Release job | CI has ecosystem-specific release job (goreleaser / cargo build) |
| C4 | Actions pinned to SHA | All `uses:` lines have `@[a-f0-9]{40}` pattern |
| C5 | Top-level permissions | Every workflow has top-level `permissions:` block |

**Security checks** (skip if `--component` != security):

| # | Check | How to detect |
|---|-------|---------------|
| S1 | Vulnerability scanning in CI | Ecosystem-specific audit command in workflow |
| S2 | Gitleaks in CI | `gitleaks` in workflow with `fetch-depth: 0` |
| S3 | Dependabot config | `.github/dependabot.yml` exists with ecosystem + github-actions entries |
| S4 | Branch protection | `gh api .../protection` returns PR reviews (WARN if enforce_admins=false) |
| S5 | Secret scanning enabled | `gh api .../` shows secret_scanning.status = enabled |
| S6 | CodeQL workflow | `codeql-action` in any workflow file |
| S7 | Scorecard workflow | `ossf/scorecard-action` in any workflow file |
| S8 | SLSA attestation | `attest-build-provenance` in release workflow |

**Config checks** (skip if `--component` != config):

| # | Check | How to detect |
|---|-------|---------------|
| F1 | .editorconfig | File exists and matches ecosystem template |
| F2 | Justfile with standard recipes | `Justfile` has: check, test, fmt, sync-version, bump-*, release-* |
| F3 | .gitignore comprehensive | File exists with ecosystem-appropriate patterns |
| F4 | CONTRIBUTING.md | File exists with setup + workflow + quality gates |
| F5 | SECURITY.md | File exists at root |
| F6 | LICENSE | File exists at root |
| F7 | CODE_OF_CONDUCT.md | File exists at root |

**Governance checks** (part of security component):

| # | Check | How to detect |
|---|-------|---------------|
| G1 | CODEOWNERS | `.github/CODEOWNERS` or `CODEOWNERS` exists |
| G2 | Repo settings hardened | Wiki disabled, squash-only, auto-delete branches |
| G3 | Issue/PR templates | `.github/ISSUE_TEMPLATE/` or `.github/pull_request_template.md` |

### Step 4: Output report

```
CONFORM — Repository Standards Report
══════════════════════════════════════
Repo: $OWNER/$REPO
Language: $LANGUAGE ($ECOSYSTEM)
Date: $(date -I)

HOOKS
─────
[PASS] H1  .githooks/ exists + core.hooksPath configured
[PASS] H2  Pre-commit: format + lint + gitleaks
[PASS] H3  Commit-msg: conventional commits enforced
[FAIL] H4  Pre-push: missing drift detection
[PASS] H5  Post-merge: sync + build + fix

CI/CD
─────
[PASS] C1  CI workflow with quality gates
[PASS] C2  Auto-tag from conventional commits
[PASS] C3  Release job configured
[PASS] C4  Actions pinned to SHA
[PASS] C5  Top-level permissions set

SECURITY
────────
[PASS] S1  Vulnerability scanning in CI
[PASS] S2  Gitleaks in CI
[PASS] S3  Dependabot configured
[SKIP] S4  Branch protection (gh not available)
[SKIP] S5  Secret scanning (gh not available)
[PASS] S6  CodeQL configured
[PASS] S7  Scorecard configured
[PASS] S8  SLSA attestation

CONFIG
──────
[PASS] F1  .editorconfig present
[PASS] F2  Justfile with standard recipes
[PASS] F3  .gitignore comprehensive
[PASS] F4  CONTRIBUTING.md
[PASS] F5  SECURITY.md
[PASS] F6  LICENSE
[PASS] F7  CODE_OF_CONDUCT.md

GOVERNANCE
──────────
[PASS] G1  CODEOWNERS configured
[SKIP] G2  Repo settings (gh not available)
[PASS] G3  Issue/PR templates

SCORE: 23/25 checks passing (92%)
Hooks: 4/5 | CI/CD: 5/5 | Security: 6/8 | Config: 7/7 | Governance: 1/3
```

If `--audit-only`, STOP HERE and present the report.

## Phase 2: Generate & Apply

For each FAIL check, apply the remediation. Group by type:

### File creation (no confirmation needed in --apply mode)

For missing files, create from templates in `templates/` directory. Adapt to `$ECOSYSTEM`/`$LANGUAGE`. Replace `{{PLACEHOLDER}}` values with detected values.

| Check | Template | Target |
|-------|----------|--------|
| H2 | `templates/hooks/pre-commit.sh` | `.githooks/pre-commit` |
| H3 | `templates/hooks/commit-msg.sh` | `.githooks/commit-msg` |
| H4 | `templates/hooks/pre-push.sh` | `.githooks/pre-push` |
| H5 | `templates/hooks/post-merge.sh` | `.githooks/post-merge` |
| S3 | `templates/security/dependabot-$ECOSYSTEM.yml` | `.github/dependabot.yml` |
| S6 | `templates/security/codeql.yml` | `.github/workflows/codeql.yml` |
| S7 | `templates/security/scorecard.yml` | `.github/workflows/scorecard.yml` |
| F1 | `templates/config/editorconfig-$LANGUAGE` | `.editorconfig` |
| F2 | `templates/justfile/justfile-$LANGUAGE` | `Justfile` |
| F3 | `templates/config/gitignore-$LANGUAGE` | `.gitignore` |
| F4 | `templates/config/contributing-$LANGUAGE.md` | `CONTRIBUTING.md` |
| F5 | Generate SECURITY.md | `SECURITY.md` |
| F6 | Generate LICENSE | `LICENSE` (MIT with current year) |
| F7 | Generate CODE_OF_CONDUCT.md | `CODE_OF_CONDUCT.md` |
| G1 | Generate CODEOWNERS | `.github/CODEOWNERS` (`* @$OWNER`) |

### Hook setup

When creating hooks (H1-H5):
1. Create `.githooks/` directory
2. Write hook files with `chmod +x`
3. Set `git config core.hooksPath .githooks`

### Template parameterization

Replace `{{PLACEHOLDER}}` values in templates:

| Placeholder | Source |
|-------------|--------|
| `{{PROJECT_NAME}}` | Repo name from `git remote get-url origin` or directory name |
| `{{OWNER}}` | Extracted from remote URL |
| `{{BINARY_NAME}}` | Same as project name (lowercase) |
| `{{SOURCE_DIR}}` | `cmd/` for Go, `src/` for Rust |
| `{{FORMAT_CHECK}}` | From ecosystem metadata `pre_commit_format` |
| `{{LINT_CHECK}}` | From ecosystem metadata `pre_commit_lint` |
| `{{BUILD_RELEASE_CMD}}` | From ecosystem metadata |
| `{{VERSION_FILE}}` | From ecosystem metadata |
| `{{MIN_VERSION}}` | From ecosystem metadata |
| `{{QUALITY_GATE_JOBS}}` | Detected job names from CI workflow |

### SHA pinning (C4)

For `__PLACEHOLDER__` values in security templates (runtime-resolved):
1. Extract `owner/action@ref` from each `uses:` line
2. Run `git ls-remote --refs https://github.com/$owner/$action.git "refs/tags/$ref*" | sort -t'/' -k3 -V | tail -1`
3. Replace `@ref` with `@$SHA # $ref`

### CI modifications (show diff, then apply)

| Check | What to modify |
|-------|----------------|
| C4 | Pin all `uses:` in workflows to SHA |
| C5 | Add `permissions: contents: read` at workflow top level |
| S1 | Add advisory check step to CI |
| S2 | Add gitleaks job to CI |
| S8 | Add attestation step to release job |

### GitHub API calls (always confirm before applying)

| Check | API call |
|-------|----------|
| S4 | `gh api .../branches/$BRANCH/protection --method PUT` |
| S5 | `gh repo edit --enable-secret-scanning --enable-secret-scanning-push-protection` |
| G2 | `gh api repos/$OWNER/$REPO --method PATCH` (wiki, merge strategy, etc.) |

Branch protection payload:
```json
{
  "required_status_checks": { "strict": true, "contexts": ["<detected-ci-job-names>"] },
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": 1 },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

Repo settings payload:
```json
{
  "has_wiki": false,
  "has_pages": false,
  "delete_branch_on_merge": true,
  "allow_squash_merge": true,
  "allow_merge_commit": false,
  "allow_rebase_merge": false
}
```

## Phase 3: Verify

After applying:

1. **YAML validation**: For each created/modified workflow, verify valid YAML
2. **Hook permissions**: Verify `.githooks/*` are executable
3. **Secrets scan**: `gitleaks detect --source . --verbose` (if available)
4. **Branch protection**: `gh api .../branches/$BRANCH/protection` and verify (if gh available)
5. **Final report**: Re-run the audit checklist and show updated score

```
CONFORM — Post-Remediation Summary
═══════════════════════════════════

Applied: 8 fixes
Score: 18/25 → 25/25 (100%)

Files created:
  .githooks/pre-commit
  .githooks/commit-msg
  .github/dependabot.yml
  ...

Files modified:
  .github/workflows/ci.yml (SHA pins, permissions)

GitHub settings applied:
  Branch protection: enforce_admins, PR reviews, status checks
  Repo: wiki off, squash-only, auto-delete branches

Next steps:
  - git add + commit the new files
  - Push to trigger CI and verify all jobs pass
```

## Important guidelines

- **Never commit automatically**. Create files, modify files, configure GitHub — but leave the commit to the user.
- **gh api calls are destructive** — always confirm before executing, even in `--apply` mode.
- **SHA lookup is live** — always fetch latest SHAs at runtime, never hardcode.
- **Additive only** — never delete existing workflow jobs, hooks, or governance files. Only add or modify.
- **Respect existing files** — if a hook/config already exists with more content than the template, preserve the extra content and only add what's missing.
- **Language detection is best-effort** — if unsure, ask the user.
- **Private repos** can't have branch protection on free plans. Detect 403 response and note.
