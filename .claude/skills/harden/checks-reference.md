# Harden — Checks Reference

Detailed detection and remediation logic for each security check.

## Essential Checks

### E1: CI workflow exists

**Why**: Without CI, nothing else is enforceable.

**Detect**:
```bash
ls .github/workflows/*.yml 2>/dev/null
```
PASS if at least one workflow file exists.

**Remediate**: This is too project-specific to auto-generate. Note as FAIL and suggest user creates a CI workflow first.

---

### E2: Actions pinned to SHA

**Why**: Mutable tags (`@v4`) can be compromised. The March 2025 tj-actions attack affected 23,000+ repos via tag poisoning.

**Detect**: In every workflow YAML, check all `uses:` lines:
```
grep -E 'uses:\s+\S+@' .github/workflows/*.yml
```
PASS if every `@ref` is a 40-char hex SHA. FAIL if any use version tags.

**Remediate**: For each `uses: owner/action@ref`:
1. `git ls-remote --refs https://github.com/$owner/$action.git "refs/tags/$ref*" | sort -t'/' -k3 -V | tail -1`
2. If ref is a branch name: `git ls-remote https://github.com/$owner/$action.git $ref`
3. Replace `@ref` with `@$SHA # $ref`

---

### E3: Top-level permissions

**Why**: Without explicit permissions, GITHUB_TOKEN may have write access to all scopes. Principle of least privilege.

**Detect**:
```bash
head -20 .github/workflows/*.yml | grep -l "^permissions:"
```
PASS if every workflow has a top-level `permissions:` block.

**Remediate**: Add at the workflow root (after `on:`, before `jobs:`):
```yaml
permissions:
  contents: read
```
Keep any per-job overrides (like `contents: write` on release jobs).

---

### E4: Advisory/vulnerability scanning

**Why**: Dependencies may have known CVEs. CI should fail on known vulnerabilities.

**Detect** (by ecosystem):
- **Rust**: `cargo deny check` includes `advisories` in arguments
- **Go**: `govulncheck` appears in workflow
- **Node**: `npm audit` or `snyk` appears in workflow
- **Python**: `pip-audit` or `safety` appears in workflow

**Remediate**:
- **Rust**: Change `cargo deny check licenses bans` → `cargo deny check licenses bans advisories`
- **Go**: Add step `go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck ./...`
- **Node**: Add step `npm audit --audit-level=high`
- **Python**: Add step `pip install pip-audit && pip-audit`

---

### E5: Secret scanning (gitleaks)

**Why**: Secrets in git history are permanently exposed once public. Triple layer: hook (local), CI (PRs), GitHub push protection (auto).

**Detect**:
- Check `.githooks/pre-commit` for `gitleaks`
- Check workflows for `gitleaks/gitleaks-action`
- Either one = PASS, both = ideal

**Remediate**:
1. Create `.githooks/pre-commit`:
```bash
#!/usr/bin/env bash
if command -v gitleaks &>/dev/null; then
  gitleaks git --pre-commit --staged
else
  echo "Warning: gitleaks not installed, skipping secret scan"
fi
```
2. Add CI job (use template pattern from existing workflows for SHA).

---

### E6: Dependabot configuration

**Why**: Automated dependency updates catch vulnerabilities without manual monitoring.

**Detect**:
```bash
test -f .github/dependabot.yml
```

**Remediate**: Copy ecosystem-specific template from `templates/dependabot-$ECOSYSTEM.yml`. Always include `github-actions` ecosystem too.

---

### E7: Branch protection

**Why**: Prevents accidental or malicious direct pushes to main branch.

**Detect**:
```bash
gh api repos/$OWNER/$REPO/branches/$BRANCH/protection 2>/dev/null
```
PASS if response includes `enforce_admins.enabled: true` AND `required_pull_request_reviews`.

**Remediate**: Apply via `gh api --method PUT` with standard payload (see SKILL.md Phase 2).

Note: requires public repo or GitHub Pro for free accounts.

---

### E8: Required status checks

**Why**: Without required checks, PRs can be merged even if CI fails.

**Detect**: From branch protection response, check `required_status_checks.contexts` is non-empty.

**Remediate**: Parse job names from CI workflow and add to branch protection payload.

---

### E9: Secret scanning enabled

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
Note: auto-enabled for new public repos since March 2024, but verify.

---

## Recommended Checks

### R1: CodeQL workflow

**Why**: Free static analysis. Supports Rust (GA Oct 2025), Go, JS/TS, Python, Java, C/C++.

**Detect**: `codeql-action` in any workflow file.

**Remediate**: Copy `templates/codeql.yml`, replace `__LANGUAGE__` placeholder.

---

### R2: OpenSSF Scorecard

**Why**: Automated security health metrics. 18 checks scoring 0-10. CISA endorses it.

**Detect**: `ossf/scorecard-action` in any workflow file.

**Remediate**: Copy `templates/scorecard.yml`.

---

### R3: Artifact attestation (SLSA)

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

### R4–R8: Governance files

| Check | File | Detect | Remediate |
|-------|------|--------|-----------|
| R4 | SECURITY.md | `test -f SECURITY.md` | Generate with standard disclosure template |
| R5 | LICENSE | `test -f LICENSE` | Generate MIT with current year |
| R6 | CODEOWNERS | `test -f .github/CODEOWNERS` | `* @$OWNER` |
| R7 | CONTRIBUTING.md | `test -f CONTRIBUTING.md` | Generate with ecosystem-specific dev setup |
| R8 | CODE_OF_CONDUCT.md | `test -f CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 summary |

---

### R9: Repo settings hardened

**Why**: Reduce attack surface and enforce clean git history.

**Detect**:
```bash
gh api repos/$OWNER/$REPO --jq '{wiki: .has_wiki, pages: .has_pages, squash: .allow_squash_merge, merge: .allow_merge_commit, delete_branch: .delete_branch_on_merge}'
```
PASS if wiki=false, pages=false, squash=true, merge=false, delete_branch=true.

**Remediate**: `gh api repos/$OWNER/$REPO --method PATCH` with settings payload.

---

## Nice-to-have Checks

### N1: .editorconfig

**Detect**: `test -f .editorconfig`

**Remediate**: Copy `templates/editorconfig-$LANGUAGE`.

---

### N2: Unsafe code guard (Rust only)

**Detect**: `grep -q 'forbid(unsafe_code)' src/main.rs`

**Remediate**: Add `#![forbid(unsafe_code)]` as first line of `src/main.rs`.

---

### N3: Auditable builds

**Detect**: `cargo-auditable` or `cargo auditable` in release workflow.

**Remediate**: Replace `cargo build --release` with `cargo auditable build --release` in release job. Add install step for `cargo-auditable`.

---

### N4: SBOM generation

**Detect**: `cargo-sbom`, `cyclonedx`, or `sbom` in workflows.

**Remediate**: Low priority. Note as suggestion, don't auto-apply.
