---
name: Smoke test before freezing (docs, memories, pinned versions)
description: Before committing an install doc, writing a memory claim, or pinning a dependency version — run an end-to-end test that actually passes
type: feedback
---

Before committing a setup doc (MCP install, service config, build pipeline), writing a memory claiming "X works", or pinning a dependency version : **run a basic end-to-end call that actually passes**. If it fails, fix it before freezing the doc — otherwise the doc and the memory lie from the very first commit.

**Why:** a doc that doesn't survive a clean clone + first command is worse than no doc at all (it costs trust and debug time when others hit the failure). Memories that capture "X works" without verification become stale fast and mislead future conversations. Pinning `@beta`, `@latest -rc`, `@next`, or any pre-release is a warning sign that the dependency isn't actually production-ready — accept it only with conscious tradeoff documented.

**How to apply:** after writing a setup doc, run the install path from a fresh state and verify the success criterion. After writing a memory like "MCP X is configured and working", actually call one of its tools and confirm it returns a real response (not a "Server not initialized" or generic OK). When tempted to pin a `-rc` version, check why the stable isn't enough first. The smoke test is 2 minutes ; the dead doc costs 2 hours later.

Concrete checks for this project :
- New MCP setup doc → run `mcp__<server>__<basic_tool>` and confirm non-error response
- New `firmware/deploy.sh` flag → deploy to a CHIP and verify the new behavior fires
- New token in `design/tokens/src/` → re-run `generate-css.py` and grep for the resolved value in `tokens.css`
