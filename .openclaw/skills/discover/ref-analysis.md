# Discover Analysis Subcommands Reference

## Subcommand: interlink

Scan system and add wikilinks `[[name]]` where mentions are detected.

### Process

1. **Check existing links via rootline** (if available):
   ```bash
   rootline graph . --check
   ```

2. **Build entity list**: folder names from lines/, theories/, backlog/.

3. **Search**: For each .md file, find mentions NOT already inside `[[...]]`. Exclude code blocks, URLs, file paths.

4. **Propose changes**: Show summary with file, line, and proposed wikilink. Ask: apply all / review one by one / cancel.

5. **Apply**: Edit files, report changes, suggest `/discover update-map`.

6. **Orphan concepts** (optional): If frequent mentions of concepts without files, ask about creating stubs.

**Don't modify**: skill directories, templates.

---

## Subcommand: review-patterns

Evaluate maturity of emergent patterns.

### Process

1. **Extract patterns**: Query rootline for theories by confidence level (if available), then supplement with `connections.md` "Emergent Patterns" section:
   ```bash
   rootline query theories/ --where 'confianza == "emergent"' --output table
   rootline query theories/ --where 'confianza == "developing"' --output table
   rootline query theories/ --where 'confianza == "consolidated"' --output table
   ```
   If rootline unavailable, extract patterns from `connections.md` manually.

2. **Quantitative score**:
   | Criterion | Points |
   |-----------|--------|
   | Mention in different cycle | +1 |
   | Mention in different line | +2 |
   | Appears in CLOSURE.md | +3 |

3. **Qualitative maturity** (for score >= 5):
   | Criterion | Question |
   |-----------|----------|
   | Clear conditions | When does it apply / NOT apply? |
   | Counter-examples | Cases where it failed? |
   | External connection | Papers, books, frameworks? |
   | Explanatory mechanism | WHY it works, not just THAT it works? |
   | Prediction | Can it anticipate new results? |

   Classification: 4-5 criteria = Theory, 2-3 = Principle, 0-1 = Observation.

4. **Show results** and ask: formalize with `/discover theory`, continue, or add to backlog.

**Key principle**: Many mentions != mature theory. High score is a proxy, not proof.

---

## Fork Detection (proactive behavior)

Not a subcommand — Claude applies this during any interaction.

### When to detect

- Responding about a topic NOT the central question of the active line
- A concept/tool/question emerged that deserves its own exploration
- User expressed interest in something tangential
- Research revealed something broadening the scope

### Diagnostic question

> "Is this new element part of the essential experience of the phenomenon we're exploring, or is it external context or theoretical curiosity?"

| Category | Action |
|----------|--------|
| Essential experience | Incorporate without asking |
| External context | Mention, maybe to backlog |
| Theoretical curiosity | To backlog or discard |

### If significant divergence

Present:
```
**Possible fork detected**
Current topic: [describe]
Active line: [[line-name]] — [central question]
My assessment: [category]
Options:
1. Continue here — part of current exploration
2. New line — deserves its own inquiry (/discover new-line [name])
3. To backlog — interesting but not urgent
```

### Glaser Test (if in doubt)

| Criterion | Question |
|-----------|----------|
| Fit | Connects with what we know about this line? |
| Work | Explains or resolves something about the central question? |
| Relevance | Addresses real concerns in this line? |
| Grab | Substantial magnetism? |

3+ yes = essential, 2 = context, 0-1 = curiosity.
