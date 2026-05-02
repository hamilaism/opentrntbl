# openTRNTBL by ismo

**Resurrect your TRNTBL vinyl turntable.** Stream to Sonos speakers via WiFi, with optional local RCA output.

> VNYL shut down their servers in 2023. Your TRNTBL is now dead hardware. This firmware brings it back to life.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Status: alpha](https://img.shields.io/badge/status-alpha-orange.svg)
![Hardware: C.H.I.P.](https://img.shields.io/badge/hardware-C.H.I.P.%20v1.0-purple.svg)

<img width="600" height="auto" alt="White VNYL turntable seen from a three-quarter angle, with a transparent platter, gold tonearm and mounted cartridge, on a pink background." src="https://github.com/user-attachments/assets/711335dd-0ef0-46bb-8afb-9d9c6ee72e81" />

## UI

<img width="400" height="auto" alt="OpenTRNTBL Wi-Fi captive portal on iOS — network connection screen with available networks list loading, a Rescan button and a manual entry option." src="https://github.com/user-attachments/assets/518dc4dc-3d98-4550-b004-391324e1f904" />
<img width="400" height="auto" alt="OpenTRNTBL main app interface — turntable status showing 'Waiting for a record', connected to ORBI65 network, with a list of available Sonos speakers (Bedroom One, Living Room Beam, Sonos Roam, Vynil Port) and an Audio Stream section." src="https://github.com/user-attachments/assets/6b44858b-0d46-458b-a1c2-1a548eec7784" />


---

## ⚠️ Disclaimer

**This firmware modifies the bootloader and the NAND of the C.H.I.P. SBC.** If you interrupt the flash process or follow the wrong steps, you can render your hardware unusable (a "brick"). **Proceed at your own risk.** The author declines any liability for damaged hardware. If you brick the C.H.I.P., the [FLASH-GUIDE](docs/FLASH-GUIDE.md) explains how to recover via FEL/fastboot — but recovery is not always guaranteed.

---

## 🎵 What It Does

1. **Capture vinyl** — USB audio from your turntable's ADC (PCM2900C BurrBrown @ 48 kHz)
2. **Stream to Sonos** — Native multiroom grouping via SOAP/UPnP, no extra apps
3. **Local RCA output** *(optional)* — Direct analog out via NE5532 + PAM8403 mod
4. **Bitrate control** — 128/192/256/320 kbps, persistent across reboots
5. **Vinyl priority** — Auto-pause when vinyl stops spinning (motor sense)
6. **Captive WiFi setup** — Falls back to AP mode if no saved network, mobile-friendly portal

---

## 🛒 Where to Get the Hardware

VNYL is gone since 2023. The C.H.I.P. SBC was EOL'd by Next Thing Co. in 2017. Both are second-hand only :

- **TRNTBL platine** : eBay, Discogs, Reverb, Facebook Marketplace (rare, ~150-300 €)
- **C.H.I.P. v1.0** : eBay, AliExpress (older listings), Tindie occasional restocks (~25-60 €)
- **Optional RCA mod parts** : NE5532 module preamp (Amazon/AliExpress, ~5-10 €), PAM8403 board (~3-5 €). See [HARDWARE.md](docs/HARDWARE.md).

If you don't already own a TRNTBL, this project is probably not for you — it's a niche revival, not a new product.

---

## 🚀 Getting Started

The path depends on your C.H.I.P. state :

### A. Easy path — your C.H.I.P. boots and is on WiFi

You already have SSH access (`ssh root@<YOUR-CHIP-IP>`, default password `chip`) :

```bash
git clone https://github.com/hamilaism/opentrntbl.git
cd opentrntbl
bash firmware/deploy.sh trntbl.local    # or replace with your CHIP IP
```

Then access **http://trntbl.local** from any device on your WiFi.

### B. From scratch — fresh C.H.I.P. or bricked

You need to **flash the NAND first**, then deploy :

1. **[FLASH-GUIDE.md](docs/FLASH-GUIDE.md)** — Reflash the C.H.I.P. NAND with Debian Jessie via FEL (Mac fastboot)
2. **[INSTALL-GUIDE.md](docs/INSTALL-GUIDE.md)** — Post-flash setup (WiFi, SSH key, networking)
3. Then run the Easy path above

Total time A → B → ready : **~30-60 min** depending on familiarity.

### Access points after deploy

- **Web portal** : http://trntbl.local (or http://`<YOUR-CHIP-IP>`)
- **SSH** : `ssh root@trntbl.local` (password : `chip`)
- **Stream URL** : http://trntbl.local:8000/vinyl (share to iOS/Android browsers)

---

## 🏗️ Architecture

### Hardware Stack

| Component | Model | Purpose |
|-----------|-------|---------|
| **SBC** | C.H.I.P. v1.0 (Allwinner R8/A13) | 1 GHz single-core ARM, 512 MB RAM |
| **WiFi** | RTL8723BS | 2.4 GHz only ; power management disabled (`rtw_power_mgnt=0`) |
| **USB ADC** | PCM2900C BurrBrown | 48 kHz only (driver limitation) |
| **Audio Codec** | sun4i-codec | 3.5mm jack out (low signal — needs preamp for RCA) |
| **Turntable Motor** | HYEJET-01 / EG-530SD-3F | Controlled by ATmega328P (U2 on main board) |
| **Storage** | Toshiba 4G NAND | ~15 bad blocks (normal) |
| **RCA preamp** *(optional)* | NE5532 dual op-amp | Boosts weak jack output to line-level |
| **RCA amp** *(optional)* | PAM8403 (3 W + 3 W) | Drives RCA outputs |

### Software Stack

| Layer | Tech | Port | Notes |
|-------|------|------|-------|
| **OS** | Debian Jessie | — | Python 2.7 only ; no PulseAudio |
| **Streaming** | darkice → Icecast2 | 8000 | MP3 encoder ; captures hw:1,0 (USB ADC) at 48 kHz |
| **Portal** | Flask (Python 2, threaded) | 80 | ~30 ms response, captive portal in AP mode |
| **Sonos API** | SOAP/UPnP | 1400 | Native `x-rincon:` grouping (no middleware) |
| **Discovery** | avahi (mDNS) | 5353 | Hostname : `trntbl.local` |
| **AP fallback** | hostapd + dnsmasq | 2.4 GHz | SSID : `TRNTBL-Setup`, no password |
| **Boot** | rc.local → start-trntbl.sh | — | Decides AP vs Normal mode based on saved WiFi |

### Deployment Flow

```
deploy.sh (your laptop)
  ├─ SCP firmware files → /tmp/opentrntbl-deploy/ (CHIP)
  └─ SSH remote commands :
       ├─ Move files to /home/chip/opentrntbl/
       ├─ Configure /etc/hostapd/, /etc/dnsmasq.conf, /etc/avahi/avahi-daemon.conf
       ├─ Set WiFi power mgmt : /etc/modprobe.d/8723bs.conf
       ├─ Purge Python .pyc files (prevents marshal errors post-flash)
       ├─ Start Flask : python app.py (background, supervised)
       └─ Verify : netstat port 80
```

---

## 🎮 API Reference

Full endpoint documentation in [docs/API.md](docs/API.md). Key endpoints :

- `GET /api/status` — Dashboard state (WiFi, Sonos, bitrate, uptime)
- `POST /api/sonos/select` — Add/remove a speaker from the stream
- `POST /api/settings/bitrate` — Change bitrate (128–320 kbps)
- `GET /api/wifi/scan` — List available networks
- `POST /api/wifi/connect` — Connect to a network with password
- `POST /api/wifi/disconnect` — Erase saved WiFi → reboot to AP mode

---

## 🎨 Design System

The web portal UI is built on a **DTCG-compliant design tokens system** (113 CSS variables) with 4 mode axes :

- **Color** : light, dark
- **Contrast** : default, enhanced (HC for low vision)
- **Vision** : default, deuteranopia, protanopia, tritanopia, achromatopsia
- **Density** : default, compact, spacious

The system is structured in 4 strict layers (`primitive → brand → semantic → component`), each carrying a specific kind of decision. Source in `design/tokens/src/` (DTCG JSON), generators in `design/tokens/scripts/`, Storybook gallery in `design/components/`.

**Inspirations** : the architecture builds on the public work of [Donnie d'Amato](https://donnie.damato.design/) (color systems, `color-mix()` hover pattern), [Bill Collins](https://github.com/billycollins) (token architecture, longest-match cascade), [Ness Grixti](https://nessgrixti.com/) (DS methodology), and David Fusilier (mode composition).

→ Full architecture details, mode axes specifics, generator pipeline, and extension guide in **[`docs/DESIGN-TOKENS.md`](docs/DESIGN-TOKENS.md)**.

---

## 🤖 Built with Claude Code

This project was **co-developed with [Claude Code](https://docs.claude.com/en/docs/claude-code/overview)** (Anthropic's terminal-based AI agent). ~80% of commits include `Co-Authored-By: Claude`. The repository ships with a **vibecoding template** that other people can reuse to extend or fork the project :

- [`CLAUDE.md`](CLAUDE.md) : project context for Claude Code (stack, conventions, constraints)
- [`docs/VIBECODING-WITH-CLAUDE.md`](docs/VIBECODING-WITH-CLAUDE.md) : how to set up Claude Code for this repo, memory templates, sub-agent workflow, **MCP servers detailed setup** (SSH, GitHub, Figma, Penpot)
- [`.claude/memory-templates/`](.claude/memory-templates/) : anonymized memory examples (feedback, project, reference)
- [`.claude/settings.local.json.example`](.claude/settings.local.json.example) : starter template for permission allowlist (pre-authorize commands and MCP wildcards so sub-agents work without prompts)

You don't need Claude Code to use this firmware. It's just a transparent record of how it was built, and a starter kit if you want to extend it the same way.

---

## 🧪 Stability & Testing

**Validated** :
- Power cycle → boot → dashboard accessible (under 30 s on a clean install)
- WiFi switching (AP mode ↔ client mode) without reboot
- Captive portal trigger on iOS (auto-detect)
- Multiroom Sonos grouping, native sync
- 24+ h continuous uptime under load

**Not yet validated post-V1.0.0-alpha** :
- 72 h soak test
- RCA output (NE5532 mod not wired by maintainer at time of release)

See [docs/TEST-PLAN.md](docs/TEST-PLAN.md) for the full test matrix.

---

## 🛠️ Troubleshooting

**Portal won't load**
- Check WiFi : `ssh root@trntbl.local "cat /tmp/trntbl-wifi-mode"` → should print `normal`, not `ap`
- Check Flask : `ssh root@trntbl.local "pgrep -a python"`
- Check logs : `ssh root@trntbl.local "tail /tmp/trntbl-portal.log"`

**No Sonos speakers found**
- Ensure speakers are on the same WiFi as the C.H.I.P.
- Click "Rescan" in the portal — first scan can be empty if speakers are slow to respond
- Verify in Sonos app that speakers show as connected

**WiFi keeps disconnecting**
- WiFi power management is already disabled in `start-trntbl.sh`
- Move the C.H.I.P. closer to the router (it's a 2.4 GHz only chip on a small antenna)
- Check for 2.4 GHz interference (avoid channels 1, 6, 11 if possible)

**Audio crackle / sync lag**
- Try lowering bitrate from 320 to 256 kbps if your network is congested
- Check CPU load (`ssh root@trntbl.local "uptime"`) — single-core CHIP can max out under heavy network load

---

## 📚 Documentation

| Doc | What it covers |
|---|---|
| [FLASH-GUIDE.md](docs/FLASH-GUIDE.md) | Reflash NAND from scratch (FEL + fastboot) — recovery from brick |
| [INSTALL-GUIDE.md](docs/INSTALL-GUIDE.md) | Post-flash setup (WiFi, SSH, deploy script) |
| [HARDWARE.md](docs/HARDWARE.md) | Pinouts, schematics, BOM, RCA wiring with NE5532 + PAM8403 |
| [API.md](docs/API.md) | Full HTTP API reference for the portal |
| [RCA-ARCHITECTURE.md](docs/RCA-ARCHITECTURE.md) | Why the two-level RCA control exists |
| [TEST-PLAN.md](docs/TEST-PLAN.md) | Validation checklist before releasing |
| [VIBECODING-WITH-CLAUDE.md](docs/VIBECODING-WITH-CLAUDE.md) | How this project was built with Claude Code, and how to do the same. Includes detailed MCP setup (SSH / GitHub / Figma / Penpot) |
| [DESIGN-TOKENS.md](docs/DESIGN-TOKENS.md) | Design system architecture (4 layers, 4 mode axes, DTCG pipeline, generator scripts, Storybook gallery, credits) |
| [PENPOT-MCP-SETUP.md](docs/PENPOT-MCP-SETUP.md) | Setup the Penpot MCP server (for design system contributors) |
| [ROADMAP.md](ROADMAP.md) | Versioning + future work |
| [CHANGELOG.md](CHANGELOG.md) | What changed in each release |

---

## 🤝 Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for code style and testing on real hardware.

**Good first issues** (look for the `good first issue` label on GitHub) :
- Add support for non-Sonos UPnP/DLNA speakers
- Bluetooth A2DP source mode
- Multi-brand design tokens swap (the DS architecture is ready, just needs new primitive sets)
- 33/45 RPM motor calibration UI

If you want to extend the firmware substantially, the [`design/research/`](design/research/) folder has my synthesized notes on the DTCG ecosystem (Donnie Damato, Bill Collins, David Fusilier, Ness Grixti) — useful background for design system contributions.

---

## 👤 About

**openTRNTBL by ismo** — 100 % open-source, non-commercial. No sales, no consulting, no profit. Just a dead turntable brought back to life because VNYL shut their servers and a few hundred owners were left with bricks.

**Why open-source ?**
- VNYL is gone ; you own your hardware now
- The community can improve it, fix bugs, adapt to future Sonos API changes
- Transparency : you see exactly what code is running on your device

---

*Released under [GPL v3](LICENSE). Built with Claude Code. Last updated: 2026-05-02 — V1.0.0-alpha*
