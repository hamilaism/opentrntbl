#!/bin/bash
# openTRNTBL — Graceful WiFi reconnection (AP → client, no reboot)
#
# Mirror of wifi-to-ap.sh. Called by app.py /api/wifi/connect after the
# new wpa_supplicant.conf has been written. Stops hostapd/dnsmasq cleanly,
# brings wlan0 back up in client mode, runs wpa_supplicant + dhclient,
# and verifies association before returning. If anything fails, falls
# back to wifi-to-ap.sh so the user gets the captive portal back.
#
# Caller MUST have written the new wpa_supplicant.conf before invoking.
# Usage: wifi-to-client.sh [<expected-ssid>]
#
# Logged to /tmp/trntbl-wifi-switch.log (shared with wifi-to-ap.sh).

LOG="/tmp/trntbl-wifi-switch.log"
EXPECTED_SSID="$1"
echo "$(date) === wifi-to-client.sh start (target=${EXPECTED_SSID:-from-config}) ===" >> "$LOG"

# 1. Stop AP services first (hostapd holds the radio in AP mode).
echo "$(date) stopping hostapd + dnsmasq" >> "$LOG"
pkill -f dnsmasq 2>/dev/null
pkill -TERM hostapd 2>/dev/null
for _ in 1 2 3 4 5; do
    pgrep -x hostapd >/dev/null || break
    sleep 1
done
pkill -9 hostapd 2>/dev/null

# 2. Bring interface down + flush IPv4 (drop the AP IP 192.168.4.1).
#    Pause to let RTL8723BS settle.
echo "$(date) bringing wlan0 down" >> "$LOG"
ifconfig wlan0 down 2>>"$LOG"
ip addr flush dev wlan0 2>>"$LOG"
sleep 3

# 3. Bring up as client.
echo "$(date) bringing wlan0 up (client)" >> "$LOG"
ifconfig wlan0 up 2>>"$LOG"
sleep 1

# 4. Start wpa_supplicant with the new config.
echo "$(date) starting wpa_supplicant" >> "$LOG"
pkill -9 wpa_supplicant 2>/dev/null
sleep 1
wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf >> "$LOG" 2>&1

# 5. Wait for association (up to 30s).
echo "$(date) waiting for association" >> "$LOG"
associated=0
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do
    if iw dev wlan0 link 2>/dev/null | grep -q 'Connected to'; then
        associated=1
        echo "$(date) associated after ${i}s" >> "$LOG"
        break
    fi
    sleep 1
done

if [ "$associated" -ne 1 ]; then
    echo "$(date) ASSOCIATION FAIL → falling back to AP mode" >> "$LOG"
    bash /home/chip/opentrntbl/wifi-to-ap.sh
    exit 1
fi

# 6. Request DHCP (one-shot to avoid the orphan-daemon bug we hit before).
echo "$(date) requesting DHCP (-1 one-shot, 10s wait)" >> "$LOG"
dhclient -1 wlan0 2>>"$LOG" &
DHCLIENT_PID=$!

# Wait up to 10s for an IPv4 (not link-local).
got_ip=0
for i in 1 2 3 4 5 6 7 8 9 10; do
    ip=$(hostname -I 2>/dev/null | tr -d ' ')
    if [ -n "$ip" ] && ! echo "$ip" | grep -q '^169\.254'; then
        got_ip=1
        echo "$(date) got IP=${ip} after ${i}s" >> "$LOG"
        break
    fi
    sleep 1
done

# Kill dhclient explicitly so it doesn't survive as orphan.
kill -9 $DHCLIENT_PID 2>/dev/null
wait $DHCLIENT_PID 2>/dev/null

if [ "$got_ip" -ne 1 ]; then
    echo "$(date) DHCP FAIL → falling back to AP mode" >> "$LOG"
    bash /home/chip/opentrntbl/wifi-to-ap.sh
    exit 1
fi

# 7. Mark mode + restart Sonos monitor (it caches the local IP).
echo "client" > /tmp/trntbl-wifi-mode
pkill -f sonos-monitor 2>/dev/null
sleep 1
bash /home/chip/opentrntbl/sonos-monitor.sh >> /tmp/trntbl-boot.log 2>&1 &

# 8. Restart Avahi so trntbl.local resolves on the new interface.
service avahi-daemon restart >> "$LOG" 2>&1

# Note: Flask portal stays alive on 0.0.0.0:80, automatically serves on
# the new client IP. dashboard.local / trntbl.local also reachable.

echo "$(date) === wifi-to-client.sh done — IP=${ip} ===" >> "$LOG"
