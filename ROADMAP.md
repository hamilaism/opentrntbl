# openTRNTBL — Product Roadmap

## V1.0.0-alpha — Current release (2026-05-02)

**Status:** Shipped, alpha publishable. Stable for daily use, 24+ h continuous validated, 72 h soak in progress.

**Path to V1.0.0 stable** (no timeline, "when ready") :
- Manual cleanup pass on design assets (Figma + Penpot) by the maintainer — current state was 100 % vibecoded with Claude Code, needs a human eye for finishing touches before declaring stable
- 72 h soak test passed
- NE5532 wiring physically validated by the maintainer (currently documented but not yet wired)
- Community feedback from this alpha incorporated (typos in docs, install path quirks, common bugs)

### What's included

- ✅ WiFi client mode (saved networks, auto-reconnect)
- ✅ WiFi AP fallback (TRNTBL-Setup captive portal, mobile-friendly)
- ✅ Sonos speaker discovery & multiroom grouping (native `x-rincon:`)
- ✅ Stream URL sharing (iOS/Android)
- ✅ Bitrate selection (128/192/256/320 kbps, persistent)
- ✅ Vinyl priority mode (auto-pause on non-spinning, motor sense)
- ✅ Local RCA output *(optional, hardware-dependent — NE5532 + PAM8403 mod)*
- ✅ Output mode toggle (Sonos ↔ RCA)
- ✅ Runtime AP↔STA switching without reboot (`wifi-to-ap.sh` / `wifi-to-client.sh`)
- ✅ SDIO watchdog (RTL8723BS recovery, rate-limited)
- ✅ Design tokens V1 (113 CSS vars, 4 mode axes : color/contrast/vision/density)
- ✅ Accessibility: setup panel a11y (lang + theme + density + contrast + vision daltonism)
- ✅ Structural fixes: subprocess `close_fds` (no more port :80 zombie), scan UX improvements, cold-scan retry pattern

### What's NOT included (parked or pending hardware)

- ⏸ NE5532 hardware mod by maintainer (component ordered, not yet wired — RCA path still needs preamp for clean line-level)
- ⏸ Bluetooth A2DP source (V1.1 target)
- ⏸ GitHub Actions CI (V1.1 target)
- ⏸ UPnP / DLNA support beyond Sonos (V2 target)
- ⏸ Hardware upgrade Allwinner H6 (V2 target)

---

## V1.1 — Bluetooth + CI (target Q3 2026)

### Bluetooth A2DP source

**The platine emits audio to a Bluetooth speaker** (e.g. JBL portable, Bose Soundlink) as an alternative to the Sonos / RCA paths.

**Important UX trade-off** : the RTL8723BS chip on the C.H.I.P. is a **combo BT+WiFi** sharing the same 2.4 GHz radio antenna. This forces architectural choices :

- ✅ **BT will run in *complement* of WiFi, not replacement** — WiFi stays up so the captive portal remains accessible (otherwise pairing/config is impossible without adding hardware buttons)
- ✅ **User toggle in the dashboard** : `Mode = Sonos | Bluetooth` switch
  - In Sonos mode : WiFi up, BT off, audio routed to Sonos speakers
  - In Bluetooth mode : WiFi minimal (just the portal accessible), BT scans for nearby speakers, audio routed to selected BT speaker
- ⚠️ **Expected coexistence trade-offs** :
  - CPU pressure on single-core 1 GHz (already tight on WiFi-only)
  - Possible 2.4 GHz interference (BT and WiFi sharing the same antenna)
  - To mitigate : BT only active when in BT mode (toggled), not always-on background

If coexistence proves impractical on RTL8723BS, fallback : "BT mode" turns WiFi off (loses portal access), and re-entering Sonos mode requires a power cycle to bring WiFi back. We'll measure during V1.1 implementation.

### GitHub Actions CI

- Python lint (`ruff` or `flake8`) on `firmware/*.py`
- Shell lint (`shellcheck`) on `firmware/*.sh`
- JSON schema validation on `design/tokens/src/*.tokens.json`
- Smoke test for `design/tokens/scripts/generate-css.py` (regenerate + diff vs committed)

### Why V1.1, not V2

- BT A2DP source is implementable on existing C.H.I.P. hardware (Bluez + bluez-alsa)
- No hardware change required (chip already supports BT 4.0)
- CI is pure tooling
- Builds on V1.0.0-alpha architecture without breaking anything

---

## V2.0 — Hardware upgrade & broader speaker support (target 2027)

**Major: move away from C.H.I.P. v1.0 (EOL since 2017, single-core bottleneck, RTL8723BS instability).**

### Hardware target: Allwinner H6 or similar quad-core ARM

- Why : 4-core (vs CHIP's single-core)
- Benefits :
  - Darkice + alsaloop simultaneously (current blocker)
  - Faster Sonos discovery (network-heavy)
  - Better thermal profile
  - Modern WiFi/BT chip with stable drivers
  - Room for new features

### New features (V2.0)

- ✨ **UPnP / DLNA speaker support** (not just Sonos) — broader speaker compatibility
- ✨ **Hardware upgrade kit** for existing TRNTBL owners (H6 board + new audio codec + assembly guide)
- ✨ **Multi-device streaming coordination** (sync audio across Sonos + UPnP simultaneously)
- ✨ **Multi-brand design system swap** (the DS architecture is ready : swap the `Brand-openTRNTBL` primitives layer to rebrand the entire UI for hardware variants)

### Hardware upgrade kit (~$80-120 USD, Q4 2027)

- Allwinner H6 dev board
- New audio codec (replaces sun4i-codec)
- RCA circuit improvements (NE5532 already standard)
- NAND + pre-flashed Debian
- Complete assembly guide

---

## V2.1+ — Future considerations (no timeline)

- **Mobile app** (iOS/Android) for remote control beyond web portal
- **Cloud sync** of settings + playlists (optional, privacy-first)
- **Smart home integration** (HomeKit, Google Home)
- **Backup/restore** of config across devices
- **Multi-platine sync** (multi-room vinyl streaming from multiple platines)

---

## Timeline summary

| Version | Scope | Est. delivery | Status |
|---------|-------|---------------|--------|
| **V1.0.0-alpha** | Core WiFi + Sonos + DS + structural fixes | **Shipped 2026-05-02** | 🟢 Released |
| V1.1 | Bluetooth A2DP source + CI | Q3 2026 | ⚪ Planned |
| V2.0 | H6 hardware upgrade + UPnP/DLNA | 2027 | ⚪ R&D phase |
| V2.1+ | Mobile app, cloud, smart home | 2027+ | ⚪ Backlog |

---

## Key decisions & rationale

### Why ship V1.0.0-alpha now (vs wait for everything)
- Core functionality is stable and validated
- Design system V1 is shipped and consumed by the firmware
- Bluetooth and CI are non-blocking — they enhance, don't fix
- Earlier release = earlier community feedback = better V1.1 priorities

### Why V1.1 = BT first, not UPnP
- BT A2DP source is the most-requested feature for vinyl streaming (any portable speaker)
- UPnP requires more abstraction (SOAP/UPnP vs Sonos's specific dialect) — better fit for V2 where we have the H6 CPU headroom

### Why H6 over Raspberry Pi
- H6 has better NAND integration (TRNTBL board compatibility)
- Lower cost (~$30 vs $50+ for RPi 4)
- Allwinner ecosystem proven via C.H.I.P. development
- Mainline kernel support
- Smaller form factor (closer to TRNTBL platine integration)

### Why no commercial offering
- openTRNTBL is 100 % open source, GPL-3.0
- No sales, no consulting, no profit
- Hardware sourcing via curated regional Amazon / Aliexpress links (see `docs/SHOPPING-LISTS.md`)
- Maintainer is doing this for the community, not as a side business

---

## Notes for contributors

- Document architectural decisions in `docs/` (like `docs/RCA-ARCHITECTURE.md`)
- Keep `docs/TEST-PLAN.md` aligned with shipped features
- Mark future work in code : `# TODO V1.1: <feature>` or `# TODO V2: <feature>`
- Version is set in `firmware/app.py` (line 3 docstring) and bumped at release tag
- For roadmap discussion : open a GitHub issue with the `roadmap` label
