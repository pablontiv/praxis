# Conform — Checks Reference

Detailed detection and remediation logic for each check.

---

## Hooks Checks

### H1: .githooks/ exists + core.hooksPath configured

**Why**: Git hooks enforce conventions locally before code reaches CI. Without them, developers can push non-conforming commits.

**Detect**:
```bash
test -d .githooks && [ "$(git config core.hooksPath)" = ".githooks" ]
```
PASS if both conditions true.

**Remediate**:
1. `mkdir -p .githooks`
2. `git config core.hooksPath .githooks`

---

### H2: Pre-commit has format + lint + gitleaks

**Why**: Catches formatting errors, lint violations, and secrets before they enter git history. The earlier you catch, the cheaper the fix.

**Detect**:
```bash
test -f .githooks/pre-commit
```
Then verify content includes gitleaks secret scanning AND format/lint via one of:
- **Strategy A (all-in-hook)**: format + lint + gitleaks all in `.githooks/pre-commit`
  - **Rust**: `cargo fmt` AND `cargo clippy` AND `gitleaks`
- **Strategy B (framework + hook)**: `.pre-commit-config.yaml` handles format/lint, `.githooks/pre-commit` handles gitleaks
  - **Go**: `.pre-commit-config.yaml` with `golangci-lint` + `gofmt` AND `.githooks/pre-commit` with `gitleaks`

PASS if gitleaks present AND format/lint covered (either in-hook or via pre-commit framework). WARN if gitleaks only with no format/lint in either location.

**Remediate**: For Strategy A (recommended for Rust), generate from `templates/hooks/pre-commit.sh`. For Strategy B (Go with pre-commit framework), ensure `.pre-commit-config.yaml` covers format/lint and `.githooks/pre-commit` covers gitleaks.

---

### H3: Commit-msg enforces conventional commits

**Why**: Conventional commits enable automatic versioning, changelog generation, and meaningful git history. The commit-msg hook is the enforcement point.

**Detect**:
```bash
grep -q 'feat|fix|chore|docs|refactor|perf|test|style|ci' .githooks/commit-msg 2>/dev/null
```
PASS if conventional commit regex pattern found.

**Remediate**: Copy `templates/hooks/commit-msg.sh` (universal, no parameterization needed). Set executable.

---

### H4: Pre-push validates docs + detects drift + builds + syncs skills

**Why**: Pre-push is the last gate before code reaches remote. It should validate documentation consistency, detect code-docs drift, rebuild the project binary, and sync Claude Code skills.

**Detect**: Check `.githooks/pre-push` contains:
1. `rootline validate` (docs validation)
2. `git diff --name-only` with drift detection logic — two scopes:
   - **Source drift**: source dir changed but docs unchanged
   - **Infra drift**: CI/scripts/config changed (`.github/`, `install.sh`, `install.ps1`, `Justfile`, `Cargo.toml`/`go.mod`) but docs unchanged
3. Build command (ecosystem-specific)
4. Skill sync (`cp -r` to `~/.claude/skills/`)

PASS if all four present (both drift scopes count as #2). WARN if partial.

**Remediate**: Generate from `templates/hooks/pre-push.sh` with ecosystem params. Key placeholders:
- `{{SOURCE_DIR}}`: `cmd/` (Go) or `src/` (Rust)
- `{{BUILD_RELEASE_CMD}}`: ecosystem build command
- `{{PROJECT_NAME}}`: repo name
- `{{INFRA_PATHS}}`: `.github/ install.sh install.ps1 Justfile` + ecosystem config (`Cargo.toml` for Rust, `go.mod .goreleaser.yml` for Go)

---

### H5: Post-merge syncs + builds + propagates aggregates

**Why**: After pulling merged code, the local binary and skills must stay in sync. Rootline aggregates may need re-propagation after doc merges.

**Detect**: Check `.githooks/post-merge` contains:
1. Skill sync to `~/.claude/skills/`
2. Build command (ecosystem-specific)
3. `rootline fix --all` (aggregate propagation)

PASS if all three present. WARN if partial.

**Remediate**: Generate from `templates/hooks/post-merge.sh` with ecosystem params.

---

### H6: Skill sync in hooks

**Why**: Claude Code skills in `.claude/skills/` must stay in sync with `~/.claude/skills/` so the user always has the latest version. Hooks automate this on push and merge.

**Detect**: Check `.githooks/pre-push` AND `.githooks/post-merge` both contain:
```bash
grep -q '.claude/skills' .githooks/pre-push .githooks/post-merge 2>/dev/null
```
PASS if both hooks sync skills. WARN if only one does.

**Remediate**: Already included in `templates/hooks/pre-push.sh` and `templates/hooks/post-merge.sh`. Ensure the skill sync block is present.

---

## CI/CD Checks

### C1: CI workflow with quality gates

**Why**: CI is the definitive quality gate. Without parallel quality checks, bad code reaches main branch.

**Detect**: At least one `.github/workflows/*.yml` exists with jobs covering:
- Format/lint check
- Tests
- Vulnerability/audit scan
- Secret scanning (gitleaks)

PASS if all four categories present across CI workflows.

**Remediate**: This is project-specific — note as FAIL and guide the user. Reference `templates/ci/gitleaks-job.yml` for the gitleaks job pattern if missing.

---

### C2: Auto-tag from conventional commits

**Why**: Automatic versioning from conventional commits eliminates manual version management. Pre-1.0 and post-1.0 strategies differ to match semver expectations.

**Detect**: CI workflow contains:
- Conventional commit parsing (feat/fix/breaking patterns)
- Version bump logic (MAJOR/MINOR/PATCH calculation)
- `git tag` and `git push origin` (or `gh release create`)

PASS if auto-tag logic present.

**Remediate**: Reference `templates/ci/auto-tag.yml` for the standard algorithm. Must be adapted to existing workflow structure (runs after quality gates, needs write permissions).

---

### C3: Release job

**Why**: Automated releases produce consistent cross-platform binaries with provenance.

**Detect**:
- **Go**: `goreleaser` in workflow
- **Rust**: `cargo build --release` or `cargo auditable build` + `gh release create` in workflow

PASS if release automation present.

**Remediate**: Reference `templates/ci/release-go.yml` or `templates/ci/release-rust.yml`.

---

### C4: Actions pinned to SHA

**Why**: Mutable tags (`@v4`) can be compromised. The March 2025 tj-actions attack affected 23,000+ repos via tag poisoning. SHA pinning is the defense.

**Detect**: In every workflow YAML:
```bash
grep -E 'uses:\s+\S+@' .github/workflows/*.yml
```
PASS if every `@ref` is a 40-char hex SHA. FAIL if any use version tags.

**Remediate**: For each `uses: owner/action@ref`:
1. `git ls-remote --refs https://github.com/$owner/$action.git "refs/tags/$ref*" | sort -t'/' -k3 -V | tail -1`
2. If ref is a branch: `git ls-remote https://github.com/$owner/$action.git $ref`
3. Replace `@ref` with `@$SHA # $ref`

---

### C5: Top-level permissions

**Why**: Without explicit permissions, GITHUB_TOKEN may have write access to all scopes. Principle of least privilege.

**Detect**:
```bash
head -20 .github/workflows/*.yml | grep -l "^permissions:"
```
PASS if every workflow has a top-level `permissions:` block.

**Remediate**: Add after `on:`, before `jobs:`:
```yaml
permissions:
  contents: read
```
Keep any per-job overrides (like `contents: write` on release jobs).

---

### C6: Cross-platform release binaries

**Why**: Users on different platforms need pre-built binaries. A single-platform release limits adoption.

**Detect**: Release workflow(s) produce binaries for ≥2 of: linux, darwin, windows.
- **Rust**: Multiple `cargo build --release` or `cargo zigbuild` steps with different `--target` values, or separate release jobs per platform
- **Go**: `.goreleaser.yml` with `builds:` containing multiple `goos`/`goarch` entries

PASS if ≥2 platforms covered. WARN if only one.

**Remediate**: Add per-platform release jobs (Rust) or goreleaser targets (Go). Reference existing C3 release infrastructure.

---

### C7: Release smoke tests

**Why**: A binary that can't start is worse than no binary. Smoke tests catch linking errors, missing symbols, and broken builds before users download them.

**Detect**: Release workflow runs `--version` and `--help` (or subcommand help) on built binaries BEFORE upload/publish.
```bash
grep -E '\-\-version|\-\-help' .github/workflows/*.yml
```
PASS if smoke test steps exist in release job(s) between build and upload steps.

**Remediate**: Add smoke test step after build:
```yaml
- name: Smoke Test Binary
  run: |
    ./binary --version
    ./binary --help
```

---

### C8: Changelog generation

**Why**: Users need to know what changed between releases. Automated changelog from conventional commits ensures consistency.

**Detect**:
- **Rust**: `cliff.toml` exists AND `git-cliff` in release workflow
- **Go**: `.goreleaser.yml` has `changelog:` section (goreleaser generates changelogs natively)

PASS if changelog automation present. WARN if manual only.

**Remediate**:
- **Rust**: Install `git-cliff`, create `cliff.toml` from template, add step to release job: `git-cliff --latest --strip header --output RELEASE_NOTES.md`
- **Go**: Ensure `.goreleaser.yml` has `changelog:` with `use: git` or `use: github`

---

## Security Checks

### S1: Vulnerability scanning in CI

**Why**: Dependencies may have known CVEs. CI should fail on known vulnerabilities.

**Detect** (by ecosystem):
- **Rust**: `cargo deny check` includes `advisories`
- **Go**: `govulncheck` in workflow
- **Node**: `npm audit` or `snyk` in workflow
- **Python**: `pip-audit` or `safety` in workflow

**Remediate**:
- **Rust**: Ensure `cargo deny check` arguments include `advisories`
- **Go**: Add step: `go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./...`
- **Node**: Add step: `npm audit --audit-level=high`
- **Python**: Add step: `pip install pip-audit && pip-audit`

---

### S2: Gitleaks in CI

**Why**: Secrets in git history are permanently exposed once public. CI scanning catches what pre-commit hooks miss (new contributors without hooks, force pushes).

**Detect**: `gitleaks/gitleaks-action` in any workflow AND `fetch-depth: 0` on checkout.

**Remediate**: Add gitleaks job from `templates/ci/gitleaks-job.yml`. Resolve `__GITLEAKS_SHA__` at runtime.

---

### S3: Dependabot configured

**Why**: Automated dependency updates catch vulnerabilities without manual monitoring.

**Detect**: `test -f .github/dependabot.yml` AND file contains both ecosystem package manager AND `github-actions` entries.

**Remediate**: Copy `templates/security/dependabot-$ECOSYSTEM.yml` to `.github/dependabot.yml`.

---

### S4: Branch protection

**Why**: Prevents accidental or malicious direct pushes to main branch.

**Detect**:
```bash
gh api repos/$OWNER/$REPO/branches/$BRANCH/protection 2>/dev/null
```
- PASS if response includes `required_pull_request_reviews` AND `enforce_admins.enabled: true`
- WARN if `required_pull_request_reviews` present but `enforce_admins: false` (common for solo-maintainer repos where owner needs bypass capability)
- FAIL if no branch protection or no PR review requirement

**Remediate**: Apply via `gh api --method PUT` (see SKILL.md Phase 2 for payload). Note: requires public repo or GitHub Pro for free accounts. For solo-maintainer repos, `enforce_admins: false` is acceptable — note in report but don't flag as FAIL.

---

### S5: Secret scanning enabled

**Why**: GitHub scans for known token patterns and blocks pushes containing them.

**Detect**:
```bash
gh api repos/$OWNER/$REPO --jq '.security_and_analysis.secret_scanning.status'
```
PASS if `enabled`.

**Remediate**:
```bash
gh repo edit $OWNER/$REPO --enable-secret-scanning --enable-secret-scanning-push-protection
```

---

### S6: CodeQL workflow

**Why**: Free static analysis. Supports Rust (GA Oct 2025), Go, JS/TS, Python, Java, C/C++.

**Detect**: `codeql-action` in any workflow file.

**Remediate**: Copy `templates/security/codeql.yml`, replace `__LANGUAGE__` with detected language. Resolve SHAs at runtime.

---

### S7: OpenSSF Scorecard

**Why**: Automated security health metrics. 18 checks scoring 0-10. CISA endorses it.

**Detect**: `ossf/scorecard-action` in any workflow file.

**Remediate**: Copy `templates/security/scorecard.yml`. Resolve SHAs at runtime.

---

### S8: SLSA build attestation

**Why**: Cryptographic provenance linking binary to source + build. SLSA Build Level 2 with one action.

**Detect**: `attest-build-provenance` in release/build workflow.

**Remediate**: Add to release job:
```yaml
- uses: actions/attest-build-provenance@<SHA>
  with:
    subject-path: <path-to-binary>
```
Requires permissions: `id-token: write`, `attestations: write`.

---

## Config Checks

### F1: .editorconfig

**Detect**: `test -f .editorconfig`

**Remediate**: Copy `templates/config/editorconfig-$LANGUAGE`.

---

### F2: Justfile with standard recipes

**Why**: Justfile provides a consistent interface across ecosystems. Standard recipes (check, test, fmt, release-*) let contributors onboard without reading build docs.

**Detect**: `test -f Justfile` AND file contains all required recipes:
- `check:` (format + lint + build/check)
- `test:` (test runner)
- `fmt:` (auto-format)
- `sync-version:` (version sync from git tag)
- `bump-patch:` / `bump-minor:` (version increment)
- `release-patch:` / `release-minor:` (full release)

PASS if all present. WARN if Justfile exists but missing some recipes.

**Remediate**: Copy `templates/justfile/justfile-$LANGUAGE`. Replace `{{PROJECT_NAME}}` and `{{VERSION_FILE}}`.

---

### F3: .gitignore comprehensive

**Detect**: `test -f .gitignore` AND file contains ecosystem-specific patterns (build artifacts, IDE, OS files).

**Remediate**: If missing, copy `templates/config/gitignore-$LANGUAGE`. If exists but incomplete, suggest additions without overwriting.

---

### F4: CONTRIBUTING.md

**Detect**: `test -f CONTRIBUTING.md` AND file contains setup instructions + workflow + quality gates.

**Remediate**: Copy `templates/config/contributing-$LANGUAGE.md`. Replace `{{PROJECT_NAME}}`, `{{OWNER}}`, `{{MIN_VERSION}}`.

---

### F5–F7: Governance files

| Check | File | Detect | Remediate |
|-------|------|--------|-----------|
| F5 | SECURITY.md | `test -f SECURITY.md` | Generate with standard disclosure template using repo name |
| F6 | LICENSE | `test -f LICENSE` | Generate MIT with current year and `$OWNER` |
| F7 | CODE_OF_CONDUCT.md | `test -f CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 summary |

---

### F8: Install scripts

**Why**: Pre-built binaries need a frictionless install path. `curl | bash` is the standard for Unix, PowerShell for Windows.

**Detect**: `test -f install.sh`. If CI produces Windows binaries (C6 detected Windows target), also check `test -f install.ps1`.

PASS if install.sh exists. WARN if Windows binaries exist but no install.ps1.

**Remediate**: Generate from `templates/config/install-$LANGUAGE.sh`. Key features: platform detection, latest release from GitHub API, install to `~/.local/bin/` or `/usr/local/bin/`.

---

### F9: Linter config file

**Why**: Explicit linter configuration ensures consistent code quality across contributors and CI. Without it, lint rules depend on tool defaults which may change between versions.

**Detect**:
- **Rust**: `test -f .clippy.toml`
- **Go**: `test -f .golangci.yml` OR `test -f .golangci.yaml`

PASS if ecosystem-appropriate linter config exists.

**Remediate**: Generate with strict defaults:
- **Rust**: `.clippy.toml` with nursery + pedantic group
- **Go**: `.golangci.yml` with govet, errcheck, staticcheck, unused, ineffassign, gocritic, gosec

---

### F10: Dependency policy config (Rust only)

**Why**: `cargo deny` enforces license compliance, bans specific crates, and checks advisories. The config file makes the policy explicit and reproducible.

**Detect**: `test -f deny.toml` AND file contains `[advisories]`, `[licenses]`, `[bans]` sections.

PASS if deny.toml exists with all three sections. SKIP for non-Rust ecosystems.

**Remediate**: Generate `deny.toml` from template with safe defaults (MIT/Apache-2.0/BSD allow list, advisory checking enabled, wildcard dependencies warned).

---

### F11: Release profile optimized (Rust only)

**Why**: Default release builds leave performance and size on the table. LTO, single codegen unit, and symbol stripping produce smaller, faster binaries.

**Detect**: `Cargo.toml` contains `[profile.release]` with `lto = true` AND `strip = true`.

PASS if both present. WARN if `[profile.release]` exists but missing optimizations. SKIP for non-Rust ecosystems.

**Remediate**: Add to `Cargo.toml`:
```toml
[profile.release]
opt-level = 3
lto = true
codegen-units = 1
panic = "abort"
strip = true
```

---

## Governance Checks

### G1: CODEOWNERS

**Detect**: `test -f .github/CODEOWNERS` OR `test -f CODEOWNERS`

**Remediate**: Create `.github/CODEOWNERS` with `* @$OWNER`

---

### G2: Repo settings hardened

**Why**: Reduce attack surface and enforce clean git history.

**Detect**:
```bash
gh api repos/$OWNER/$REPO --jq '{wiki: .has_wiki, squash: .allow_squash_merge, merge: .allow_merge_commit, delete_branch: .delete_branch_on_merge}'
```
PASS if wiki=false, squash=true, merge=false, delete_branch=true.

**Remediate**: `gh api repos/$OWNER/$REPO --method PATCH` with settings payload.

---

### G3: Issue/PR templates

**Detect**: `.github/ISSUE_TEMPLATE/` directory exists OR `.github/pull_request_template.md` exists.

**Remediate**: Low priority. Note as suggestion — templates are project-specific.

---

## Ecosystem-Specific Checks (optional)

These are checked when detected but not required:

| Check | Ecosystem | Detect | Remediate |
|-------|-----------|--------|-----------|
| N1 | Rust | `forbid(unsafe_code)` in main.rs | Add `#![forbid(unsafe_code)]` |
| N2 | Rust | `cargo-auditable` in release | Replace `cargo build` with `cargo auditable build` |
| N3 | Any | SBOM generation in workflow | Note as suggestion |
