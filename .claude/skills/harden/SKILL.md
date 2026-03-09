---
name: harden
description: |
  Auditar y endurecer la postura de seguridad de un repositorio GitHub para
  hacerlo público. Detecta lenguaje automáticamente y aplica: branch protection,
  SHA-pinned Actions, secret scanning (gitleaks), CodeQL, Scorecard, Dependabot,
  CODEOWNERS, governance files, y configuración de repo. Usar este skill siempre
  que el usuario diga "hacer público", "harden", "security audit", "preparar
  para open source", "revisar seguridad del repo", "endurecer", "public release
  checklist" — incluso si no dice "harden" e incluso si solo pregunta "está
  listo para ser público?" o "what do I need before open-sourcing?".
  (No para: pentesting, vulnerability research, code review de lógica.)
user-invocable: true
argument-hint: "[--audit-only] [--apply]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

# /harden — Security Hardening for Public Repos

## Routing

Parse `$ARGUMENTS`:

| Input | Mode | Behavior |
|-------|------|----------|
| (empty) | **audit + apply** | Audit, show report, apply fixes with confirmation |
| `--audit-only` | **audit** | Only show the report, don't touch anything |
| `--apply` | **apply** | Audit and apply without individual confirmations (still confirms gh api) |

## Dependencia: gh CLI

**Requerida para**: branch protection, repo settings, secret scanning verification.
**NO requerida para**: file-based checks (CI, governance, dependabot).

Gate check:
```bash
command -v gh && gh auth status
```
Si no está disponible, skip GitHub API checks and note them as "unable to verify".

## Dependencia: gitleaks

**Requerida para**: secret scanning of git history.

Gate check:
```bash
command -v gitleaks
```
Si no está disponible, note it as "gitleaks not installed — install from https://github.com/gitleaks/gitleaks" and continue.

## Phase 1: Detect & Audit

### Step 1: Detect ecosystem

Identify the primary language by checking for marker files in the repo root:

| File | Ecosystem | Language |
|------|-----------|----------|
| `Cargo.toml` | cargo | Rust |
| `go.mod` | gomod | Go |
| `package.json` | npm | Node/JS |
| `pyproject.toml` or `setup.py` | pip | Python |

If multiple are found, use the first match in order above. Store as `$ECOSYSTEM` and `$LANGUAGE`.

### Step 2: Detect GitHub remote

```bash
git remote get-url origin 2>/dev/null
```

Extract `$OWNER/$REPO` from the URL. If no remote, skip all gh api checks.

### Step 3: Run audit checklist

For every check in the checklist below, determine status: PASS, FAIL, or SKIP.

See [checks-reference.md](checks-reference.md) for detailed detection logic per check.

**Essential checks:**

| # | Check | How to detect |
|---|-------|---------------|
| E1 | CI workflow exists | `.github/workflows/*.yml` exists |
| E2 | Actions pinned to SHA | All `uses:` lines have `@[a-f0-9]{40}` pattern |
| E3 | Top-level permissions | `permissions:` block at workflow root level |
| E4 | Advisory/vuln scanning in CI | Ecosystem-specific audit command in workflow |
| E5 | Gitleaks (CI or hook) | `gitleaks` in workflow OR `.githooks/pre-commit` |
| E6 | Dependabot config | `.github/dependabot.yml` exists |
| E7 | Branch protection | `gh api .../protection` returns enforce_admins + PR reviews |
| E8 | Required status checks | `gh api .../protection` returns required_status_checks |
| E9 | Secret scanning enabled | `gh api .../` shows secret_scanning.status = enabled |

**Recommended checks:**

| # | Check | How to detect |
|---|-------|---------------|
| R1 | CodeQL workflow | `.github/workflows/codeql.yml` or codeql in any workflow |
| R2 | Scorecard workflow | `ossf/scorecard-action` in any workflow |
| R3 | Artifact attestation | `attest-build-provenance` in release workflow |
| R4 | SECURITY.md | File exists at root |
| R5 | LICENSE | File exists at root |
| R6 | CODEOWNERS | `.github/CODEOWNERS` or `CODEOWNERS` exists |
| R7 | CONTRIBUTING.md | File exists at root |
| R8 | CODE_OF_CONDUCT.md | File exists at root |
| R9 | Repo settings hardened | Wiki disabled, squash-only, auto-delete branches |

**Nice-to-have checks:**

| # | Check | How to detect |
|---|-------|---------------|
| N1 | .editorconfig | File exists at root |
| N2 | Unsafe code guard | Rust: `forbid(unsafe_code)` in main.rs |
| N3 | Auditable builds | `cargo-auditable` or equivalent in release workflow |
| N4 | SBOM generation | `cargo-sbom` or `cyclonedx` in workflow |

### Step 4: Output report

Format as a scored table:

```
HARDEN — Security Audit Report
═══════════════════════════════
Repo: $OWNER/$REPO
Language: $LANGUAGE ($ECOSYSTEM)
Date: $(date -I)

ESSENTIAL
─────────
[PASS] E1  CI workflow exists
[FAIL] E2  Actions not pinned to SHA
[PASS] E3  Top-level permissions set
...

RECOMMENDED
───────────
[FAIL] R1  No CodeQL workflow
[PASS] R4  SECURITY.md present
...

NICE-TO-HAVE
─────────────
[FAIL] N1  No .editorconfig
...

SCORE: 14/22 checks passing (64%)
Essential: 7/9 | Recommended: 5/9 | Nice-to-have: 2/4
```

If `--audit-only`, STOP HERE and present the report.

## Phase 2: Generate & Apply

For each FAIL check, apply the remediation. Group by type:

### File creation (no confirmation needed)

For missing files, create them from templates in this skill's `templates/` directory. Adapt to `$ECOSYSTEM`/`$LANGUAGE`:

| Check | Template | Adaptation |
|-------|----------|------------|
| E6 | `templates/dependabot-$ECOSYSTEM.yml` | Copy as `.github/dependabot.yml` |
| R1 | `templates/codeql.yml` | Replace `__LANGUAGE__` with `$LANGUAGE` |
| R2 | `templates/scorecard.yml` | Copy as-is |
| N1 | `templates/editorconfig-$LANGUAGE` | Copy as `.editorconfig` |
| R4 | Generate SECURITY.md | Use repo name, standard template |
| R5 | Generate LICENSE | MIT with current year |
| R6 | Generate CODEOWNERS | `* @$OWNER` |
| R7 | Generate CONTRIBUTING.md | Adapted to ecosystem tooling |
| R8 | Generate CODE_OF_CONDUCT.md | Contributor Covenant summary |

### File modification (show diff, then apply)

| Check | What to modify |
|-------|----------------|
| E2 | Pin all `uses:` in workflows to SHA via `git ls-remote` |
| E3 | Add `permissions: contents: read` at workflow top level |
| E4 | Add advisory check to existing audit step |
| E5 | Add gitleaks job to CI + create `.githooks/pre-commit` |
| R3 | Add attestation step to release job |
| N2 | Add `#![forbid(unsafe_code)]` to `src/main.rs` (Rust only) |

For CI modifications, the procedure is:

1. Read the existing workflow
2. Show the user what will change (summary, not full diff)
3. Apply edits

### SHA pinning procedure

For each `uses:` line in workflows:
1. Extract `owner/action@ref`
2. Run `git ls-remote --refs https://github.com/$owner/$action.git "refs/tags/$ref*"` to get latest tag SHA
3. If ref is a branch (like `stable`), use `git ls-remote ... HEAD`
4. Replace `@ref` with `@$SHA # $ref`

### GitHub API calls (always confirm before applying)

These affect shared state — always show what will change and ask for confirmation:

| Check | API call |
|-------|----------|
| E7+E8 | `gh api .../branches/$BRANCH/protection --method PUT` |
| R9 | `gh api repos/$OWNER/$REPO --method PATCH` (wiki, merge strategy, etc.) |
| E9 | `gh repo edit --enable-secret-scanning --enable-secret-scanning-push-protection` |

Branch protection payload (standard baseline):
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

Status check contexts: parse job names from existing CI workflow YAML.

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

1. **Secrets scan**: `gitleaks detect --source . --verbose` (if available)
2. **YAML validation**: For each created/modified workflow, verify valid YAML
3. **Branch protection**: `gh api .../branches/$BRANCH/protection` and verify settings
4. **Final report**: Re-run the audit checklist and show updated score

```
HARDEN — Post-Remediation Summary
══════════════════════════════════

Applied: 8 fixes
Score: 14/22 → 22/22 (100%)

Files created:
  .github/dependabot.yml
  .github/workflows/codeql.yml
  .github/CODEOWNERS
  ...

Files modified:
  .github/workflows/ci.yml (SHA pins, permissions, gitleaks job)

GitHub settings applied:
  Branch protection: enforce_admins, PR reviews, status checks
  Repo: wiki off, squash-only, auto-delete branches

Next steps:
  - git add + commit the new files
  - Push to trigger CI and verify all jobs pass
  - If repo is private: make public, then re-run /harden to apply branch protection
```

## Important guidelines

- **Never commit automatically**. Create files, modify files, configure GitHub — but leave the commit to the user.
- **gh api calls are destructive** — always confirm before executing, even in `--apply` mode.
- **SHA lookup is live** — always fetch latest SHAs at runtime, never hardcode.
- **Additive only** — never delete existing workflow jobs or governance files. Only add or modify.
- **Language detection is best-effort** — if unsure, ask the user.
- **Private repos** can't have branch protection on free plans. Detect this (403 response) and note it for post-public-flip.
