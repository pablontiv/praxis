# Anti-Presupposition Process

Process to detect presuppositions in questions and reformulate them observationally, preventing confirmation bias in inquiry.

## The 5 Steps

### 1. Ask for explicit presuppositions

Ask: "What do you expect to find? What prior experiences influence this question?"

### 2. Detect additional presuppositions

Analyze the question and point out:
- **Verbs that presuppose structure**: components, architecture, works, improves
- **Implicit undeclared expectations**: assumed outcomes, assumed categories
- **Categories assumed to exist**: taxonomies, hierarchies, distinctions taken for granted

### 3. Propose observational reformulation

Generate a version that invites observation, not confirmation:

| Presupposes | Observational |
|-------------|---------------|
| "What components does it have?" | "What do I find when I open...?" |
| "How does it work?" | "What do I observe happening when...?" |
| "Why does X improve Y?" | "What changes with/without X?" |
| "hybrid rules engine" | "automated decision systems" |
| "agent architecture" | "how LLM applications are structured" |
| "best practices for X" | "documented approaches for X" |

### 4. Generate alternative hypotheses

Propose 2-3 alternatives to the user's intuition:
- At least one that **contradicts** the main expectation
- Include a **null option** if applicable (e.g., "perhaps no such thing exists")

### 5. Confirm with user

Present:
- Original question vs reformulated
- Detected presuppositions
- Alternative hypotheses

Ask: "Does this capture what you want to investigate?"

## Context-Specific Application

### In new-line (always apply — full process)

Run all 5 steps. Document results in QUESTION.md:
- Explicit presuppositions section
- Alternative hypotheses section
- Reformulated question (if it differs from original)

### In cycle (check and update)

Check if QUESTION.md has anti-presupposition sections.

**If NOT present** (line created before the process):
1. Offer: "This line was created before presupposition validation. Review the central question with the process before continuing?"
2. If accepted → run full process, update QUESTION.md
3. If declined → note in field log: "User chose not to apply anti-presupposition process"

**If present** — review and update:
1. Are documented presuppositions still relevant?
2. Have new presuppositions emerged since last cycle?
3. Has any hypothesis been confirmed/refuted?
4. Propose updates if the question has evolved. Confirm before modifying.
5. Ask: "Before investigating: is this still the question you want to explore?"

### In research (validate topic before searching)

Before executing searches:
1. Analyze the topic: What does it assume exists? What verbs presuppose structure?
2. Propose broader reformulation if presuppositions detected
3. Generate search queries that include alternatives:
   - Main query (user's topic)
   - Alternative query (broader reformulation)
   - Contrast query (opposite/critique, e.g., "X vs Y", "problems with X")
4. Confirm with user if significant presuppositions found
5. Document in synthesis under "### Topic presuppositions":
   - What the topic assumed
   - What research revealed (if reality differed)
