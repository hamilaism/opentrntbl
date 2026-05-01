# openTRNTBL — QA Checklist V1.0.0-alpha

**Firmware:** openTRNTBL pre-alpha v9  
**Hardware:** CHIP v1.0, RTL8723BS, PCM2900C  
**Status:** Smoke tests + Power cycle ✅ | **Remaining:** 72h stability soak

---

## Quick Smoke Tests (10 min — validate no regression)

Run these once before stability tests to ensure nothing broke.

### Boot & Dashboard

```
[ ] Power on CHIP → Dashboard at http://trntbl.local loads within 3s
[ ] WiFi shows MyHomeWiFi, signal bars visible
[ ] Sonos scan shows 4-6 speakers after ~15s
[ ] Uptime incrementing
```

### Bitrate Change

```
[ ] Réglages → Bitrate: click 192k → button highlights, spinner visible (1-2s)
[ ] After 2s: click 320k → darkice restarts
[ ] Refresh page: 320k still highlighted (persistence)
```

### RCA Toggle

```
[ ] Réglages → "Afficher la sortie RCA" toggle
[ ] Click toggle OFF → "Sortie locale" disappears from dashboard
[ ] Click toggle ON → "Sortie locale" reappears
[ ] Refresh: toggle state persists
```

### Sonos Selection

```
[ ] Click Roam → becomes green, "playing" after ~3s
[ ] Click Salon-One → also green, both "playing" (grouping)
[ ] Click Roam again → deselect, Salon-One continues playing alone
[ ] "Tout déconnecter" → all grey, status = disconnected
```

### Power Cycle

```
[ ] Débrancher CHIP power (5 secondes)
[ ] Rebrancher, attendre 40s
[ ] Dashboard loads: WiFi OK, Sonos OK
[ ] Config persisted: bitrate, selected speakers
```

**⏱️ Expected:** All green in ~10 minutes. If any red → investigate before stability tests.

---

## 72-Hour Stability Soak (Main Goal)

**Timeline:** Start end of day → run 3 full days → finish with clean shutdown.

### Setup (15 min)

1. **Dashboard:**
   - [ ] WiFi: MyHomeWiFi connected, signal > 50%
   - [ ] Sonos: 2+ speakers selected + "playing" (e.g., Roam + Salon-One)
   - [ ] Bitrate: 320k
   - [ ] Leave dashboard tab open (or pin to browser, check periodically)

2. **SSH Terminal:** Open for background monitoring
   ```bash
   watch -n 60 'ps aux | grep -E "python|darkice|avahi"; uptime'
   ```
   (Runs every 60s, watch for process changes or load spikes)

### Daily Log (2x per day: morning + evening)

**Check & note:**

```
=== Day 1 — [HH:MM] ===
[ ] Dashboard responsive (click a button)
[ ] Sonos: both speakers "playing", audio sync
[ ] WiFi signal: __ / 100 (note the level)
[ ] Uptime: __h __m
[ ] SSH load: __ (from `uptime` — should stay < 1.5)
[ ] Logs: `ssh root@<YOUR-CHIP-IP> "dmesg | tail -5"` → [paste, look for errors]

=== Day 2 — [HH:MM] ===
[ ] Dashboard responsive
[ ] Sonos "playing"
[ ] WiFi stable
[ ] Uptime: __h __m
[ ] Load: __
[ ] Logs clean: [Y/N]

=== Day 3 — [HH:MM] ===
[ ] Dashboard responsive
[ ] Sonos "playing"
[ ] WiFi stable
[ ] Uptime: __h __m
[ ] Load: __
[ ] Logs clean: [Y/N]
```

### Optional: Planned Reboot During Soak

**At 24h mark (if you want to test):**
```bash
ssh root@<YOUR-CHIP-IP> "reboot"
# Wait 40s → Dashboard should reload automatically
# Verify: services restart, uptime reset, Sonos reconnects
```

### Success Criteria

**72h passes if:**
- ✅ Zero unplanned reboots (uptime > 72h, or continuous from last power-on)
- ✅ Dashboard always responsive (no freezes)
- ✅ Sonos stays "playing" without manual restart
- ✅ WiFi signal stable (no sudden drops)
- ✅ CPU load stays < 1.5 (even with 2+ speakers streaming)
- ✅ No kernel panics or critical errors in dmesg

**Red flags (stop & investigate):**
- ❌ Dashboard unresponsive
- ❌ Sonos drops mid-stream
- ❌ WiFi spontaneous disconnect
- ❌ High CPU load (> 2.0)
- ❌ Kernel errors in dmesg (OOM, segfault, thermal throttle)

---

## Blocker Report (if any issues found)

If you hit a stopper, fill in:

```
=== BLOCKER ===
Title: [One line]
Severity: CRITICAL | MAJOR | MINOR

Reproduce:
1. [Step]
2. [Step]
3. [Observe issue]

Expected: [What should happen]
Actual: [What happens instead]

Logs: [paste dmesg / syslog tail]
Environment: [Time, uptime, load at time of issue]
```

---

## Quick Commands

```bash
# SSH into CHIP
ssh root@<YOUR-CHIP-IP>  # password: chip

# Monitor in real-time
ps aux | grep -E "python|darkice|avahi"
uptime
iw dev wlan0 link | grep SSID

# Logs
dmesg | tail -20
tail -50 /var/log/syslog
tail -f /tmp/trntbl-portal.log

# API status
curl http://<YOUR-CHIP-IP>/api/status | jq '.wifi, .sonos_state, .bitrate, .uptime'

# Reboot
reboot
```

---

## Sign-Off

After 72h complete:

```
✅ STABILITY TEST RESULT

Tester: Ismail Hamila
Start Date: YYYY-MM-DD HH:MM
End Date: YYYY-MM-DD HH:MM
Total Uptime: ___h ___m

Issues Found: [ ] NONE [ ] [count]
Critical Blockers: [ ] NONE [ ] [describe]

Status: [ ] ✅ READY FOR V1.0.0-alpha [ ] ⚠️ NEEDS FIXES
```

---

**TL;DR:**
1. Run smoke tests (10 min) → all should pass
2. Start 72h soak → Sonos + WiFi + Dashboard running
3. Check 2x per day → log uptime + load
4. At 72h → if stable + no crashes → ✅ ALPHA READY
5. If issues → document blocker + investigate

Go ! 🎵
