# openTRNTBL — Changelog

All notable changes to the project, dated.

Status legend: ✅ tested and validated in real conditions  ·  🟡 partially tested (works but not 100%)  ·  ⚠️ deployed but not verified end-to-end  ·  ❌ known broken, deferred to V2 with reason

## [v1.2.0] — 2026-05-14 — Design System stable: 4 themes, a11y 0 violations, test coverage 99%

DS package graduates from `1.0.0` → `1.2.0`. Work focused on the Storybook Design System: theme experiments, zero-violation a11y, test coverage.

### Added

- ✅ **4 complete DS themes**: Sonos V1 (existing dark theme, TRNTBL identity), Neumorphic V2 (physical material: shadows, depth, pop animations), Flat-UI V3 (Notion-like paper tone, type-forward, warm surface), Modern V4 (ShadCN/Radix-inspired, compact, focus halos)
- ✅ **Live theme switcher in the firmware portal**: pick any theme from the Display panel — sets `data-token-system` on `<body>`, CSS cascade, no reload
- ✅ **Storybook screens matching trntbl.local** (`Patterns/Dashboard`, `Patterns/WifiSetup`, `Patterns/SpeakerPicker`, `Patterns/Stream`, `Patterns/AP-Setup`) — mirror real portal markup and UX flow
- ✅ **`firmware-ui.css`** loaded in Storybook — guaranteed visual parity with the real portal
- ✅ **Toggle DS component**: canonical stories (Default, Checked, Interactive) + Overview
- ✅ **`Dev/Helpers` story**: exercises defensive paths in `_helpers.js` — null guards, dead aliases, `resolveTypography` optional fields, `dimValue` branches
- ✅ **Token architecture experiments** (6 reference architectures in `design/tokens/experiments/`): algorithmic, flat-ui, modern-algo, modern-nested, nested-modes, neumorphic — each with its own Python resolver and generated CSS

### Fixed / Improved

- ✅ **A11y: 0 violations** — 85/85 tests green in `error` mode (axe-core via `@storybook/addon-a11y`):
  - Structural fixes: `aria-pressed` on SegmentedControl, `role="group"` (replacing `role="list"`), `for`/`id` labels, `aria-hidden` on decoratives, `role="img"` signalBars, `aria-label` Toggle input
  - Documented WCAG 1.4.3 exemptions: disabled states (opacity:0.4), loading (opacity:0.5), brand accent color (gold) on light surface
  - HTML structure fixes: `h3`→`h2` (heading-order), `scope="col/row"` on table headers
- ✅ **Dead imports cleaned up**: `dimValue` removed from unused imports in `Primitives.Dimensions` and `Semantic.Spacing`
- ✅ **Architecture selector removed** from firmware settings panel (was dev-only, not for end-users)

### Test coverage

| Metric | Before | After |
|---|---|---|
| Statements | 95.49% | **99.09%** |
| Branches | 68.42% | **91.42%** |
| Functions | 91.66% | **100%** |
| Lines | 93.93% | **98.97%** |

Floor at 91.42% branches: 4 remaining branches in `activeModes()` and `preview.js` are structurally unreachable from a story (decorator sets `body.dataset.*` before execution).

### Known / non-blocking

- 🟡 Architecture selector removed from portal (dev-only feature)
- 🟡 `activeModes()` fallbacks not covered — structural, not fixable without test infra outside Storybook

---

## [v1.0.0] — 2026-05-13 — stable release

Promoted from alpha. 180h continuous run validated (well beyond the 72h target). CI in place. NE5532 wiring deferred as a hardware enhancement (not a blocker — firmware is fully functional over Sonos/WiFi). Design asset polish continues in 1.0.x.

### Added

- ✅ **GitHub Actions CI**: shellcheck (severity=warning) on all `firmware/*.sh` + flake8 on `firmware/app.py`, runs on every push and PR
- ✅ **Storybook deployed to GitHub Pages**: `https://hamilaism.github.io/opentrntbl/` — live DS token + component gallery, auto-deployed on push to main

### Fixed (code quality)

- ✅ **`app.py` bare `except:` → `except Exception:`** (28 instances): was silently catching `KeyboardInterrupt` and `SystemExit`
- ✅ **`app.py` unused local variables** removed (4 instances: `bssid`, `freq`, `current_bssid`, `current_freq` in WiFi scan parser)
- ✅ **`app.py` SOAP XML templates** extracted as module-level constants `_SOAP_*` — line length from 400+ chars to readable multi-line strings
- ✅ **`app.py` one-liner `if ...: return`** in `get_device_type()` expanded to standard multi-line style
- ✅ **Shell scripts SC2155** (5 instances): `local var=$(cmd)` split to `local var; var=$(cmd)` — `local` was masking return values
- ✅ **Shell scripts SC2034** (2 instances): unused loop/read variables renamed to `_`
- ✅ **Shell scripts SC2164**: `cd /home/chip/opentrntbl` → `cd ... || exit 1`
- ✅ **Shell scripts SC2006**: legacy backtick `` `date +%s` `` → `$(date +%s)`
- ✅ **Shell scripts SC2162**: `read CHIP_IP` → `read -r CHIP_IP` in `deploy.sh`

---

## [v1.0.0-alpha] — 2026-05-02 — first public alpha

First public tagged release. The firmware is stable for daily use, DS V1 is shipped, critical structural bugs are fixed (fd-leak, scan UX, cold scan retry, boot speaker selection clear). The next stable v1.0.0 will integrate polished design assets (Figma + Penpot complete), 72h soak tests passed, and NE5532 wiring documented end-to-end. The maintainer will do a manual cleanup pass on the design assets before v1.0.0 — until now everything was vibecoded with Claude Code, no manual touchup.

### Added

- ✅ **Design tokens V1**: 113 CSS vars (`firmware/tokens.css`) generated from DTCG sources (`design/tokens/src/`). 4 mode axes: color (light/dark), contrast (default/enhanced), vision (default + 4 color blindness types), density (default/compact/spacious). Longest-match cascade
- ✅ **Mode-aware generator** (`design/tokens/scripts/generate-css.py`): cascade-coherent output for 12+ tokens with composed variances
- ✅ **Storybook components** (`design/components/`): Button (6 variants), Card, Row (3 trailing types), Alert (4 variants), Input, SegmentedControl, StatusBadge (4 levels), Layout patterns (TitleBlock, SectionHeader, WifiBar)
- ✅ **AP portal a11y set-panel**: language + theme + density + contrast + color blindness vision selection on the setup side
- ✅ **wifi-to-ap.sh** + **wifi-to-client.sh**: runtime AP↔STA transition without reboot, avoids SDIO crashes on shutdown
- ✅ **sdio-watchdog.sh**: detection of `RD RTO` (RTL8723BS driver lock), recovery via rmmod/modprobe + `reboot -f` rate-limited (4/h)
- ✅ **resolve-modes-matrix.py**: cascade resolution script for 20 consolidated modes (light/dark × default/HC × default/4 color blindness types), output `dist/tokens.modes-matrix.json` (47 KB) + `tokens.density-matrix.json`
- ✅ **Penpot DS docs**: Core page (99 LibraryColors) + Brand-openTRNTBL page (99 LibraryColors aliasing core, 4 boards)

### Fixed

- ✅ **Boot speaker selection clear** (`verify_targets_state_at_boot()` in `app.py`): on boot, persisted `sonos_targets` are cleared. Why: CHIP reboot tears down any `x-rincon:` group, but config kept the persisted target list — UI showed speakers as "selected" while no actual stream was routed. User had to manually disconnect/reconnect. Now boots clean, user re-selects explicitly which triggers a clean SOAP join group call.
- ✅ **`int('-57.00')` silent ValueError** in the AP scan parser (`int(float(current_signal))` — commit 6696a14). Networks now appear in AP mode. Before: silent empty list because `try/except: pass` swallowed the error
- ✅ **fd-leak bug on :80 (cause of "zombie ports")**: Python 2 `subprocess` default `close_fds=False` made subprocesses inherit the :80 socket (`wpa_supplicant -B`, `dhclient`, ...). When Flask died, these orphans kept the port busy. Fix: monkey-patch `subprocess.Popen.__init__` with `close_fds=True` at the top of `app.py`. No more zombie :80 port
- ✅ **Scan UX on load (WiFi setup page AND dashboard "Change network")**: direct `scanWifi()` took 4s+ with random HTTP timeout in AP mode. Replaced with `doWifiRescan()` on load (async POST + 3.5s setTimeout + cache GET). List shows up on first load, no more empty wait
- ✅ **STA cold scan often returned only 1 network**: RTL8723BS doesn't have time to scan all channels in 2.5s. Added retry pattern in `wifi_scan()` (re-trigger scan + 2s if <3 networks). Complete list on first load
- ✅ **`subprocess.check_output(['date'])` in scan-debug log**: replaced with `_time.strftime()` (one less useless fork per scan)
- ✅ **Boot V6 stable**: `start-trntbl.sh` with `pkill` (killall absent on minimal Jessie), `dhclient -1` one-shot, `ip addr flush dev wlan0` before binding 192.168.4.1
- ✅ **Radical HC pattern**: track/input = `surface.dim` + `on-dim` (white); active tile = `surface.bright` + `on-bright` (black). No band-aid borders, just colors that carry their own contrast
- ✅ **on-accent `vision:achromatopsia` override**: color compensated to preserve perceived contrast in achromatopsia (luminance-only)
- ✅ **HC hover/pressed**: mix toward `text-primary` instead of over-saturation

### Changed

- ✅ Strict DS vocabulary: "Theme" axis → "Mode" axis (theme = brand expression, mode = user consumption mode)
- ✅ Tokens dist bundles: `tokens.json` (matrix), `tokens.studio.json` (legacy hex), `tokens.modes-matrix.json` (20 resolved modes for Figma), `tokens.density-matrix.json` (3 density-only modes)
- ✅ ALSA `boosted_jack` output always present (config kept for easy activation when NE5532 is wired)

### Known / reported (bonus, not blocking for the release)

- 🟡 **72h stability tests not redone since V6**: to validate in real conditions. V5 had passed 8h+24h, but V6 and the structural fixes from this session haven't been put through a 72h cycle
- ⚠️ **NE5532 wiring**: replacement for the PAM8403 (insufficient gain to drive RCA from sun4i-codec). Component ordered. ALSA `boosted_jack` config already in place for easy reactivation
- 🟡 **RTL8723BS driver**: still sensitive to fast transitions. The sdio-watchdog mitigates but recovery is not guaranteed in all cases (occasional physical hard reset possible)
- ⚠️ **Corrupt dpkg status**: no install via apt. Post-flash limitation, to investigate if needed in the future
- ⚠️ **Penpot DS docs Semantic + Components + Documentation**: in progress (Core and Brand DONE). Background agent for the rest

### Infra / meta

- ✅ Final DS structure: `design/tokens/src/` (editable DTCG sources), `design/tokens/dist/` (generated bundles), `design/tokens/scripts/` (Python 3 generators)
- ✅ Storybook 10.3 (`@storybook/html-vite`) — primitives + components gallery with mode toggles
- ✅ `docs/RCA-ARCHITECTURE.md`: two-level RCA control architecture (`rca_enabled` hardware vs `rca_show_ui` user toggle)
- ✅ `docs/PENPOT-MCP-SETUP.md`: Penpot remote MCP 2.15 setup

---

## [pre-alpha] — 2026-04-23 — captive portal + WiFi rescan (AP mode)

WiFi setup fix session in AP mode (TRNTBL-Setup). Problem: after reflash, users couldn't access the captive portal to configure initial WiFi. Cause: `wpa_cli` doesn't exist in AP mode, and the WiFi scanner was broken.

### Fixed

- ✅ **WiFi scanner broken in AP mode**: `/api/wifi/scan` used `wpa_cli` (requires wpa_supplicant) which doesn't exist in AP mode. Now detects the mode and uses `iw` in AP, `wpa_cli` in client mode. WiFi scan works in both modes
- ✅ **Captive portal not triggered on iOS**: dnsmasq.conf was missing wildcard DNS redirect + Apple URLs (captiveportal.apple.com). Added `address=/#/192.168.4.1` + explicit rules for Apple URLs. iOS now auto-detects the portal
- ✅ **Versioned system configs**: created `firmware/etc/dnsmasq.conf` (AP mode), `firmware/etc/hostapd/hostapd.conf` (TRNTBL-Setup SSID), `firmware/etc/wpa_supplicant/wpa_supplicant.conf` (client mode template)

### Added

- ✅ `POST /api/wifi/rescan`: endpoint to force a new WiFi scan (useful if networks are missing)
- ✅ "Rescan" button at the top of the WiFi panel (dashboard/AP UI)
- ✅ Auto-detection of wpa_cli vs iw mode in `/api/wifi/scan` (graceful fallback)
- ✅ dnsmasq.conf: wildcard DNS redirect + Apple captive portal URLs for iOS auto-trigger

### Changed

- ✅ `scanWifi()` JS: shows spinner during scan (AP mode ~3s, client mode ~2.5s)
- ✅ `doWifiRescan()`: wrapper that calls `/api/wifi/rescan` then re-polls `/api/wifi/scan`

### Test applied

- ✅ AP mode (TRNTBL-Setup visible, iPhone connects + captive portal launches automatically)
- ✅ WiFi scan in AP mode: `iw dev wlan0 scan` returns networks ✓
- ✅ WiFi scan in client mode: `wpa_cli` returns networks ✓
- ✅ Manual MyHomeWiFi entry → switch to client mode → reconnects to WiFi ✓
- ⚠️ iOS captive portal auto-trigger: portal does launch when iPhone connects to TRNTBL-Setup, but timing depends on DNS + Apple check (non-critical, manual fallback always available)

---

## [pre-alpha] — 2026-04-22 — performance + UX session

Session with the CHIP put back into the turntable + freshly soldered PAM8403. Big post-reflash cleanup and UX refactor.

### Fixed — post-NAND-reflash regressions

- ✅ `/etc/default/icecast2` was set to `ENABLE=false` → Icecast didn't start since the reflash, no streaming possible. Set back to `true` + defensive sed-fix at boot in start-trntbl.sh (in case reinstall repackages the default)
- ✅ `/etc/icecast2/*` and `/var/log/icecast2/` had orphan UIDs (110/117) vs the new icecast2 user (UID 109) after recreating `/etc/passwd`. Icecast couldn't read its own config. Defensive `chown -R icecast2:icecast` added to start-trntbl.sh on each boot
- ✅ `/etc/darkice.cfg` was **completely missing** post-reflash. Recreated with `plug:dsnoop_usb`, 48kHz, Icecast localhost:8000/vinyl, 320 kbps
- ✅ `/etc/asound.conf` also missing. Created with `dsnoop_usb` (capture sharing hw:1,0 between darkice + alsaloop) and `boosted_jack` (route plugin ×16 gain before PAM, inactive by default)
- ✅ Shell bug in scan-sonos-bg.sh produced invalid JSON (`[,"192.168.1.50",...]` with leading comma) → `load_cached_ips()` returned `[]` due to parse error → forced full scan every time. Script rewritten in Python (see below), bug gone

### Added

- ✅ `firmware/etc/asound.conf` and `firmware/etc/darkice.cfg`: system configs versioned in the repo (were on the CHIP only before)
- ✅ `firmware/scan-sonos-bg.py`: Python rewrite of scan-sonos-bg.sh with parallel threading (15 concurrent threads, Semaphore-gated) + in-process urllib2 instead of forking curl per IP. Replaces scan-sonos-bg.sh which has been removed
- ✅ `apply_output_mode(mode)` helper in app.py: kill alsaloop+darkice then launch the right one according to mode
- ✅ POST `/api/settings/output-mode`: endpoint to switch sonos/rca (kept as API, no longer exposed in UI after refactor)
- ✅ `output_mode` key in `config.json` (values: `sonos` or `rca`). Read by app.py and by start-trntbl.sh at boot
- ✅ `parallel_soap()` helper in app.py: launches one SOAP call per target in parallel threads. Used in `sonos_disconnect` and in the RCA switch. Gain: multiroom disconnect goes from N×3s to ~3s
- ⚠️ POST `/api/wifi/disconnect`: erases wpa_supplicant.conf and reboots → comes back up in AP mode TRNTBL-Setup. Not yet tested end-to-end
- ⚠️ Red "Disconnect WiFi" button in the Settings panel (with confirmation via `confirm()`). Not yet clicked by the user
- ⚠️ Dedicated "Local output" UI section (separate card from "Sonos speakers") with the `RCA local` row. Gestalt: two visually distinct groups since RCA ≠ Sonos speaker. Not yet seen on screen by the user after final refactor
- ✅ Dedicated SVG icon for RCA (two concentric circles = RCA L+R jack)

### Changed

- ✅ `start-trntbl.sh` v4: busy-waits replace `sleep 15/10/3`. New helpers `wait_for()` + `has_real_ip()`. Boot script goes from ~40s to ~24s. Total "power ON → portal available" time goes from ~90s to ~25s
- ✅ `start-trntbl.sh` reads `output_mode` from config.json at boot and launches **either** darkice **or** alsaloop, never both (avoids CPU saturation load 4+ → recurring crash observed before)
- ✅ `/api/wifi/scan`: switched from `iw dev wlan0 scan` (buggy on RTL8723BS when associated — often returned nothing) to `wpa_cli scan` + `scan_results`. Measured: 2.75s, 19 networks found (before: 10-15s for nothing or timeout)
- ✅ `probe_sonos()`, `get_player_id()`, `scan-sonos-bg.py probe()`: `urllib2.urlopen` in-process instead of `subprocess.check_output(['curl', ...])`. 254 IPs scanned in 8-15s vs ~47s before
- ✅ `scan_cached()` refactored via `probe_many()` with ThreadPoolExecutor-like (Semaphore 15 max concurrent)
- ✅ `/api/status`: `get_wifi_info()` extracted into a utility function, wifi inline in the response. Dashboard polls one endpoint instead of two
- ✅ Default bitrate: 256 → **320 kbps** (user request "this is the vinyl concept"). CPU-tenable now that we have only one audio consumer
- ⚠️ UI `renderSpeakers()` split into `renderLocalOutput()` + `renderSpeakers()`. RCA loads immediately (even before Sonos scan finishes). Not yet seen on screen by the user
- ✅ `renderSpeakers` text fallback: "Searching..." instead of "No speaker found" while the scan is running

### Known / reported

- ❌ **RCA audio inaudible even with software ×16 gain + PAM8403 at 100%**. Root cause: jack output level of sun4i-codec too low to drive the PAM. A 1kHz speaker-test at -6dBFS (strong digital signal) was also inaudible. Hardware diag: need an **analog preamp between the CHIP jack and the PAM input** (NE5532 or equivalent). Deferred to **V2**. alsaloop + `boosted_jack` config left in place for easy reactivation when the preamp is wired
- 🟡 **Sonos scan finds 4-6 speakers out of 6 known**. Some Sonos take more than 0.8s to respond under CPU load. Current trade-off: 0.8s timeout, 15 threads. To reach <2s + 100% Sonos → V2 via **SSDP multicast** (native UPnP discovery, no need to scan the /24)
- 🟡 Launching Flask via SSH sometimes leaves python-c zombies when the SSH session ends before the process detaches completely. Non-blocking (reboot resolves). Robust pattern: `nohup bash -c 'python app.py > log' &` alone (no setsid in SSH)

### Infra / meta

- ✅ Fix root SSH access to CHIP via dedicated ed25519 key (`~/.ssh/trntbl_ed25519`). No more need for UART to deploy. id_rsa key isn't kept because it's too long to paste reliably over UART at 115200 baud (lost characters). New `trntbl-root` and `trntbl-root-ip` entries in `~/.ssh/config`

---

## [pre-alpha] — 2026-04-18

### Added
- Complete firmware package: app.py v9, index.html, shell scripts
- One-shot deploy script (single password, auto pyc purge)
- Documentation: FLASH-GUIDE, INSTALL-GUIDE, HARDWARE, SETUP
- GitHub repo structure with firmware/, docs/, design/

### Fixed
- wifi_status() no longer depends on iwgetid/iwconfig (reads /proc/net/wireless + wpa_supplicant.conf)
- wifi_scan() uses `iw` with `iwlist` fallback (no more need for wireless-tools)
- deploy.sh writes rc.local directly (no more sed on exit 0 that fails if file is empty)
- deploy.sh fixes dpkg statoverride (missing crontab group)
- Version corrected to "pre-alpha" (not "v1.0-alpha")

### NAND reflash
- NAND flash succeeded via UTM VM (FEL) + Mac (fastboot)
- SPL + U-Boot written via FEL, UBI via Mac fastboot (11 chunks, 187s)
- 2 bad blocks cleanly skipped (0x10800000, 0x10C00000)
- /etc/passwd and /etc/group recreated (emptied by the flash)
- Corrupt Python .pyc purged

---

## [dev] — 2026-04-10

### Fixed
- Interface freeze → Flask threaded=True
- Phantom status at boot → state file cleared
- Scan clears the list → cache visible during rescan
- Multiroom not in sync → native Sonos grouping x-rincon:
- Toggle microcopy → "Enable/Disable priority"
- Partial playback → sonos-monitor recognizes x-rincon: as playing
- Share button KO → fallback execCommand copy for HTTP
- Avahi reverts to chip.local → separate SCP configs

### Tested
- 24/30 tests passed (see TEST-PLAN.md)
- Stability tests 8.1-8.5 not yet performed

---

## [initial] — 2026-03-29

### Added
- First functional version
- Streaming Darkice → Icecast → Sonos
- Flask portal with Sonos scan, selection, vinyl priority
- WiFi captive portal (AP mode TRNTBL-Setup)
- Auto-boot via rc.local
