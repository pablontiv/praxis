# Subcommand: init — Full Procedure

Initialize an R&D project in the current directory.

## Process

1. **Validate**: Check if `MAP.md` already exists. If yes, warn and ask to confirm overwrite.

2. **Create directory structure**:
```
intake/
backlog/
lines/
theories/
paused/
closed/
shared/code/
shared/patterns/
shared/templates/
.claude/rules/
```

**intake/** is the reference library for the discover framework. Files arrive here via `/discover @file` and stay while they're being investigated. Lines, backlog items, and theories reference intake docs via `[[intake/name]]` wikilinks. A file leaves `intake/` only when it graduates out of discover entirely — to `/hypothesize` (formal falsification) or `/roadmap` (implementation decomposition).

3. **Copy templates** from [templates/](templates/) to `shared/templates/`:
   - [QUESTION.md](templates/QUESTION.md)
   - [FIELD-LOG.md](templates/FIELD-LOG.md)
   - [CLOSURE.md](templates/CLOSURE.md)
   - [THEORY.md](templates/THEORY.md)

4. **Copy FRAMEWORK.md**: Copy [FRAMEWORK.md](templates/FRAMEWORK.md) to project root as methodology reference.

5. **Suggest CLAUDE.md setup**: If the project doesn't have a CLAUDE.md, suggest the user create one referencing the generated `.claude/rules/` files. Do not auto-generate — users should own their CLAUDE.md.

6. **Generate state files**:

   `.claude/rules/current-state.md`:
   ```markdown
   # Current State
   > Last updated: [today's date]
   ## Active Lines
   (none yet)
   ## Paused Lines
   (none)
   ## Closed Lines
   (none)
   ## Last Session
   - [today's date]: Project initialized
   ```

   `.claude/rules/connections.md`:
   ```markdown
   # Discovered Connections
   ## Between Lines
   (no connections yet)
   ## Emergent Patterns
   (no patterns yet)
   ## Connections with Theories
   (none yet)
   ```

7. **Generate MAP.md** at project root:
   ```markdown
   # System Map
   > Last updated: [today's date]
   ## Structure
   ### /intake (Reference library)
   | Document | Classification | Referenced by |
   |----------|---------------|---------------|
   (empty)
   ### /backlog (Unexplored questions)
   | Question | Topic |
   |----------|-------|
   (empty)
   ### /lines (Active lines of inquiry)
   | Line | Central question | Cycles | Status |
   |------|-----------------|--------|--------|
   (none yet)
   ### /theories (Emergent theories)
   | Theory | Confidence | Connections |
   |--------|-----------|-------------|
   (none yet)
   ### /paused
   (none)
   ### /closed
   (none)
   ### /shared (Reusable artifacts)
   - /code: [empty]
   - /patterns: [empty]
   - /templates: QUESTION.md, FIELD-LOG.md, CLOSURE.md, THEORY.md
   ## Known Connections
   (none yet)
   ## Emergent Patterns
   (none yet)
   ## Current Context
   - **Active lines**: 0/3
   - **Last session**: [today's date] — Project initialized
   ```

8. **Confirm** to user with summary of what was created and next steps: `/discover new-line [name]`, `/discover status`.

**Notes**: Only creates structure — never overwrites existing line data. Templates are copied to the project so they can be customized per-project.
