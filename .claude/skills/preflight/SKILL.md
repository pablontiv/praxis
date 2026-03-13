---
source: pablontiv/praxis
name: preflight
description: |
  Verificación pre-vuelo del entorno. Chequea estado de git, disponibilidad
  de CLIs, integridad de schemas rootline, archivos del proyecto, y presencia
  de .stem ANTES de que otros skills corran. Detecta tipo de proyecto
  automáticamente. SIEMPRE usar este skill cuando el entorno parece mal,
  falta una herramienta, la validación falla inesperadamente, git está en
  mal estado, o antes de iniciar un workflow complejo. Triggers: "preflight",
  "check environment", "verificar entorno", "que falta", "why is this failing",
  "pre-check" — incluso si el usuario no pide un chequeo de entorno e incluso
  si el error parece no estar relacionado con el entorno. En proyectos de
  infraestructura (k8s, IaC), usar PROACTIVAMENTE al inicio de sesión o tras
  compactación para detectar problemas de salud del cluster (pods not ready,
  restarts altos, servicios caídos) ANTES de iniciar cualquier investigación.
  También corre como gate antes de otros skills con --for <skill>.
user-invocable: true
argument-hint: "[--full | --quick | --for <skill>]"
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# /preflight — Pre-flight Environment Verification

Verify that the environment is ready before executing skills. Catches missing CLIs, dirty git state, broken schemas, and absent project files before they cause cryptic failures downstream.

## Modes

Parse `$ARGUMENTS` to determine mode:

| Argument | Mode | What it checks |
|----------|------|----------------|
| *(none)* | Auto-detect | Detect project type, run appropriate checks |
| `--full` | Full | All verifications regardless of project type |
| `--quick` | Quick | Git state + project paths only (fast) |
| `--for <skill>` | Skill-specific | Only checks required by that skill |

---

## Procedure

### Step 1: Identify project

```bash
# Get project name from directory
basename "$(pwd)"
```

Print the header immediately:

```
PREFLIGHT — [project-name]
═══════════════════════════
```

### Step 2: Detect project type (auto-detect mode only)

If mode is auto-detect (no arguments), determine project type from files present. A project can match multiple types. Run checks for ALL matched types.

```bash
# Run all detections in one pass
echo "--- Project Type Detection ---"
[ -f go.mod ] && echo "TYPE:go"
[ -d k8s/clusters ] || [ -d terraform/k8s ] && echo "TYPE:k8s"
[ -d terraform/proxmox ] && echo "TYPE:proxmox"
[ -f MAP.md ] || [ -d lines ] && echo "TYPE:discover"
[ -f .claude/roadmap.local.md ] && echo "TYPE:roadmap"
[ -f go.mod ] || [ -d k8s ] || [ -d terraform ] || [ -f MAP.md ] || [ -d lines ] || [ -f .claude/roadmap.local.md ] || echo "TYPE:generic"
```

### Step 3: Run checks

Execute checks in order. Track counts: `errors=0`, `warnings=0`.

#### 3a. Git State (all modes)

```bash
# Current branch
git branch --show-current 2>/dev/null

# Dirty state (uncommitted changes)
git status --porcelain 2>/dev/null

# Remote sync status
git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null
```

Interpret results:
- Branch name → report it
- Porcelain output empty → `clean`; non-empty → `dirty (N uncommitted changes)` → **warning**
- Left-right count: `0\t0` → `synced`; left > 0 → `N commits ahead`; right > 0 → `N commits behind` → **warning**
- If git is not initialized → `not a git repo` → **warning**

Output line:
```
[✓] Git: main branch, clean, synced with remote
[⚠] Git: feature/xyz branch, dirty (3 uncommitted changes), 2 commits ahead
```

#### 3b. CLI Availability (not in --quick mode)

Which CLIs to check depends on mode:

| Mode | CLIs to check |
|------|---------------|
| `--full` | rootline, kubectl, tofu, flux, velero, helm, go, golangci-lint |
| `--for roadmap` | rootline |
| `--for discover` | rootline |
| `--for hypothesize` | rootline |
| `--for workload` | kubectl, flux, helm |
| `--for instance` | tofu |
| auto-detect TYPE:go | go, golangci-lint |
| auto-detect TYPE:k8s | kubectl, flux, helm |
| auto-detect TYPE:proxmox | tofu |
| auto-detect TYPE:discover | rootline |
| auto-detect TYPE:roadmap | rootline |
| auto-detect TYPE:generic | rootline |

For each CLI, check availability and version:

```bash
# Check each CLI — use command -v, NOT which
for cli in rootline kubectl tofu flux velero helm go golangci-lint; do
  if command -v "$cli" >/dev/null 2>&1; then
    version=$("$cli" version --short 2>/dev/null || "$cli" version 2>/dev/null || "$cli" --version 2>/dev/null || echo "installed")
    echo "OK:$cli:$version"
  else
    echo "MISSING:$cli"
  fi
done
```

Adapt the list of CLIs to the mode. Do NOT check CLIs that are not relevant to the detected project type (unless `--full`).

Interpret results:
- `OK` → report with version snippet (first line, truncated to 60 chars)
- `MISSING` and CLI is required for detected project type → **error**
- `MISSING` and CLI is optional → **warning**

Required vs optional:
- `rootline` is **required** for discover, roadmap, hypothesize project types
- `kubectl` is **required** for k8s project type
- `tofu` is **required** for proxmox project type
- `go` is **required** for go project type
- All others are **warnings** when missing

Output lines:
```
[✓] CLI: rootline v0.9.2 available
[✗] CLI: kubectl not found — required for k8s operations
[⚠] CLI: velero not found — optional, needed for backup operations
```

#### 3c. Rootline Integrity (not in --quick mode)

Only if `rootline` is available AND project has rootline-managed content (any `.stem` file exists):

```bash
# Check if any .stem files exist
find . -name '.stem' -maxdepth 5 -print -quit 2>/dev/null

# If .stem files exist, validate
rootline validate --all . --output json 2>&1
```

Parse the JSON output:
- Count total files validated and errors
- If 0 errors → report success with count
- If errors > 0 → report each error path briefly → **error** (count as 1 error regardless of how many files fail)

Output lines:
```
[✓] Rootline: 15/15 files valid, 0 errors
[✗] Rootline: 12/15 files valid, 3 errors — run 'rootline fix --all .' to repair
```

#### 3d. Project Files (all modes)

Check presence of key project files:

```bash
# Check project files
[ -f CLAUDE.md ] && echo "OK:CLAUDE.md" || echo "MISSING:CLAUDE.md"
[ -f README.md ] && echo "OK:README.md" || echo "MISSING:README.md"
[ -d .claude/rules ] && echo "OK:.claude/rules:$(ls .claude/rules/ 2>/dev/null | wc -l) files" || echo "MISSING:.claude/rules"
[ -f .claude/roadmap.local.md ] && echo "OK:.claude/roadmap.local.md" || echo "MISSING:.claude/roadmap.local.md"
```

Interpret results:
- `CLAUDE.md` missing → **warning**
- `README.md` missing → **warning**
- `.claude/rules/` missing → **warning** (informational)
- `.claude/roadmap.local.md` missing → only report if project type is roadmap → **warning**

Output lines:
```
[✓] Project: CLAUDE.md present, .claude/rules/ (3 files)
[⚠] Project: README.md missing
```

#### 3e. Schemas (not in --quick mode)

Only for project types that use rootline. Check that `.stem` files are present where expected.

| Mode / Type | Expected .stem locations |
|-------------|-------------------------|
| `--for discover` | `lines/.stem`, `theories/.stem`, `MAP.md` parent dir |
| `--for roadmap` | Value of `roadmap-root` from `.claude/roadmap.local.md` |
| auto-detect TYPE:discover | `lines/.stem`, `theories/.stem` |
| auto-detect TYPE:roadmap | Roadmap root dir (read from `.claude/roadmap.local.md`) |
| `--full` | All of the above + any directory containing `.md` files with YAML frontmatter |

```bash
# Check expected .stem locations
for dir in lines theories; do
  if [ -d "$dir" ]; then
    [ -f "$dir/.stem" ] && echo "OK:$dir/.stem" || echo "MISSING:$dir/.stem"
  fi
done
```

Interpret results:
- Directory exists but `.stem` missing → **warning** (docs in that dir won't validate)
- Directory does not exist → skip (not applicable)

Output lines:
```
[✓] Schema: lines/.stem present
[⚠] Schema: theories/.stem missing — discover docs won't validate
```

#### 3f. Kubernetes Health (TYPE:k8s, --full, --for workload)

Only if `kubectl` is available AND project type includes k8s. Uses `KUBECONFIG=~/.kube/config-k3s`.

```bash
# 1. Pods not ready or in bad state (excludes Completed/Succeeded jobs)
KUBECONFIG=~/.kube/config-k3s kubectl get pods -A --no-headers 2>/dev/null | awk '$4 != "Running" && $4 != "Completed" && $4 != "Succeeded" {print $1"/"$2": "$4}'

# 2. Pods with containers not ready (READY column mismatch, e.g. 0/1)
KUBECONFIG=~/.kube/config-k3s kubectl get pods -A --no-headers 2>/dev/null | awk -F'[ /]+' '$3 != $4 && $5 != "Completed" && $5 != "Succeeded" {print $1"/"$2": "$3"/"$4" ready"}'

# 3. Pods with high restart count (>5)
KUBECONFIG=~/.kube/config-k3s kubectl get pods -A --no-headers 2>/dev/null | awk '$5 > 5 {print $1"/"$2": "$5" restarts"}'

# 4. HelmReleases not Ready
KUBECONFIG=~/.kube/config-k3s kubectl get helmreleases -A --no-headers 2>/dev/null | awk '$3 != "True" {print $1"/"$2": Ready="$3}'

# 5. PVCs not Bound
KUBECONFIG=~/.kube/config-k3s kubectl get pvc -A --no-headers 2>/dev/null | awk '$3 != "Bound" {print $1"/"$2": "$3}'

# 6. Services without endpoints
KUBECONFIG=~/.kube/config-k3s kubectl get endpoints -A --no-headers 2>/dev/null | awk '$2 == "<none>" {print $1"/"$2": no endpoints"}'

# 7. Flux sources not ready (GitRepository, HelmRepository)
KUBECONFIG=~/.kube/config-k3s kubectl get gitrepositories,helmrepositories -A --no-headers 2>/dev/null | awk '$3 != "True" {print $1"/"$2": Ready="$3}'
```

Interpret results:
- Any pods not ready or high restarts → **warning** (not error — could be transient)
- Any HelmReleases not Ready → **error** (indicates failed deployment)
- Any PVCs not Bound → **error** (workload likely broken)
- Services without endpoints → **warning** (could be scaling to zero)
- Flux sources not ready → **error** (GitOps pipeline broken)

Output lines:
```
[✓] k8s: All pods healthy, 0 high-restart, 0 not-ready
[✗] k8s: 1 HelmRelease not Ready — media/jellyfin: Ready=False
[⚠] k8s: 2 pods with high restarts — monitoring/prometheus-0: 8 restarts
[✓] k8s: All PVCs Bound, all Flux sources Ready
[⚠] k8s: 1 Service without endpoints — dev/test-svc
```

#### Skill-specific additional checks (`--for <skill>`)

| Skill | Additional checks beyond CLIs and schemas |
|-------|-------------------------------------------|
| `--for roadmap` | `.claude/roadmap.local.md` must exist and contain `roadmap-root` |
| `--for discover` | `lines/` or `theories/` directories should exist |
| `--for hypothesize` | `intake/` or `docs/research/` directory should exist |
| `--for workload` | `k8s/` directory with manifests should exist |
| `--for instance` | `terraform/proxmox/` directory should exist, check for `.tf` files |

### Step 4: Summary

Count totals and emit result line:

```
RESULT: 0 errors, 0 warnings — environment ready
RESULT: 1 error, 2 warnings — fix errors before proceeding
RESULT: 0 errors, 1 warning — proceed with caution
```

Rules:
- If errors > 0 → `fix errors before proceeding` (and list actionable fixes)
- If warnings > 0 but no errors → `proceed with caution`
- If clean → `environment ready`

---

## Complete Output Format

```
PREFLIGHT — [project-name]
═══════════════════════════

[✓] Git: main branch, clean, synced with remote
[✓] CLI: rootline v0.9.2 available
[✗] CLI: kubectl not found — required for k8s operations
[✓] Rootline: 15/15 files valid, 0 errors
[⚠] Schema: lines/.stem missing — discover docs won't validate
[✓] Project: CLAUDE.md present, .claude/rules/ (3 files)
[✓] k8s: All pods healthy, HelmReleases Ready, PVCs Bound, Flux sources Ready

RESULT: 1 error, 1 warning — fix errors before proceeding

  Fix: install kubectl — https://kubernetes.io/docs/tasks/tools/
```

---

## Actionable Fix Suggestions

When reporting errors or warnings, include a concrete fix when possible:

| Issue | Suggested fix |
|-------|---------------|
| rootline missing | `curl -fsSL https://raw.githubusercontent.com/pablontiv/rootline/master/install.sh \| bash` |
| kubectl missing | `https://kubernetes.io/docs/tasks/tools/` |
| tofu missing | `https://opentofu.org/docs/intro/install/` |
| flux missing | `https://fluxcd.io/flux/installation/` |
| git dirty | `git stash` or `git commit` uncommitted changes |
| git behind remote | `git pull` to sync |
| rootline validation errors | `rootline fix --all .` |
| .stem missing | `rootline init <dir>` to infer schema from existing files |
| CLAUDE.md missing | Create with project description |
| HelmRelease not Ready | `kubectl describe helmrelease -n NS NAME` for error details |
| PVC not Bound | Check PV exists and `claimRef` matches; check StorageClass |
| Pods high restarts | `kubectl logs -n NS POD --previous` for crash reason |
| Flux source not Ready | `kubectl describe gitrepository/helmrepository -n flux-system` |
| Service no endpoints | Check pod selector matches, pod is Ready |

---

## Conventions

- Use `command -v` for CLI detection, never `which`
- Parse `rootline validate` JSON output for error counts
- Do not fail hard on warnings — only errors are blockers
- Keep output concise — one line per check, details only on failure
- Run checks in order: git, CLIs, rootline, project files, schemas
- Total execution should stay under 10 seconds for `--quick`, under 30 seconds for full
