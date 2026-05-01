# Penpot MCP setup

Connects Claude Code to the Penpot account to read / modify design files,
sync tokens, push components, etc.

## Active mode (2026-04-29) — remote 2.15

Since Penpot 2.15, the local mode (`npx @penpot/mcp` + plugin manifest)
is no longer used. Everything goes through the hosted endpoint
`https://design.penpot.app/mcp/stream?userToken=…`.

### Setup

1. **Generate the key** in the Penpot UI:
   - https://design.penpot.app → avatar → **Your account**
   - **Integrations** tab → **MCP Server**
   - Enable the feature → **Generate MCP key**
   - Copy the full URL (format
     `https://design.penpot.app/mcp/stream?userToken=…`) — shown
     **only once**.

2. **Add the MCP** on the Claude Code side (user scope, so available across
   all projects):
   ```bash
   claude mcp add --scope user --transport http penpot \
     "https://design.penpot.app/mcp/stream?userToken=YOUR_KEY"
   ```

3. **Verify the connection** before relaunching:
   ```bash
   claude mcp list | grep penpot
   # → penpot: https://design.penpot.app/... (HTTP) - ✓ Connected
   ```

4. **Relaunch Claude Code**. The 5 `mcp__penpot__*` tools appear at
   session startup (the inventory is fixed at boot, no hot-reload).

### Exposed tools (5, low-level)

- `mcp__penpot__execute_code` — workhorse, runs JS through the Plugin SDK
- `mcp__penpot__high_level_overview` — summary of the current context
- `mcp__penpot__penpot_api_info` — API surface
- `mcp__penpot__export_shape` — export a shape as an image
- `mcp__penpot__import_image` — import an image into the design

No native `list_projects`, `get_file`, etc. To list projects:

```js
mcp__penpot__execute_code({ code: 'penpot.getProjects()' })
```

### Why remote rather than local

- No more `npx @penpot/mcp` to babysit in the background
- No more Penpot plugin to load via local manifest
- No more "@beta broken in prod" bug (the version is managed by Penpot)
- Possibly also fixes the *SDK 2.14.1 loses tokens past the last walked one*
  bug noted in local mode (to be re-tested on a bulk push).

## Known pitfalls

### Two Claude profiles on the same machine

On this machine there is `~/.claude.json` (default profile) and
`~/.claude-perso/.claude.json` (active profile for this repo). `claude mcp
add --scope user` writes to the **active** profile at the time the
command runs — confirm by reading the `File modified: …` that the
command prints.

### Local-scope masking user-scope

If an old penpot config remains in `local` scope (project-private config),
it overrides the user scope:

```bash
claude mcp remove penpot -s local   # remove the stale one
claude mcp list | grep penpot       # check there's only one entry
```

### Smoke test if tools are missing after relaunch

```bash
curl -m 5 -o /dev/null -w "HTTP %{http_code}\n" \
  "https://design.penpot.app/mcp/stream?userToken=YOUR_KEY"
```

- **HTTP 406** = endpoint alive (refuses bare GET, normal — MCP handshake
  expects POST with specific headers). This is healthy.
- **HTTP 401 / 403** = invalid or revoked key → regenerate.
- **HTTP 404 / timeout** = the endpoint is down or the URL is wrong.

### Revoke / regenerate the key

In the Penpot UI → **Integrations** → **MCP Server** → **Revoke**, then
**Generate** again. On the Claude side:

```bash
claude mcp remove penpot -s user
claude mcp add --scope user --transport http penpot \
  "https://design.penpot.app/mcp/stream?userToken=NEW_KEY"
```

## Local mode (legacy — do not use except for special cases)

The old mode `npx -y @penpot/mcp@latest` + plugin manifest at
`http://localhost:4400/manifest.json` is still possible but has been
abandoned because it required babysitting the process and had plugin SDK
2.14.1 bugs. To be reconsidered **only** if the remote goes down or to
debug a specific case.

## Official documentation

- Penpot MCP: https://help.penpot.app/mcp/
- Penpot main repo: https://github.com/penpot/penpot
