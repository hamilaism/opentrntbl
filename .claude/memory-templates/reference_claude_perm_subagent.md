---
name: Allowlist MCP servers for sub-agents in .claude/settings.local.json
description: Sub-agents in background can't show permission prompts — they're auto-denied on any MCP tool not pre-allowlisted. Add `mcp__<server>` (without explicit wildcard) to allow all tools of that server.
type: reference
---

When you spawn a sub-agent in the background (via the `Agent` tool), it inherits the session's MCP server configurations but **NOT** the session's permission state. The main conversation can show "Allow this tool ?" prompts and you accept ; sub-agents can't show prompts so they're auto-denied.

**Symptom :** sub-agent reports `"All tools mcp__<server>__* refused"` even though the MCP server is connected and the main conversation can use it normally. Often only `mcp__<server>__get_status` works (because it's commonly pre-allowlisted historically).

**Fix :** add an entry to `.claude/settings.local.json` under `permissions.allow` :

```json
{
  "permissions": {
    "allow": [
      "mcp__figma-console",
      "mcp__penpot__execute_code",
      "mcp__penpot__high_level_overview",
      "mcp__ssh__runRemoteCommand",
      "mcp__ssh__uploadFile"
    ]
  }
}
```

The pattern `mcp__<server>` (without explicit `*` or `__*` suffix) is interpreted as a **wildcard for all tools of that MCP server**. Verified : after adding `mcp__figma-console`, sub-agents could call `figma_search_components`, `figma_get_variables`, `figma_execute`, `figma_create_variable_collection`, `figma_take_screenshot`, etc. (126 tool calls in one run, no denial).

For servers with destructive operations (deploy, payment, bulk delete), prefer **listing tools explicitly** instead of wildcarding. Example for `mcp__github__*` : list `mcp__github__create_issue`, `mcp__github__get_pull_request`, etc. — but NOT `mcp__github__delete_repository` unless you really want sub-agents to be able to delete repos.

**When to use :** every time you spawn a sub-agent that depends on an MCP server not yet allowlisted for sub-agents. More efficient than listing each tool individually (less typing, covers future tools of the server).

**When NOT to use :** for MCP servers with critical side-effects, prefer explicit tool listing over wildcard.

**How to apply :** before launching a sub-agent that uses `mcp__<server>__*`, check `.claude/settings.local.json` and add the prefix entry if absent. If you're unsure which scope (wildcard vs explicit), look at the server's tool list and assess the blast radius.
