# Model Profiles (March 2026)

Understanding why each model is suited for different tasks helps make better routing decisions. These aren't arbitrary preferences — they reflect measurable differences in architecture and training.

## Gemini 3.1 Pro — "El Analista"

The Gemini CLI auto-routes between Gemini 3 Pro and 3 Flash based on task complexity. No need to specify a model — the CLI handles this intelligently.

- **Context**: 1M tokens (4x Kimi) — can ingest entire codebases, long doc sets, full k8s manifests
- **Reasoning**: GPQA Diamond 94.3%, thinking mode is mandatory (always shows its work)
- **Coding**: SWE-bench 80.6% — strong at systematic code analysis
- **Behavior**: Contextual and analytical — good at inferring intent, connecting dots across large inputs, structured evaluation
- **Quota**: Runs on its own subscription quota — delegating here preserves Claude token budget

**Best for**: Tasks requiring deep analysis over large amounts of information. When you need a thorough, structured evaluation of something complex.

## Kimi K2.5 — "El Ejército"

The Kimi CLI uses `kimi-for-coding`, a K2.5-based model optimized for coding tasks with 256K context.

- **Context**: 256K tokens — sufficient for most single-file or focused analysis
- **Architecture**: 1.04T total params, 32B active (MoE) — extremely efficient
- **Tool use**: +20.1pp improvement with tools (2x Claude's +12.4pp), Agent Swarm supports 100 sub-agents and 1,500 coordinated tool calls
- **Reasoning**: HLE with tools 50.2% (beats Claude Opus and GPT-5.2), AIME 2025 96.1%
- **Behavior**: Literal and precise — follows instructions exactly without over-inferring. Aggressive tool orchestration when given agency
- **Quota**: Runs on its own subscription quota — delegating here preserves Claude token budget

**Best for**: Tasks that benefit from precise execution, parallel decomposition, or heavy tool use. Also valuable for offloading long-running work that would otherwise consume Claude's token quota.
