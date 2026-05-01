#!/bin/bash
# openTRNTBL — Graceful WiFi disconnect (client → AP, no reboot)
#
# Replaces the previous "blank wpa_supplicant.conf + reboot" flow which
# was causing RTL8723BS driver lockups. We do the transition runtime,
# stopping services in the right order so the SDIO bus isn't yanked
# while a transfer is in flight.
#
# Caller (app.py /api/wifi/disconnect) MUST blank wpa_supplicant.conf
# BEFORE invoking this script — we don't touch it here. Reason: Flask
# response goes out, then we run; if anything crashes, the empty config
# guarantees a clean AP boot.
#
# Logged to /tmp/trntbl-wifi-switch.log (shared with wifi-switch.sh).

LOG="/tmp/trntbl-wifi-switch.log"
echo "$(date) === wifi-to-ap.sh start ===" > "$LOG"

# 1. Stop user-facing services first (they hold sockets / read config)
echo "$(date) stopping user services" >> "$LOG"
pkill -f sonos-monitor 2>/dev/null
pkill -f darkice 2>/dev/null
pkill -f alsaloop 2>/dev/null
sleep 1

# 2. Stop network client cleanly (graceful, not SIGKILL)
#    SIGTERM lets wpa_supplicant deauth + release the radio properly.
#    Wait up to 5s for it to exit before escalating.
echo "$(date) stopping wpa_supplicant + dhclient (graceful)" >> "$LOG"
pkill -TERM wpa_supplicant 2>/dev/null
pkill -TERM -f 'dhclient wlan0' 2>/dev/null
for _ in 1 2 3 4 5; do
    pgrep -x wpa_supplicant >/dev/null || pgrep -x dhclient >/dev/null || break
    sleep 1
done
# Last resort if still alive
pkill -9 wpa_supplicant 2>/dev/null
pkill -9 -f 'dhclient wlan0' 2>/dev/null

# 3. Bring interface down + flush IPv4
#    Pause to let the driver settle — RTL8723BS doesn't like fast transitions.
echo "$(date) bringing wlan0 down" >> "$LOG"
ifconfig wlan0 down 2>>"$LOG"
ip addr flush dev wlan0 2>>"$LOG"
sleep 3

# 4. Bring up as AP host
echo "$(date) bringing wlan0 up (AP)" >> "$LOG"
ifconfig wlan0 192.168.4.1 netmask 255.255.255.0 up 2>>"$LOG"
sleep 1

# 5. Start hostapd + dnsmasq (kill any stale instance first)
pkill -9 hostapd 2>/dev/null; sleep 1
hostapd /etc/hostapd/hostapd.conf -B >> "$LOG" 2>&1
sleep 1
pkill -f dnsmasq 2>/dev/null; sleep 0.5
dnsmasq -C /etc/dnsmasq.conf >> "$LOG" 2>&1 &
sleep 1

# 6. avahi for trntbl.local resolution
service avahi-daemon restart >> "$LOG" 2>&1

# 7. Mark mode + verify
echo "ap" > /tmp/trntbl-wifi-mode
sleep 1
if pgrep -x hostapd >/dev/null && ip addr show wlan0 | grep -q '192.168.4.1'; then
    echo "$(date) AP mode active — TRNTBL-Setup ready" >> "$LOG"
else
    echo "$(date) ERROR: AP failed to come up. Forcing reboot." >> "$LOG"
    sleep 1
    reboot -f
    exit 1
fi

# Warm the scan cache so the captive portal shows networks immediately.
# `iw scan trigger` is non-disruptive on RTL8723BS — hostapd / clients
# stay connected. The cache will then be served by `iw scan dump`.
echo "$(date) warming scan cache (iw scan trigger)" >> "$LOG"
iw dev wlan0 scan trigger >> "$LOG" 2>&1
sleep 1

# Note: Flask portal stays alive. It was already bound to 0.0.0.0:80,
# so it now serves on 192.168.4.1:80 automatically.

echo "$(date) === wifi-to-ap.sh done ===" >> "$LOG"
