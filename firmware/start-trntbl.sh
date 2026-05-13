#!/bin/bash
# openTRNTBL by ismo — Boot Script v5
# Changes vs v4:
# - dhclient lancé en -1 (one-shot) + tué explicitement par PID après le
#   poll d'IP, pour éviter qu'un daemon orphan (ppid=1) survive et squatte
#   wlan0 quand on bascule en mode AP.
# - killall remplacé par pkill -9 partout : `killall` n'est pas installé
#   sur ce Debian Jessie minimal (busybox-extras absent), tous les killall
#   échouaient silencieusement → process zombies multipliés.
# - ip addr flush dev wlan0 avant le bind 192.168.4.1, pour purger toute
#   IPv4 résiduelle laissée par un client.
# - watchdog WiFi : dhclient -1 (cohérence).

LOG="/tmp/trntbl-boot.log"
echo "=== openTRNTBL boot $(date) ===" > "$LOG"

# Busy-wait helper: wait up to $timeout seconds for $test_cmd to succeed
wait_for() {
    local desc="$1"
    local test_cmd="$2"
    local timeout="${3:-20}"
    local start
    start=$(date +%s)
    for _ in $(seq 1 "$timeout"); do
        if eval "$test_cmd" >/dev/null 2>&1; then
            echo "$(date) $desc OK ($(($(date +%s) - start))s)" >> "$LOG"
            return 0
        fi
        sleep 1
    done
    echo "$(date) $desc TIMEOUT after ${timeout}s" >> "$LOG"
    return 1
}

has_real_ip() {
    local ip
    ip=$(hostname -I 2>/dev/null | tr -d ' ')
    [ -n "$ip" ] && ! echo "$ip" | grep -q "^169\.254"
}

# Wait for wlan0 to be available (replaces sleep 15)
wait_for "wlan0 available" "ip link show wlan0" 20

# Clear stale Sonos state from previous session
echo '{}' > /tmp/trntbl-sonos-state

# WiFi power management — disable power saving
echo "options 8723bs rtw_power_mgnt=0" > /etc/modprobe.d/8723bs.conf 2>/dev/null

# Stop NetworkManager — we manage WiFi ourselves
systemctl stop NetworkManager 2>/dev/null
pkill -9 wpa_supplicant 2>/dev/null
rm -f /var/run/wpa_supplicant/wlan0
sleep 1

# ALSA — restore mixer settings (jack output enabled, RCA volume maximized)
alsactl restore >> "$LOG" 2>&1
amixer -c 0 cset numid=1 63 2>/dev/null
amixer -c 0 sset 'Left Mixer Left DAC' on 2>/dev/null
amixer -c 0 sset 'Right Mixer Right DAC' on 2>/dev/null
amixer -c 0 sset 'Power Amplifier DAC' on 2>/dev/null
amixer -c 0 sset 'Power Amplifier Mute' on 2>/dev/null
amixer -c 0 sset 'Power Amplifier Mixer' on 2>/dev/null
# Maximize all DAC output levels for RCA (sun4i-codec is weak)
amixer -c 0 sset 'DAC' 100% 2>/dev/null
amixer -c 0 sset 'DAC Playback' 100% 2>/dev/null
amixer -c 0 sset 'Line Out' 100% 2>/dev/null
alsactl store 2>/dev/null

# Decide WiFi mode: AP (setup) or Normal (connected)
WIFI_MODE="ap"
if [ -f /etc/wpa_supplicant/wpa_supplicant.conf ]; then
    WPA_CONTENT=$(cat /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null)
    if echo "$WPA_CONTENT" | grep -q "network="; then
        echo "$(date) Trying saved WiFi..." >> "$LOG"
        ifconfig wlan0 up
        wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf

        # Wait up to 30s for WiFi association (RTL8723BS can be slow)
        wait_for "WiFi associated" "iw dev wlan0 link | grep -q 'Connected to'" 30

        # Request DHCP. -1 = one-shot (try once, exit on success/failure) so
        # no orphan daemon survives the AP fallback. We poll for IP below.
        dhclient -1 wlan0 2>/dev/null &
        DHCLIENT_PID=$!

        # Wait up to 10s for a real IP (not link-local 169.254.x.x)
        wait_for "IP acquired" "has_real_ip" 10

        # Whatever the outcome, dhclient is no longer needed: kill it now
        # so the AP fallback below doesn't fight a stale client over wlan0.
        kill -9 $DHCLIENT_PID 2>/dev/null
        wait $DHCLIENT_PID 2>/dev/null

        IP=$(hostname -I 2>/dev/null | tr -d ' ')
        if [ -n "$IP" ] && ! echo "$IP" | grep -q "^169\.254"; then
            WIFI_MODE="normal"
            echo "$(date) Connected to WiFi, IP=$IP" >> "$LOG"

            # NTP sync — CHIP has no battery-backed RTC, time is wrong after reboot.
            # Try ntpdate first (fastest, most reliable when present), fall back to rdate
            # over time/37 (Debian Jessie default), then to HTTP Date header as last resort.
            echo "$(date) Syncing time..." >> "$LOG"
            if command -v ntpdate >/dev/null 2>&1; then
                ntpdate -u pool.ntp.org >> "$LOG" 2>&1 \
                    || echo "$(date) ntpdate failed (offline?)" >> "$LOG"
            elif command -v rdate >/dev/null 2>&1; then
                rdate -n -p time.nist.gov >> "$LOG" 2>&1 \
                    && rdate -n -s time.nist.gov >> "$LOG" 2>&1 \
                    || echo "$(date) rdate failed" >> "$LOG"
            else
                # Last-resort fallback: parse HTTP Date header (always works if WiFi up)
                HTTP_DATE=$(curl -sI http://google.com 2>/dev/null | grep -i '^date:' | sed 's/^[Dd]ate: //')
                if [ -n "$HTTP_DATE" ]; then
                    date -s "$HTTP_DATE" >> "$LOG" 2>&1 \
                        || echo "$(date) HTTP Date sync failed" >> "$LOG"
                else
                    echo "$(date) No NTP tool available (ntpdate/rdate/curl) — time stays wrong" >> "$LOG"
                fi
            fi
            echo "$(date) Time after sync: $(date)" >> "$LOG"
        else
            echo "$(date) Saved WiFi failed, starting AP mode" >> "$LOG"
            pkill -9 wpa_supplicant 2>/dev/null
        fi
    fi
fi

if [ "$WIFI_MODE" = "ap" ]; then
    echo "$(date) Starting AP mode (TRNTBL-Setup)" >> "$LOG"
    echo "ap" > /tmp/trntbl-wifi-mode

    # Clean slate before the AP bind: kill any wpa_supplicant/dhclient that
    # may still hold wlan0, retry-loop until pgrep is clean.
    pkill -9 wpa_supplicant 2>/dev/null
    pkill -9 -f 'dhclient wlan0' 2>/dev/null
    for _ in 1 2 3; do
        pgrep -x dhclient >/dev/null || break
        pkill -9 dhclient 2>/dev/null
        sleep 0.3
    done

    ifconfig wlan0 down
    sleep 1
    ip addr flush dev wlan0  # purge any IPv4 left over by a stale dhclient
    ifconfig wlan0 192.168.4.1 netmask 255.255.255.0 up
    sleep 1
    hostapd /etc/hostapd/hostapd.conf -B
    sleep 1
    pkill -f dnsmasq 2>/dev/null; sleep 0.5
    dnsmasq -C /etc/dnsmasq.conf &
    sleep 1
    service avahi-daemon restart >> "$LOG" 2>&1
    echo "$(date) AP mode active (hostapd + dnsmasq + avahi)" >> "$LOG"
else
    echo "normal" > /tmp/trntbl-wifi-mode

    # Avahi (trntbl.local)
    service avahi-daemon restart >> "$LOG" 2>&1
    echo "$(date) Avahi started" >> "$LOG"

    # Icecast — ensure daemon is ENABLED (reflash regression: was false)
    if grep -q "^ENABLE=false" /etc/default/icecast2 2>/dev/null; then
        sed -i 's/^ENABLE=false/ENABLE=true/' /etc/default/icecast2
        echo "$(date) Icecast2 ENABLE flipped to true" >> "$LOG"
    fi
    # Fix ownership on /etc/icecast2 + /var/log/icecast2 (reflash regression:
    # user/group UIDs get orphaned after /etc/passwd/group are recreated)
    chown -R icecast2:icecast /etc/icecast2 /var/log/icecast2 2>/dev/null
    service icecast2 restart >> "$LOG" 2>&1
    wait_for "Icecast port 8000" "netstat -ln 2>/dev/null | grep -q ':8000 '" 10

    # Audio output: single consumer of hw:1,0 to keep the single-core CHIP
    # under load budget (running Darkice + alsaloop simultaneously pushed
    # load avg > 4 and caused crashes). Read config from config.json.
    RCA_ENABLED=$(python -c "
import json
try:
    cfg = json.load(open('/home/chip/opentrntbl/config.json'))
    print('true' if cfg.get('rca_enabled', False) else 'false')
except:
    print('false')
" 2>/dev/null)

    if [ "$RCA_ENABLED" = "true" ]; then
        # RCA hardware mod: launch alsaloop directly (ignore USB ADC)
        alsaloop -C plughw:1,0 -P boosted_jack -r 48000 -c 2 -f S16_LE -t 50000 > /dev/null 2>&1 &
        echo "$(date) alsaloop started (RCA mod enabled)" >> "$LOG"
    elif arecord -l 2>/dev/null | grep -q "USB AUDIO"; then
        # Standard config: USB ADC present, read output_mode
        OUTPUT_MODE=$(python -c "
import json
try:
    cfg = json.load(open('/home/chip/opentrntbl/config.json'))
    print(cfg.get('output_mode', 'sonos'))
except:
    print('sonos')
" 2>/dev/null)

        if [ "$OUTPUT_MODE" = "rca" ]; then
            alsaloop -C plughw:1,0 -P boosted_jack -r 48000 -c 2 -f S16_LE -t 50000 > /dev/null 2>&1 &
            echo "$(date) alsaloop started (USB ADC -> jack/RCA)" >> "$LOG"
        else
            darkice -c /etc/darkice.cfg > /dev/null 2>&1 &
            echo "$(date) Darkice started (USB ADC -> Icecast)" >> "$LOG"
        fi
    else
        echo "$(date) WARNING: No BurrBrown USB audio device detected and rca_enabled=false" >> "$LOG"
    fi

    # Sonos monitor (state + priority)
    sleep 1
    bash /home/chip/opentrntbl/sonos-monitor.sh >> "$LOG" 2>&1 &
    echo "$(date) Sonos monitor started" >> "$LOG"

    # WiFi watchdog
    (
        sleep 60
        while true; do
            GW=$(ip route | grep default | awk '{print $3}')
            if [ -n "$GW" ]; then
                if ! ping -c 1 -W 3 "$GW" > /dev/null 2>&1; then
                    echo "$(date) WiFi lost, reconnecting..." >> "$LOG"
                    pkill -9 wpa_supplicant 2>/dev/null
                    ifconfig wlan0 down
                    sleep 2
                    ifconfig wlan0 up
                    sleep 2
                    wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null
                    sleep 8
                    dhclient -1 wlan0 2>/dev/null
                    echo "$(date) WiFi reconnect attempted" >> "$LOG"
                fi
            fi
            sleep 60
        done
    ) &
fi

# Flask portal — always starts (serves WiFi config in AP mode, dashboard in normal mode)
cd /home/chip/opentrntbl || exit 1
python app.py > /tmp/trntbl-portal.log 2>&1 &
echo "$(date) Portal started on port 80" >> "$LOG"

# SDIO watchdog — detects RTL8723BS driver lockups (RD RTO spam in dmesg)
# and recovers via rmmod/modprobe, with reboot -f as last resort.
bash /home/chip/opentrntbl/sdio-watchdog.sh > /dev/null 2>&1 &
echo "$(date) SDIO watchdog started" >> "$LOG"

echo "$(date) Boot complete (mode: $WIFI_MODE)" >> "$LOG"
