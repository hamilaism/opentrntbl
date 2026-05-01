#!/bin/bash
# openTRNTBL — SDIO / RTL8723BS driver watchdog
#
# The RTL8723BS WiFi chipset on the C.H.I.P. has a known habit of locking
# up the SDIO bus, especially after WiFi mode transitions or under sustained
# load. Symptom: kernel log spam "sunxi-mmc 1c0f000.mmc: smc 0 err, cmd 53,
# RD RTO" — the SDIO read times out, the driver retries forever, the radio
# stops working but the CPU stays alive.
#
# When this happens, the WiFi watchdog in start-trntbl.sh can't help: it
# pings the gateway and fails, then tries `wpa_supplicant + dhclient` which
# fail too because the driver is stuck.
#
# This watchdog detects the symptom and recovers the driver:
#   1. Watch dmesg for "sunxi-mmc.*RD RTO" pattern.
#   2. If detected (>3 occurrences in last 30s) → rmmod 8723bs / modprobe.
#   3. If rmmod hangs (60s timeout) or modprobe fails → reboot -f.
#
# Run as a background daemon from start-trntbl.sh. Logs to /tmp/sdio-watchdog.log.

LOG="/tmp/sdio-watchdog.log"
CHECK_INTERVAL=15           # seconds between checks
RDTO_THRESHOLD=3            # min "RD RTO" matches in window to trigger recovery
RDTO_WINDOW=30              # seconds — only recent matches count
RMMOD_TIMEOUT=60            # seconds — give up on rmmod and force reboot
LAST_RECOVERY=0             # timestamp of last recovery attempt (avoid loops)
RECOVERY_COOLDOWN=120       # seconds — wait this long before re-attempting

echo "$(date) sdio-watchdog started (interval=${CHECK_INTERVAL}s, threshold=${RDTO_THRESHOLD}/${RDTO_WINDOW}s)" >> "$LOG"

count_recent_rdto() {
    # Count "RD RTO" lines from dmesg whose monotonic timestamp is within
    # the last RDTO_WINDOW seconds. dmesg shows timestamps as [seconds.us]
    # since kernel boot — we read /proc/uptime to get current uptime.
    local uptime cutoff
    uptime=$(awk '{print int($1)}' /proc/uptime)
    cutoff=$((uptime - RDTO_WINDOW))
    dmesg | grep "RD RTO" | awk -v cutoff="$cutoff" '
        match($0, /\[ *([0-9]+)\./, m) {
            if (m[1] + 0 >= cutoff) c++
        }
        END { print c + 0 }
    '
}

# Reboot rate-limit : if too many reboots in the last hour, give up
# rather than loop the system forever. Persisted across reboots.
REBOOT_LOG=/var/log/sdio-reboot-history
MAX_REBOOTS_PER_HOUR=4

should_reboot_or_give_up() {
    local now=$(date +%s)
    local cutoff=$((now - 3600))
    # Filter recent reboots
    local recent=0
    if [ -f "$REBOOT_LOG" ]; then
        recent=$(awk -v cutoff="$cutoff" '$1+0 > cutoff' "$REBOOT_LOG" | wc -l)
    fi
    if [ "$recent" -ge "$MAX_REBOOTS_PER_HOUR" ]; then
        echo "$(date) GIVE UP: $recent reboots in last hour ≥ $MAX_REBOOTS_PER_HOUR. Logging only, NOT rebooting." >> "$LOG"
        return 1
    fi
    echo "$now" >> "$REBOOT_LOG"
    return 0
}

recover_driver() {
    echo "$(date) RECOVERY: rmmod 8723bs (with ${RMMOD_TIMEOUT}s timeout)" >> "$LOG"

    # Bring interface down first, gives the driver a chance to flush
    ifconfig wlan0 down 2>/dev/null
    sleep 1

    # Run rmmod with timeout — if it hangs the driver is too far gone
    timeout "$RMMOD_TIMEOUT" rmmod 8723bs 2>>"$LOG"
    local rc=$?
    if [ $rc -ne 0 ]; then
        echo "$(date) RECOVERY: rmmod failed (rc=$rc)" >> "$LOG"
        if should_reboot_or_give_up; then
            sync
            sleep 1
            reboot -f
            exit 0
        else
            return 1
        fi
    fi
    echo "$(date) RECOVERY: rmmod OK, sleeping 3s before modprobe" >> "$LOG"
    sleep 3

    if ! modprobe 8723bs 2>>"$LOG"; then
        echo "$(date) RECOVERY: modprobe failed" >> "$LOG"
        if should_reboot_or_give_up; then
            sync
            sleep 1
            reboot -f
            exit 0
        else
            return 1
        fi
    fi
    echo "$(date) RECOVERY: modprobe OK, waiting 5s for driver init" >> "$LOG"
    sleep 5

    # Driver back. Restart networking depending on current mode.
    local mode
    mode=$(cat /tmp/trntbl-wifi-mode 2>/dev/null)
    if [ "$mode" = "ap" ]; then
        echo "$(date) RECOVERY: re-arming AP mode" >> "$LOG"
        ifconfig wlan0 up
        ip addr add 192.168.4.1/24 dev wlan0 2>/dev/null
        pkill -9 hostapd 2>/dev/null; sleep 1
        hostapd /etc/hostapd/hostapd.conf -B
        pkill -f dnsmasq 2>/dev/null; sleep 0.5
        dnsmasq -C /etc/dnsmasq.conf &
    else
        echo "$(date) RECOVERY: re-arming client mode" >> "$LOG"
        pkill -9 wpa_supplicant 2>/dev/null
        pkill -9 -f 'dhclient wlan0' 2>/dev/null
        sleep 1
        ifconfig wlan0 up
        wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null
        sleep 6
        dhclient -1 wlan0 2>/dev/null
    fi
    echo "$(date) RECOVERY: done" >> "$LOG"
}

# Main loop
while true; do
    sleep "$CHECK_INTERVAL"

    n=$(count_recent_rdto)
    if [ "$n" -ge "$RDTO_THRESHOLD" ]; then
        now=$(date +%s)
        elapsed=$((now - LAST_RECOVERY))
        if [ "$elapsed" -lt "$RECOVERY_COOLDOWN" ]; then
            echo "$(date) RD RTO detected (${n}/${RDTO_WINDOW}s) but in cooldown (${elapsed}s < ${RECOVERY_COOLDOWN}s)" >> "$LOG"
            continue
        fi
        echo "$(date) RD RTO detected (${n}/${RDTO_WINDOW}s) — triggering recovery" >> "$LOG"
        LAST_RECOVERY=$now
        recover_driver
    fi
done
