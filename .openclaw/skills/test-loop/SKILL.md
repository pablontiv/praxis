---
source: pablontiv/praxis
name: test-loop
description: |
  Test runner inteligente que parsea fallos, agrupa por causa raíz, sugiere
  fixes, y re-ejecuta hasta que pasan. Detecta framework automáticamente
  (go, npm, cargo, pytest). Usar este skill siempre que el usuario diga:
  correr tests, arreglar tests, tests fallando, por que fallan los tests,
  hacer pasar los tests, run tests, fix tests, debug test failures, broken
  tests, test errors, CI errors — incluso si no dice "test loop" e incluso
  si solo pega un error de CI, dice "algo está roto", o menciona que el
  build falló.
user-invocable: true
argument-hint: "[path] [--once]"
---

# Test Loop

Intelligent test runner that parses failures, groups them by root cause, suggests fixes, and re-runs until green (or the user cancels).

## Procedure

### Step 1: Parse arguments

Read `$ARGUMENTS` for optional inputs:
- A **path** (e.g. `./internal/extract` or `src/utils`) to scope test execution.
- The `--once` flag to run tests a single time without entering the fix loop.

### Step 2: Detect test framework

Inspect the project root (and the target path, if provided) to determine the test command:

| Indicator file | Test command |
|---|---|
| `go.mod` | `go test ./... -race` (or `go test -race ./path/...` if path given) |
| `package.json` | `npm test`, `yarn test`, or `bun test` (check lockfile: `yarn.lock` -> yarn, `bun.lockb` -> bun, otherwise npm) |
| `Cargo.toml` | `cargo test` (or `cargo test -p <package>` if path given) |
| `pyproject.toml` or `requirements.txt` | `pytest` (or `pytest path/` if path given) |

If multiple indicators exist and the framework is ambiguous, ask the user which to use before proceeding.

### Step 3: Run tests and capture output

Execute the detected test command. Capture both stdout and stderr in full.

### Step 4: Parse failures

From the test output, extract each failure's:
- **Test name**
- **File path and line number**
- **Error message / assertion detail**

Then **group failures by root cause**:
- Identical or near-identical error messages -> same group.
- Failures in the same file with the same error type -> same group.
- Related assertion patterns (e.g. same expected-vs-actual field) -> same group.

### Step 5: Prioritize groups

Order groups by severity, highest first:
1. **Compilation / build errors** — nothing else can pass until these are fixed.
2. **Runtime panics / crashes** — nil pointer, index out of bounds, segfaults.
3. **Assertion failures** — wrong values, missing fields, incorrect state.
4. **Timeouts / hangs** — tests that exceeded time limits.

### Step 6: Present results

Display a clear summary using this format:

```
TEST-LOOP -- <test command>
===========================

RUN <n>: <passed> passed, <failed> failed, <skipped> skipped

GROUP 1: <short root-cause description> (<count> failure(s))
|-- <TestName> (<file>:<line>)
|-- <TestName> (<file>:<line>)
Root cause: <one-line explanation of why these tests fail>

GROUP 2: ...
```

If all tests pass, report success and stop.

### Step 7: Fix loop

**Skip this step if `--once` was specified.**

For each group, starting with the highest priority:

1. **Read the relevant source and test files** to understand context.
2. **Suggest a fix** — explain what to change and why.
3. **Ask the user for approval** before applying the fix.
4. **Apply the fix** upon approval.
5. **Re-run tests** (same command as Step 3).
6. **Re-parse and re-present** results (back to Step 4).

Repeat until one of:
- All tests pass.
- 5 iterations have been completed (warn the user and ask whether to continue).
- The user cancels.

## Important guidelines

- Always show the full test command being executed so the user knows what is running.
- Never silently modify code. Always explain the proposed fix and get approval first.
- When re-running after a fix, clearly indicate which run number it is (RUN 2, RUN 3, etc.).
- If a fix introduces new failures, call that out explicitly and offer to revert.
- Keep explanations concise. Focus on the root cause and the minimal change needed.
- If the test suite is large and slow, suggest scoping to the failing package/file for faster iteration, then confirm the full suite at the end.
