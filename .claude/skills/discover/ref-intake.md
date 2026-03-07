# Subcommand: intake — Full Procedure

Analyze an external file and classify it into the appropriate flow entry point.

**Trigger**: `$ARGUMENTS` starts with `@`. Strip the `@` to get the file path.

## Process

1. **Read the file** completely. If it doesn't exist, inform the user.

2. **Fast-path check**: If the file has markers from existing skills, it's NOT external — redirect:
   - `> Estado: Fase N` → already a `/hypothesize` document → suggest `/hypothesize [file]`
   - QUESTION.md/FIELD-LOG.md template markers → already a `/discover` artifact → suggest the appropriate subcommand
   - Roadmap frontmatter (`tipo:`, `estado:`, `epic:`) → already a `/roadmap` artifact → suggest `/roadmap pending` or `/roadmap loop`

3. **Extract 7 signals**: See [intake-signals.md](intake-signals.md) — "Signal Extraction" section.
   Each signal is deterministic and observable — count sections, scan for patterns, check extension. No interpretation.

4. **Classify**: Map signals to entry point using the mapping table in [intake-signals.md](intake-signals.md) — "Entry Point Mapping" section. If ambiguous, apply **Glaser Test** (same section).

5. **Anti-presupposition scan**: Run the anti-presupposition process on the file content.
   See [anti-presupposition.md](anti-presupposition.md) — steps 2-3 (detect presuppositions + observational reformulation).
   Focus on: what does the document assume without validating?

6. **Suggest adaptations**: Based on entry point, describe what the file needs to enter the flow.
   See [intake-signals.md](intake-signals.md) — "Adaptation Templates" section.

7. **Present results**: Show signal profile, classification, presuppositions, adaptations, and recommended command. Always include alternatives so the user can override.

## Output format

```
INTAKE — [filename]
═══════════════════

SIGNALS:
  Format:        [value]
  Structure:     [value] ([detail])
  Assertions:    [value] ([count] claims, [count] questions)
  Evidence:      [value] ([detail])
  Actionability: [value] ([detail])
  Domain:        [value] ([named items])
  Completeness:  [value] ([detail])

CLASSIFICATION: [entry point]
Confidence: [high/medium/low]

PRESUPPOSITIONS DETECTED:
├─ "[claim]" — [why it's a presupposition]
├─ "[claim]" — [why]
└─ "[claim]" — [why]

SUGGESTED ADAPTATIONS:
1. [adaptation]
2. [adaptation]
N. [adaptation]

COMMAND: [recommended command]

ALTERNATIVES:
  [alternative 1] — [when to choose this instead]
  [alternative 2] — [when to choose this instead]
```

## Edge cases

- **Binary files** (images, PDFs): Format = binary → always CONTEXT
- **Very short files** (<5 lines): Treat as a topic → BACKLOG
- **Empty files**: Inform user, suggest starting with `/discover new-line` instead
- **Code files**: Classification = CONTEXT — suggest attaching as evidence to an existing line

## Notes

Intake never auto-executes a skill — it classifies, suggests, and hands off. The user decides.

**File lifecycle**: After classification, the original file stays in `intake/`. Generated artifacts (lines, backlog entries) reference it via `[[intake/name]]` wikilinks. The file leaves `intake/` only when the research graduates to `/hypothesize` or `/roadmap`. One intake file can generate multiple artifacts (lines, backlog items, theories) — this is expected.
