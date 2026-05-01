# Memory templates for openTRNTBL contributors

These are **anonymized memories** that capture decisions and patterns from the development of openTRNTBL. They're useful as a starting point if you're contributing via Claude Code.

## How to use

```bash
# 1. Find your Claude memory directory (path depends on your repo location)
MEM=~/.claude/projects/$(pwd | sed 's|/|-|g')/memory
mkdir -p "$MEM"

# 2. Copy the templates
cp .claude/memory-templates/*.md "$MEM/"

# 3. Edit MEMORY.md to add the index lines (see existing memories for format)
```

After this, every new conversation with Claude Code starts with these memories pre-loaded as context.

## What's in here

| File | Type | Why it matters |
|---|---|---|
| `feedback_no_deploy_without_ok.md` | feedback | Prevents accidentally nuking the CHIP runtime mid-test |
| `feedback_smoke_test_before_freezing.md` | feedback | Catches dead docs / broken pinned versions before they're committed |
| `feedback_self_qa_pseudostates.md` | feedback | Forces the AI to self-QA matrix variant×state×mode before declaring done |
| `project_ds_aliasing_taxonomy.md` | project | The 4-layer DS taxonomy (primitive / brand / semantic / component) |
| `project_state_taxonomy.md` | project | config (variant) vs interaction (state) vs focus (orthogonal) |
| `project_ds_status_as_tone.md` | project | Why `status.*` is the only transverse tone layer |
| `project_donnie_hover_pattern.md` | project | Hovers calculated via color-mix(), not static tokens |
| `reference_claude_perm_subagent.md` | reference | Allowlisting MCP servers for sub-agents in `.claude/settings.local.json` |

These cover : safety (don't break runtime / don't ship lies), DS architecture (4 layers, state taxonomy, hover pattern), and tooling (sub-agent permissions).

## Customize freely

Delete what you don't need. Edit the others to match your project's reality. The goal is to give Claude enough context that it doesn't ask you the same architectural questions every conversation.

## Format reminder

Each memory file is :
```markdown
---
name: Short title
description: One-line summary (used to decide relevance)
type: user | feedback | project | reference
---

The memory body. For feedback/project, structure as :
- Rule / fact (one paragraph)
- **Why:** the reasoning (often a past incident or constraint)
- **How to apply:** when this kicks in
```

`MEMORY.md` (in the same directory) is just an index — one line per memory file, pointing to the file with a hook describing what it captures.
