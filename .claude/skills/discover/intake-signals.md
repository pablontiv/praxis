# Intake Signals Reference

Guide for analyzing external files and classifying them into the appropriate flow entry point.

## Signal Extraction

Read the file completely and extract these 7 signals. Each is deterministic — based on observable characteristics, not interpretation.

### 1. Format

Detect from file extension and content structure:

| Value | Detection |
|-------|-----------|
| `markdown` | `.md` extension, heading structure |
| `code` | Programming language extension (`.py`, `.js`, `.ts`, `.go`, etc.) |
| `data` | `.json`, `.yaml`, `.csv`, `.xml`, or structured data without prose |
| `prose` | `.txt`, `.doc`, or long paragraphs without markdown structure |
| `mixed` | Combines code blocks with prose, or multiple formats |
| `binary` | `.pdf`, `.png`, `.jpg`, `.xlsx`, or non-text content |

### 2. Structure level

Count headings (`#`, `##`, etc.), tables, and list sections:

| Value | Criteria |
|-------|----------|
| `flat` | 0-2 sections, no tables |
| `structured` | 3-8 sections, may include tables or lists |
| `deep` | 9+ sections, nested hierarchy |

### 3. Assertion density

Ratio of declarative statements to questions/exploratory language:

| Value | Criteria |
|-------|----------|
| `low` | <30% declarative — mostly questions, "maybe", "what if", "I wonder" |
| `medium` | 30-70% declarative — mix of claims and exploration |
| `high` | >70% declarative — "X is Y", "we need", "this will", definitive statements |

### 4. Evidence presence

Scan for citations, URLs, data references, measurements, benchmarks:

| Value | Criteria |
|-------|----------|
| `none` | No supporting references |
| `anecdotal` | 1-3 URLs, informal references, "I've seen", personal experience |
| `systematic` | 4+ sources, structured citations, data tables, benchmark results |

### 5. Actionability

Scan for next steps, TODOs, requirements, specifications:

| Value | Criteria |
|-------|----------|
| `none` | Descriptive/analytical only |
| `implicit` | "we should", "it would be good to", "consider" — without specs |
| `explicit` | Clear requirements, acceptance criteria, task lists, specs, APIs defined |

### 6. Domain specificity

Density of technical jargon, named tools, frameworks, APIs:

| Value | Criteria |
|-------|----------|
| `generic` | No specialized terminology |
| `domain-specific` | Industry jargon, named tools/frameworks, but not implementation-level |
| `technical` | API names, code references, architecture patterns, implementation details |

### 7. Completeness

Scan for placeholders, TBDs, empty sections, question marks in content:

| Value | Criteria |
|-------|----------|
| `draft` | Many gaps, "TBD", empty sections, mostly questions |
| `partial` | Some sections complete, others pending |
| `complete` | All sections filled, no placeholders |

---

## Entry Point Mapping

Combine signals to classify the file into one of 5 entry points:

| Signal profile | Entry point | Action |
|----------------|-------------|--------|
| flat + low assertions + no evidence | **BACKLOG** | `/discover new-line` — create line of inquiry, full anti-presupposition |
| structured + high assertions + none/anecdotal evidence | **HYPOTHESIZE (direct)** | `/hypothesize` — extract claims as propositions, falsify |
| structured + systematic evidence + partial/complete | **HYPOTHESIZE (follow-up)** | `/hypothesize [adapted file]` — parse state, continue investigation |
| high actionability + explicit specs + domain-specific/technical | **ROADMAP** | `/roadmap` — decompose into epics/features/stories/tasks |
| code or data format | **CONTEXT** | Attach as evidence to existing line or create new line with this as initial material |

### Priority rules

When signals point to multiple entry points:
1. If **explicit actionability** + **technical** → ROADMAP wins (the document is ready to decompose)
2. If **high assertions** + **no/anecdotal evidence** → HYPOTHESIZE wins (claims need validation)
3. If **systematic evidence** exists → HYPOTHESIZE (follow-up) wins (research to continue)
4. When still ambiguous → apply **Glaser Test** as tiebreaker

---

## Glaser Test (tiebreaker)

For each candidate entry point, evaluate:

| Criterion | Question |
|-----------|----------|
| **Fit** | Does the file's content naturally belong in this skill's domain? |
| **Work** | Would this skill's process actually advance understanding of the material? |
| **Relevance** | Does the file address concerns that this skill handles? |
| **Grab** | Is there substantial material for this skill to work with? |

Scoring: 3+ yes = strong match, 2 = possible, 0-1 = poor fit.

---

## Adaptation Templates

### For BACKLOG → `/discover new-line`

```
ADAPTATIONS:
1. Extract the central question from the document
2. Run anti-presupposition process on that question
3. File content becomes initial context in QUESTION.md
4. Any URLs/references become starting material for Cycle 1
```

### For HYPOTHESIZE (direct) → `/hypothesize`

```
ADAPTATIONS:
1. Extract N claims as explicit propositions (C1-CN)
2. Separate facts (constraints) from assumptions (claims to test)
3. Empty/TBD sections map to unknown CAPs
4. Existing URLs/references become initial evidence in Matriz Premisa-Evidencia
5. Named tools/frameworks become evaluation targets
```

### For HYPOTHESIZE (follow-up) → `/hypothesize [file]`

```
ADAPTATIONS:
1. Map existing sections to 5-phase structure
2. Identify which phase the document is effectively in
3. Convert evidence to Matriz Premisa-Evidencia format (✅/⚠/❓/❌)
4. Identify gaps — which phases need completion
5. May require reformatting the file header to include `> Estado: Fase N`
```

### For ROADMAP → `/roadmap`

```
ADAPTATIONS:
1. Identify epic-level objectives from document goals
2. Extract features from requirement sections
3. Convert TODOs/tasks to story-level descriptions
4. Identify dependencies between sections
5. Flag any claims that should be validated first (/hypothesize)
```

### For CONTEXT (code/data)

```
ADAPTATIONS:
1. Determine if there's an active line this relates to
2. If yes → add as evidence/reference in that line's FIELD-LOG.md
3. If no → suggest creating a new line with this as initial material
4. For code: identify what questions the code answers or raises
5. For data: identify what patterns or claims the data supports
```
