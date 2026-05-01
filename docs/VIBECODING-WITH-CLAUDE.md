# Vibecoding openTRNTBL with Claude Code

This is the practical guide on **how this firmware was built**, and **how you can extend / fork / rebrand it** with the same workflow. Everything here is optional — you can use openTRNTBL without ever opening Claude Code. But if you want to ship a feature in 30 minutes instead of 3 hours, this is the path.

---

## What this is (and what it isn't)

**Vibecoding** = working with an AI coding agent that has persistent context about the project. You describe intent in plain language ("add a Bluetooth A2DP source mode"), the agent reads the relevant files, proposes changes, runs tests, and iterates. You stay in the loop : you read diffs, validate, redirect.

**This is not "I push a button and the AI ships my project"**. The AI makes mistakes. Hardware constraints (Python 2.7 ! 512 MB RAM ! bricky NAND !) trip it up. You need to know what good looks like to validate. Vibecoding accelerates a competent developer ; it doesn't replace one.

This guide is specific to **[Claude Code](https://docs.claude.com/en/docs/claude-code/overview)** (Anthropic's terminal CLI agent), but the patterns transfer to other agents (Cursor, Aider, etc.).

---

## Setup (one-time)

### 1. Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

Sign in via browser when prompted. You need an Anthropic API account ([https://console.anthropic.com](https://console.anthropic.com)).

### 2. Clone the repo

```bash
git clone https://github.com/hamilaism/opentrntbl.git
cd opentrntbl
```

### 3. Open Claude Code in the repo

```bash
claude
```

The first thing it does : **read [`CLAUDE.md`](../CLAUDE.md) at the repo root**. That file gives the agent the persistent context it needs (hardware stack, software constraints, repo structure, conventions). You don't need to re-explain "we're on Python 2.7" every conversation — it's already loaded.

### 4. Optional : seed your memory directory with the templates

```bash
mkdir -p ~/.claude/projects/$(pwd | sed 's|/|-|g')/memory
cp .claude/memory-templates/* ~/.claude/projects/$(pwd | sed 's|/|-|g')/memory/
```

The templates in `.claude/memory-templates/` are anonymized memories that capture decisions and patterns useful for *anyone* working on this codebase. They become Claude's persistent knowledge across conversations. (You can also let Claude write its own memories from scratch — but the templates save you a few iterations of teaching it the same lesson twice.)

### 5. Configure the MCP servers you'll use

MCP (Model Context Protocol) servers extend Claude Code with new tool capabilities — SSH into the CHIP, drive Figma, query Penpot, work with GitHub. Below are the MCPs that were used to build this project. None are mandatory, but each unlocks a class of workflow.

#### SSH (deploy to the CHIP)

Lets Claude execute shell commands on the CHIP via SSH and upload firmware files.

```bash
claude mcp add ssh -s user -- npx -y @aiondadotcom/mcp-ssh
```

After install, set up an SSH host alias in `~/.ssh/config` for your CHIP :

```
Host trntbl-root-ip
  HostName <YOUR-CHIP-IP>
  User root
  IdentityFile ~/.ssh/trntbl_ed25519
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
```

(See `docs/INSTALL-GUIDE.md` for SSH key generation if you don't have one.) Then Claude can use `mcp__ssh__runRemoteCommand` and `mcp__ssh__uploadFile` to interact with the CHIP without you manually typing every command.

#### GitHub (PRs, issues, releases)

```bash
claude mcp add github -s user -- npx -y @modelcontextprotocol/server-github
```

Requires a GitHub personal access token with appropriate scopes — set `GITHUB_PERSONAL_ACCESS_TOKEN` env var or follow the server's interactive setup. Useful for opening PRs from Claude, listing issues, creating releases.

#### Figma (design system reproduction)

The "Figma Console" MCP gives Claude access to Figma files via the Desktop Bridge plugin. Used in this project to mirror the design tokens system into Figma variables and components.

```bash
claude mcp add figma-console -s user -e FIGMA_ACCESS_TOKEN=<YOUR-FIGMA-TOKEN> -e ENABLE_MCP_APPS=true -- npx -y figma-console-mcp@latest
```

Then in Figma Desktop, install and run the Desktop Bridge plugin (Plugins → Development → Figma Desktop Bridge → Run). The bridge connects via WebSocket on port 9223 (with fallbacks).

#### Penpot (design system documentation)

Used for the Penpot version of the design system documentation. See `docs/PENPOT-MCP-SETUP.md` for the full setup.

#### Pre-authorize the MCPs (avoid permission prompts for sub-agents)

When Claude spawns a sub-agent in the background (the most powerful workflow), the sub-agent **can't show you permission prompts**. Any MCP tool not pre-allowlisted in `.claude/settings.local.json` will be silently denied for the sub-agent.

A starter template is included : copy `.claude/settings.local.json.example` to `.claude/settings.local.json` and customize. The pattern that matters :

```json
{
  "permissions": {
    "allow": [
      "mcp__ssh",
      "mcp__github",
      "mcp__figma-console",
      "mcp__penpot"
    ]
  }
}
```

`mcp__<server>` (without an explicit `__*` suffix) is interpreted as a wildcard for **all tools of that MCP server**. This is required for sub-agents to be able to use the server. For MCP servers with destructive operations, prefer listing tools explicitly instead.

This is captured in `.claude/memory-templates/reference_claude_perm_subagent.md` for vibecoders who want to understand the rationale.

---

## The 3 patterns that made this project shippable

### A. The memory system

By default, every new conversation with an AI starts from zero. You re-teach it your stack, your conventions, your team's quirks. This wastes hours over a project's lifetime.

Claude Code has a **persistent memory** : you tell the agent "remember this" and it writes a file. Next conversation, it reads those files first. Memories are typed :

- **`feedback_*`** — corrections you've made to its behavior ("don't deploy without my OK", "run smoke tests before pinning a version"). Saves you from repeating the same correction.
- **`project_*`** — facts about the work that aren't in the code ("we're freezing merges Friday", "the auth rewrite is driven by legal"). Decay fast — keep updated.
- **`reference_*`** — pointers to external systems ("bugs tracked in Linear project INGEST", "oncall watches grafana.internal/d/api-latency").
- **`user_*`** — about you (role, expertise level, preferences). Tailors how Claude communicates with you.

Examples are in [`.claude/memory-templates/`](../.claude/memory-templates/). They're anonymized — feel free to copy them as-is and edit, or delete and let Claude rebuild from scratch.

**The biggest win** : `feedback_no_deploy_without_ok.md` (don't push to the CHIP runtime without explicit confirmation) prevented at least 4 incidents during this project's development.

### B. Sub-agents in parallel

Some tasks are big and the AI's main context is precious. Solution : spawn a **sub-agent** in the background to do the heavy lifting (search the codebase, audit a directory, build a Figma reproduction), and let it report back when done.

Example from this project's development :

```
"Lance un agent qui fait l'audit complet de design/research/
pour identifier les contenus tiers à virer, en read-only"
```

The agent runs in the background. You keep working in the main conversation. When it's done, you get a notification with its summary. Saves hours.

**Caveat learned the hard way** : sub-agents tend to over-report their own success ("100 % done, all good !"). Always demand **proofs** in your brief :

> "Don't reproduce the previous agent's mistake : don't tell me 'X/Y % done'. Bring inspectable proofs : screenshots, dumps of bound variables, structures extracted via the API."

A bad sub-agent rapport pattern is "I checked everything and it's all good". A good one is "I checked these 17 files, here's what I found, here's the diff, here's what I couldn't verify and why".

### C. Smoke test before freezing

Before committing an install doc, pinning a version, writing a memory : run a **basic end-to-end call** to verify it actually works. Pin `@beta` or `@latest -rc` is a warning sign, not an acceptable default. If your "5-minute setup doc" doesn't survive a clean clone + first command, it lies starting from the very first commit.

This is captured in `feedback_smoke_test_before_freezing.md`. Worth its weight in saved hours.

---

## Workflow examples

### Adding a firmware feature (e.g., new `/api/sonos/...` endpoint)

```
You : "Add an endpoint POST /api/sonos/volume-master that sets the
       volume of all selected speakers in one call"

Claude : reads firmware/app.py, finds the existing /api/sonos/* handlers,
         reads the SOAP volume command in sonos-monitor.sh,
         proposes a diff, runs Python syntax check via subprocess
         locally, then asks you to deploy to the CHIP and test.

You : (after deploy + test) "It works. Add a memory that the SOAP
       volume action uses the InstanceID=0 / Channel=Master pattern."

Claude : writes that to your memory directory.
```

### Debugging a runtime issue on the CHIP

```
You : "Le portail ne répond plus. SSH marche encore."

Claude : SSH'es into the CHIP, checks 'pgrep python', 'netstat -tlnp',
         'tail /tmp/trntbl-portal.log', identifies that Flask died
         silently. Proposes the fix (e.g., respawn loop in
         start-trntbl.sh) but does NOT deploy without confirmation
         (because of feedback_no_deploy_without_ok.md).

You : "OK go fix"

Claude : pushes the fix, restarts Flask, verifies HTTP 200.
```

### Extending the design system (rebrand, add a token)

```
You : "Je veux ajouter une color 'lime' dans la palette core et la
       brander en 'success.alt' dans openTRNTBL"

Claude : reads design/tokens/src/core.tokens.json, adds the lime scale,
         reads primitives-openTRNTBL.tokens.json, adds the brand alias,
         re-runs design/tokens/scripts/generate-css.py, shows the
         tokens.css diff, asks if you want to apply it to a specific
         component.
```

---

## Anti-patterns to avoid

### "Just trust the agent's summary"

Sub-agents return rapports. Those rapports describe what the agent **intended** to do, not always what actually happened. Verify on the actual artifact :
- For code : `git diff`
- For Figma : `figma_get_variables` direct or `figma_take_screenshot`
- For Penpot : `penpotUtils.shapeStructure` or `mcp__penpot__export_shape`
- For runtime : SSH and check the actual process / port / log

This is captured in `feedback_self_qa_pseudostates.md` (the agent should self-QA the matrix variant × état × mode before claiming "done").

### Letting the agent write features you don't understand

If you can't read the diff and judge whether it's correct, you can't validate. Either learn the topic enough to validate, or scope the work down. **Don't merge AI code you don't understand into your firmware** — especially on hardware that can brick.

### Memory bloat

Don't write memories for every single decision. Memories should capture **non-obvious** things. The fact that `app.py` uses Flask is in the code ; don't memory it. The fact that **deploying mid-test** caused incident X last quarter is non-obvious ; memory that.

A good memory has : a **rule**, a **why** (so you can judge edge cases later), and a **how-to-apply** (so future you knows when it kicks in).

### Re-asking the same question every conversation

If you find yourself re-explaining "we're on Python 2.7" or "no `npm install` on the CHIP" : write that to `CLAUDE.md` (project-level, always loaded) or to a `project_*` memory. Saves time, reduces drift.

---

## Roadmap for the vibecoding side of openTRNTBL

If you contribute via Claude Code, here are some patterns worth extending :

- **CI integration** : a GitHub Action that runs the same lints Claude runs locally (Python lint, shellcheck on `firmware/*.sh`, JSON schema validation on tokens). Currently : not in place. PR welcome.
- **Test harness in CI** : currently the smoke tests live in your conversations with Claude. A real test suite (pytest for `app.py` API, shellcheck for shell, vitest for the Storybook stories) would reduce manual smoke tests.
- **Memory linting** : Claude's memories drift. A linter that reads `~/.claude/projects/*/memory/` and flags stale ones (last touched > 60 days, or claims about file paths that no longer exist) would help. Not built — would be a nice meta-tooling project.

---

## Further reading

- [Claude Code documentation](https://docs.claude.com/en/docs/claude-code/overview) — official.
- [Anthropic's "Building with the Claude SDK" cookbook](https://github.com/anthropics/claude-cookbooks) — patterns and examples.
- [`.claude/memory-templates/`](../.claude/memory-templates/) — start here to seed your memory directory.

If you ship something interesting using this workflow, open a PR or an issue — happy to learn from your variants.
