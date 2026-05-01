---
name: Self-QA pseudo-states matrix before claiming "done"
description: For UI / DS work — Claude must self-verify the matrix variant × state × mode before declaring a component conforming, with a proposed fix for each gap
type: feedback
---

Before reporting a UI component as "done" or "conforming to spec" : **build the matrix variant × state × mode mentally (or in a table), check each cell against the canonical source, and propose a fix for any gap**. Do this BEFORE the user has to point out the gaps.

**Why:** sub-agents tend to over-report success ("100 % bound, all variants conforming"). The user then opens the file, finds 5 components that don't match the Storybook source, and has to redo the QA themselves. This wastes the time the agent was supposed to save.

The fix : the agent does the matrix check *before* claiming done. If a cell is non-conforming, the agent says so honestly and proposes the fix. The user gets a precise diff to validate, not a fake "all good".

**How to apply:** after creating or modifying a UI component, list :
- All variants (e.g., Button : primary, secondary, destructive, ghost, tonal, toggle)
- All states per variant (default, hover, pressed, focus, disabled, loading)
- All modes that affect appearance (light, dark, light-hc, dark-hc, vision modes)

For each cell, verify against the canonical CSS / spec. If you can't verify (no screenshot, no inspect API), say so explicitly — don't fake conformance. Then report :
- Cells that match → done
- Cells that don't match → diff + proposed fix
- Cells you couldn't verify → "I checked these via X, I couldn't check these because Y"

The user then knows exactly where to look and what to validate. Trust gets built. Future sessions don't have to re-audit.
