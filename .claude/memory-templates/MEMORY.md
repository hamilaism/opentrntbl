# MEMORY.md (template — copy to your real memory directory)

This is an example of how to structure the `MEMORY.md` index in your real Claude memory directory. Each line is one memory file with a one-line hook.

```
- [No deploy without OK](feedback_no_deploy_without_ok.md) — never write to runtime/deploy without explicit confirmation
- [Smoke test before freezing](feedback_smoke_test_before_freezing.md) — verify install docs / pinned versions actually work end-to-end
- [Self-QA pseudo-states](feedback_self_qa_pseudostates.md) — matrix variant×state×mode self-check before claiming "done"
- [DS aliasing taxonomy](project_ds_aliasing_taxonomy.md) — 4 layers: primitive / brand / semantic / component, alias only if it carries a decision
- [State taxonomy](project_state_taxonomy.md) — config (variant) vs interaction (state) vs focus (orthogonal)
- [Status as tone](project_ds_status_as_tone.md) — status.* is the only transverse tone, no general tone layer
- [Donnie hover pattern](project_donnie_hover_pattern.md) — hovers via color-mix(), not static tokens
- [Claude perm sub-agent](reference_claude_perm_subagent.md) — allowlist MCP servers in .claude/settings.local.json for sub-agents
```

## Format rules

- One line per memory file, under ~150 chars
- Hook = "what's this about" in 5-15 words, not the full content
- Group thematically (feedbacks together, projects together, references together) for readability
- Order by frequency of relevance, most-loaded first

## Loaded automatically

This `MEMORY.md` file is **always loaded into your conversation context** at the start of every Claude Code conversation in this project. The individual memory files (`feedback_*.md`, etc.) are NOT loaded automatically — Claude reads them on-demand when the description in MEMORY.md matches the current task.

So : keep MEMORY.md tight (truncated past line 200), descriptive (so the relevance check works), and current (delete dead memories).
