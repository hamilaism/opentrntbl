# CLAUDE.md — Project context for Claude Code

This file is read automatically by [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) when it starts in this repository. It provides the persistent context the AI needs to make good decisions about this codebase. **You don't need to use Claude Code to use this firmware** — but if you do, this file (combined with the memory templates in `.claude/memory-templates/`) will save you a lot of time.

If you're new to vibecoding with Claude Code, see [docs/VIBECODING-WITH-CLAUDE.md](docs/VIBECODING-WITH-CLAUDE.md) first.

---

## The project

**openTRNTBL by ismo** — open-source firmware for the TRNTBL by VNYL turntable. VNYL shut their servers down in 2023 ; this firmware revives the platine by streaming the vinyl signal to Sonos speakers via WiFi (and optionally to a local RCA output).

GPL-3.0 licensed. Non-commercial, community-maintained.

---

## Hardware stack

- **Platine** : TRNTBL by VNYL (main board v1.72)
- **SBC** : C.H.I.P. v1.0 (Next Thing Co., Allwinner R8/A13, 512 MB RAM, Debian Jessie)
- **ADC** : PCM2900C BurrBrown USB (hw:1,0) — **48 kHz mandatory** (44.1 kHz blocks the driver)
- **Audio codec** : sun4i-codec (hw:0,0) — 3.5 mm jack, weak signal → preamp required for clean RCA
- **WiFi** : RTL8723BS — 2.4 GHz only, power management disabled (`rtw_power_mgnt=0`), occasional SDIO lockups (mitigated by `sdio-watchdog.sh`)
- **Motor** : HYEJET-01 / EG-530SD-3F, controlled by ATmega328P (U2)
- **NAND** : Toshiba 4G MLC (erasesize=0x400000, writesize=0x4000, oobsize=0x500), ~15 bad blocks normal
- **UART** : CP2102 on U14 header, 115200 baud
- **RCA** *(optional mod)* : NE5532 module preamp + PAM8403 amplifier between the codec jack and the chassis RCA jacks

See [docs/HARDWARE.md](docs/HARDWARE.md) for pinouts, BOM, and RCA wiring diagram.

---

## Software stack

Two distinct environments : what runs **on the C.H.I.P.** (firmware, hard constraints) and what runs **on your laptop** (tooling, design, build pipelines).

### Firmware (on the CHIP — embedded runtime, hard constraints)

- **OS** : Debian Jessie (NOT Stretch, NOT Python 3)
- **Python** : 2.7 only
- **Streaming** : Darkice (capture hw:1,0 @ 48 kHz) → Icecast2 (MP3, port 8000, mount /vinyl)
- **Portal** : Flask (Python 2.7, port 80, threaded=True)
- **Sonos** : SOAP/UPnP port 1400, native grouping via `x-rincon:RINCON_xxx`
- **mDNS** : Avahi → trntbl.local
- **Captive portal** : hostapd (SSID `TRNTBL-Setup`) + dnsmasq + Flask WiFi setup
- **Boot** : rc.local → start-trntbl.sh (decides AP vs Normal mode)
- **No PulseAudio** — direct ALSA only
- **No npm/pip on the CHIP** — everything via apt (4 GB NAND, 512 MB RAM ; modern toolchain impossible)
- **Vanilla HTML/CSS/JS in `firmware/`** — no framework, no build step (whatever Flask serves must run as-is)

### Tooling (on your laptop — design, generators, firmware build)

No Jessie/Python 2.7/vanilla constraint here. Use what's productive, then **compile** or **copy** artefacts to the CHIP when ready.

- **Python** : Python 3 for generator scripts (design tokens, build tooling)
- **Node / npm** : OK for the design side — Storybook, Tokens Studio, Figma/Penpot plugins
- **Storybook 10.3** : `@storybook/html-vite` — gallery for design tokens, primitives, components
- **Design tokens** : DTCG 2025.10, source in OKLCH, bundles : matrix + Tokens-Studio-compatible
- **Deploy** : `firmware/deploy.sh` copies firmware Mac→CHIP via SCP

The distinction matters : **what goes on the CHIP stays vanilla and lightweight**, but **what generates** what goes on the CHIP (tokens, assets, docs) can leverage a modern toolchain.

---

## Connections

- **SSH** : `ssh root@<YOUR-CHIP-IP>` or `ssh root@trntbl.local` (password : `chip` — Debian Jessie default, change on production deployments)
- **UART** : `screen /dev/tty.usbserial-XXXX 115200` (Mac) / `screen /dev/ttyUSB0 115200` (Linux) / COMx (Windows)
- **Deploy** : `bash firmware/deploy.sh trntbl.local` (or replace with your CHIP IP)
- **Portal** : `http://trntbl.local`

---

## Repo structure

```
firmware/             # Runs on the CHIP (Python 2.7, vanilla JS, ALSA configs)
  app.py              # Flask API + portal
  index.html          # UI (vanilla JS, CSS variables)
  sonos-monitor.sh    # Monitor Sonos state + vinyl priority
  start-trntbl.sh     # Boot script (AP vs Normal, ALSA, WiFi)
  wifi-to-ap.sh       # Runtime AP↔STA transition
  wifi-to-client.sh   # Reconnect to saved WiFi
  sdio-watchdog.sh    # Detect RTL8723BS lockups, recover
  deploy.sh           # Mac→CHIP deploy via SCP

docs/                 # User-facing docs
  FLASH-GUIDE.md      # Reflash NAND (recovery from brick)
  INSTALL-GUIDE.md    # Post-flash setup
  HARDWARE.md         # BOM, pinouts, RCA wiring
  API.md              # HTTP endpoints
  RCA-ARCHITECTURE.md # Why NE5532 → PAM8403 → RCA
  TEST-PLAN.md        # Validation checklist
  VIBECODING-WITH-CLAUDE.md  # Reproduce the dev workflow

design/               # Design system (laptop-side, injected into firmware/index.html via build)
  tokens/
    src/              # Editable DTCG sources (foundations, theme, semantic, icons)
    dist/             # Generated bundles (matrix + Tokens-Studio-compat + Figma payloads)
    scripts/          # Python 3 generators
  components/         # Storybook stories (html-vite)
  icons/              # SVG sources
  research/           # Synthesized notes on DTCG ecosystem (Donnie Damato, Bill Collins, etc.)

.storybook/           # Storybook 10.3 config
.claude/
  memory-templates/   # Anonymized memory examples for vibecoders
```

---

## Conventions

- **Always provide the complete file** when modifying a firmware file — no partial diffs (the CHIP's deploy script overwrites entire files).
- **Don't push features to "V2" when they're broken now** — the project is in alpha, fix what's broken in the current scope.
- **Don't tag releases optimistically** — keep version honest about what's tested vs what's broken.
- **When an approach is a dead-end, say it honestly** — don't pile workarounds.
- **Test commands before suggesting them** — and always specify WHERE each command runs (laptop / UART / VM).
- **Smoke test before freezing** : before committing an install doc (MCP setup, service config, build tool) or pinning a version, run a basic end-to-end call. If it fails, fix it before freezing the doc — otherwise the doc and your memory lie from the first commit. Pinning `@beta` / `-rc` / `-next` is a warning sign, not an acceptable default.
- **Communicate directly, no hedges** — this project values clarity over diplomacy.

---

## Roadmap (high level)

See [ROADMAP.md](ROADMAP.md) for details.

- **V1.0.0-alpha** (current) — alpha publishable, design tokens V1, structural fixes
- **V1.1** (next) — Bluetooth A2DP source, GitHub Actions CI (lint Python + shellcheck)
- **V2.0** (TBD) — Hardware upgrade to Allwinner H6, UPnP/DLNA support beyond Sonos, multi-brand DS via primitives swap

---

## When something is unclear

- Hardware behavior : check [docs/HARDWARE.md](docs/HARDWARE.md) and the BOOT log on `/tmp/trntbl-boot.log` (CHIP-side)
- API behavior : check [docs/API.md](docs/API.md) and `firmware/app.py`
- Design tokens cascade : check `design/tokens/scripts/generate-css.py` (the longest-match resolver)
- Vibecoding workflow / memory system : [docs/VIBECODING-WITH-CLAUDE.md](docs/VIBECODING-WITH-CLAUDE.md)

If you're stuck, opening a GitHub issue is preferable to silent debugging — chances are someone else hit the same wall.
