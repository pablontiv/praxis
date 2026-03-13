---
source: pablontiv/praxis
name: delegate
description: |
  Ejecuta gemini o kimi CLI para enviar trabajo a otro LLM. Preserva la
  cuota de tokens de Claude delegando tareas largas. Usar siempre que el
  usuario mencione gemini, kimi, o quiera otra perspectiva de IA. Triggers:
  "preguntale a gemini/kimi", "ask gemini/kimi", "pásale esto a",
  "usa kimi/gemini para", "delega", "delegate", "que lo resuelva",
  "segunda opinión", "second opinion", "que opine otro", "otra perspectiva",
  "cross-check con", "contrasta con", "verify with", "research with",
  "verify" (para revisar trabajo de Claude con otro modelo). Incluye
  heurísticas de routing automático entre gemini y kimi. NO activar si:
  el usuario pregunta SOBRE gemini/kimi como tema, la tarea es trivial,
  o Claude puede resolverla sin perspectiva externa.
user-invocable: true
argument-hint: "<gemini|kimi|auto> \"prompt\" | verify <gemini|kimi|auto> [focus] | --stdin <path> <target> \"prompt\""
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# /delegate — Multi-LLM Task Delegation

Delegate substantial work to Gemini or Kimi as independent LLM workers in batch mode. Gemini excels as a deep analyst with massive context (1M tokens); Kimi excels as a parallel research army with superior tool orchestration (separate subscription quota). For full model specs, read `references/model-profiles.md`.

## Routing

Parse `$ARGUMENTS` to determine mode, target, and prompt.

| Input pattern | Mode | Target | Prompt source |
|---------------|------|--------|---------------|
| `gemini "..."` | send | gemini | from arguments |
| `kimi "..."` | send | kimi | from arguments |
| `auto "..."` or just `"..."` | send | heuristics decide | from arguments |
| `--stdin path/to/file <target> "..."` | send+file | target or auto | file piped + arguments |
| `verify <target\|focus>` | verify | target or auto | auto-assembled |

Parsing logic:
1. If first token is `verify` → verify mode; next token is target if it matches `gemini|kimi|auto`, otherwise target = `auto` and remaining tokens = focus hint
2. If any token is `--stdin` → extract the path immediately after it
3. First non-flag token matching `gemini|kimi|auto` → target
4. Everything else in quotes or remaining → the prompt
5. If no target specified → `auto`

## Gate Check

Before executing, verify the target CLI is available:

```bash
command -v gemini >/dev/null 2>&1  # For gemini target
command -v kimi >/dev/null 2>&1    # For kimi target
```

If the target CLI is missing, suggest the other as fallback. If both are missing, stop and tell the user to install at least one.

## Heuristic Routing (target = `auto`)

When the target is `auto` or omitted, select the model based on these signals. Check in order — first match wins:

| Signal | Target |
|--------|--------|
| `--stdin` file >5000 lines (massive context that benefits from a second perspective) | **gemini** |
| Scientific/academic deep analysis or literature review | **gemini** |
| Systematic multi-criteria evaluation (vendors, architectures) | **gemini** |
| Large codebase read-only analysis (understand, map, document) | **gemini** |
| Security, auth, or vulnerability-focused review | **gemini** |
| Task naturally decomposable into parallel sub-tasks | **kimi** |
| Task requires heavy tool use (web browsing, search, file ops) | **kimi** |
| Long-running task that would consume significant Claude token quota | **kimi** |
| Verification / second opinion / auditing Claude's work | **kimi** |
| Practical code engineering (refactor, debug, write tests) | **kimi** |
| No clear signal / ambiguous | **gemini** |

When Claude invokes autonomously (not user-initiated), briefly explain the routing decision.

## Send Mode

### Step 1: Build and show the command

**Gemini**: `gemini -p "PROMPT" -o text`
**Kimi**: `kimi --quiet -p "PROMPT"`
**With file**: `cat path/to/file | <target-cmd> "PROMPT"`

If `--stdin` file exceeds 500 lines, warn the user. For gemini this is less critical (1M context); for kimi the 256K limit matters.

Always show the user what's being executed before running it. Summarize piped content:

```
Delegating to gemini:
  cat terraform/proxmox/main.tf [287 lines] | gemini -p "Review for security issues" -o text
```

Execute with Bash tool, timeout 360000ms (6 minutes).

### Step 2: Present the response

Frame the response visually:

```
━━━ DELEGATE → [gemini|kimi] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[raw response from the delegated LLM]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 3: Synthesis

After presenting the delegated response, add your own analysis. Scale the synthesis to the task complexity:

**Simple tasks** (file review, code check, focused question):
- **Key disagreements**: Where you see it differently, and why
- **Recommendation**: What the user should take away

**Complex tasks** (vendor evaluation, architecture review, verify mode):
- **Agreements**: What aligns with your own assessment
- **Disagreements**: Where you see it differently, and why
- **New insights**: Points the other model raised that you hadn't considered
- **Recommendation**: What the user should take away

The value is in the contrast, not in restating what was already said.

## Verify Mode (Cross-Review)

Verify mode packages Claude's recent work and sends it to another LLM for independent review — the "second opinion" pattern.

### Step 1: Gather context

Run in parallel:

```bash
git diff HEAD~3..HEAD --stat 2>/dev/null
git diff HEAD~3..HEAD 2>/dev/null
cat .claude/rules/current-state.md 2>/dev/null
```

Also summarize from the current conversation: what was the task, what decisions were made.

### Step 2: Assemble the review prompt

Read the template from `references/verify-template.md` and fill in the sections with gathered context. Include the user's focus hint in the Specific Focus section.

### Step 3: Execute and synthesize

Same as send mode — build the command, show it, execute, frame the response. Use the complex synthesis format:

- **Valid concerns**: Issues raised that Claude agrees with or hadn't fully considered
- **Disagreements**: Where Claude thinks the review is off-base, with reasoning
- **Action items**: Concrete changes to make based on the review
- **Assessment**: Overall — adjust course or stay the course?

This synthesis is critical. Without it, the user gets two potentially conflicting opinions with no resolution.

## Autonomous Delegation

Claude can invoke `/delegate` without the user asking when it detects that another perspective would improve the outcome.

**When to delegate autonomously**:
- After completing a complex design, delegate a verify to catch blind spots
- When evaluating multiple options and Claude's analysis feels thin
- When the task involves a domain where another model's profile fits better

**When NOT to**: Simple tasks, user in a hurry, sensitive/private information not consented for external sharing.

**Always communicate**: Tell the user what you're delegating and why before executing.

## Examples

```bash
/delegate gemini "Evaluate tradeoffs of Flux CD vs ArgoCD for a small homelab k8s cluster"
/delegate --stdin internal/parser/ast.go kimi "Review for edge cases and potential panics"
/delegate "Compare ZFS mirror vs offsite backup strategies for a 4-drive NAS"
/delegate verify kimi
/delegate verify gemini "focus on the database migration logic"
```

## Conventions

- **Timeout**: 360 seconds (6 minutes). If the CLI times out, report it and let the user decide
- **Retry cap**: Max 2 retries on HTTP 429/5xx errors. After that, fallback to the alternate target. Don't burn time on unlimited retries when the other model is available
- **No retry on other errors**: If the command fails for non-transient reasons, report the error. Don't retry the same command
- **Content filter handling**: If the target LLM rejects the prompt (HTTP 400, "high risk", content policy):
  - For **non-security topics**: rephrase sensitive terminology and retry once ("vulnerability" → "potential correctness issue", "attack vector" → "angle for failure", "exploit" → "misuse scenario", "timing attack" → "timing-based analysis")
  - For **security/auth topics** (the prompt is fundamentally about security review): vocabulary substitutions alone won't work — kimi's content filter triggers on the overall pattern, not individual words. Attempt one sanitized retry if the user explicitly requested kimi, then fallback to gemini with a transparent explanation: "Kimi's content filter rejects security-focused review prompts. Falling back to gemini."
  - When falling back due to content filter, note the limitation in the output so the user understands why their target wasn't honored
- **Truncation**: Warn if piping files >500 lines via `--stdin`. For gemini this is usually fine; for kimi, suggest scoping
- **Show the command**: Always show what's being executed before running it
- **Text output only**: Always use `-o text` for gemini, `--quiet` for kimi
- **Model selection**: Don't specify model flags — both CLIs handle model selection internally
- **Privacy**: Prompts are sent to third-party APIs. Don't include secrets, credentials, or private keys
