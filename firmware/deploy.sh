#!/bin/bash
# openTRNTBL — Deploy to CHIP
# Usage: bash deploy.sh [chip-ip]

DIR="$(cd "$(dirname "$0")" && pwd)"
CHIP_USER="root"

echo "=== openTRNTBL deploy ==="
echo ""

if [ -n "$1" ]; then
    CHIP_IP="$1"
elif ping -c 1 -W 2 trntbl.local > /dev/null 2>&1; then
    CHIP_IP="trntbl.local"
    echo "Found CHIP at trntbl.local"
else
    echo "Could not find CHIP automatically."
    echo -n "Enter CHIP IP address: "
    read CHIP_IP
    if [ -z "$CHIP_IP" ]; then
        echo "No IP provided. Exiting."
        exit 1
    fi
fi

echo "Target: ${CHIP_USER}@${CHIP_IP}"
echo ""

# Write config files locally
TMPDIR=$(mktemp -d)

cat > "$TMPDIR/hostapd.conf" << 'HAPEOF'
interface=wlan0
driver=nl80211
ssid=TRNTBL-Setup
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=0
HAPEOF

cat > "$TMPDIR/dnsmasq.conf" << 'DNSEOF'
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
address=/#/192.168.4.1
DNSEOF

cat > "$TMPDIR/avahi-daemon.conf" << 'AVHEOF'
[server]
host-name=trntbl
use-ipv4=yes
use-ipv6=yes
allow-interfaces=wlan0
deny-interfaces=usb0
[wide-area]
enable-wide-area=yes
[publish]
publish-addresses=yes
publish-hinfo=yes
publish-workstation=yes
[reflector]
[rlimits]
AVHEOF

cat > "$TMPDIR/rc.local" << 'RCEOF'
#!/bin/bash
bash /home/chip/opentrntbl/start-trntbl.sh &
exit 0
RCEOF

echo "Uploading all files in one shot..."
scp -o ConnectTimeout=30 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "$DIR/app.py" \
    "$DIR/index.html" \
    "$DIR/i18n.js" \
    "$DIR/tokens.css" \
    "$DIR/components.css" \
    "$DIR/sonos-monitor.sh" \
    "$DIR/scan-sonos-bg.sh" \
    "$DIR/start-trntbl.sh" \
    "$DIR/wifi-switch.sh" \
    "$DIR/etc/asound.conf" \
    "$DIR/etc/darkice.cfg" \
    "$DIR/etc/wpa_supplicant/wpa_supplicant.conf" \
    "$TMPDIR/hostapd.conf" \
    "$TMPDIR/dnsmasq.conf" \
    "$TMPDIR/avahi-daemon.conf" \
    "$TMPDIR/rc.local" \
    "${CHIP_USER}@${CHIP_IP}:/tmp/opentrntbl-deploy/"

if [ $? -ne 0 ]; then
    echo "ERROR: Upload failed. Is the CHIP reachable?"
    rm -rf "$TMPDIR"
    exit 1
fi

rm -rf "$TMPDIR"

echo "Configuring and starting services..."
ssh -o ConnectTimeout=30 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "${CHIP_USER}@${CHIP_IP}" bash << 'REMOTE'
set -e

# Move app files
mkdir -p /home/chip/opentrntbl
cp /tmp/opentrntbl-deploy/app.py /home/chip/opentrntbl/
cp /tmp/opentrntbl-deploy/index.html /home/chip/opentrntbl/
cp /tmp/opentrntbl-deploy/i18n.js /home/chip/opentrntbl/
cp /tmp/opentrntbl-deploy/tokens.css /home/chip/opentrntbl/
cp /tmp/opentrntbl-deploy/components.css /home/chip/opentrntbl/
cp /tmp/opentrntbl-deploy/sonos-monitor.sh /home/chip/opentrntbl/
cp /tmp/opentrntbl-deploy/scan-sonos-bg.sh /home/chip/opentrntbl/
cp /tmp/opentrntbl-deploy/start-trntbl.sh /home/chip/opentrntbl/
cp /tmp/opentrntbl-deploy/wifi-switch.sh /home/chip/opentrntbl/

# Move config files
cp /tmp/opentrntbl-deploy/asound.conf /etc/asound.conf
cp /tmp/opentrntbl-deploy/darkice.cfg /etc/darkice.cfg
cp /tmp/opentrntbl-deploy/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf
cp /tmp/opentrntbl-deploy/hostapd.conf /etc/hostapd/hostapd.conf
cp /tmp/opentrntbl-deploy/dnsmasq.conf /etc/dnsmasq.conf
cp /tmp/opentrntbl-deploy/avahi-daemon.conf /etc/avahi/avahi-daemon.conf
cp /tmp/opentrntbl-deploy/rc.local /etc/rc.local

# Permissions
chmod +x /home/chip/opentrntbl/sonos-monitor.sh
chmod +x /home/chip/opentrntbl/scan-sonos-bg.sh
chmod +x /home/chip/opentrntbl/start-trntbl.sh
chmod +x /home/chip/opentrntbl/wifi-switch.sh
chmod 644 /home/chip/opentrntbl/app.py
chmod 644 /home/chip/opentrntbl/index.html
chmod +x /etc/rc.local

# Fix hostname
echo "trntbl" > /etc/hostname
hostname trntbl
grep -q "trntbl" /etc/hosts || echo "127.0.0.1 trntbl" >> /etc/hosts

# Fix dpkg statoverride (crontab group missing)
sed -i '/crontab/d' /var/lib/dpkg/statoverride 2>/dev/null || true

# Purge stale Python bytecode (prevents marshal errors after NAND reflash)
find /usr/lib/python2.7 -name "*.pyc" -delete 2>/dev/null || true

# Kill old processes
pkill -9 -f "python app.py" 2>/dev/null || true
pkill -f sonos-monitor 2>/dev/null || true
sleep 1

# Clear stale runtime state
echo '{}' > /tmp/trntbl-sonos-state
echo '[]' > /home/chip/opentrntbl/sonos_cache.json

# Initialize config.json ONLY if missing (preserve user Sonos targets/RCA prefs on redeploy)
if [ ! -f /home/chip/opentrntbl/config.json ]; then
  echo '{"sonos_targets":[],"vinyl_priority":false,"bitrate":256,"rca_enabled":false,"rca_show_ui":true}' > /home/chip/opentrntbl/config.json
fi

# WiFi power management
echo "options 8723bs rtw_power_mgnt=0" > /etc/modprobe.d/8723bs.conf

# Restart avahi with new config
service avahi-daemon restart 2>/dev/null || true

# Start services
cd /home/chip/opentrntbl
python app.py > /tmp/trntbl-portal.log 2>&1 &
sleep 2

# Verify portal is running
if netstat -tlnp 2>/dev/null | grep -q ":80 "; then
    echo ""
    echo "Deploy complete!"
    echo "Portal: http://trntbl.local"
else
    echo ""
    echo "WARNING: Portal failed to start!"
    cat /tmp/trntbl-portal.log
fi

# Start sonos monitor
bash sonos-monitor.sh > /dev/null 2>&1 &

# Cleanup
rm -rf /tmp/opentrntbl-deploy
REMOTE

echo ""
echo "=== Done ==="
echo "Open http://trntbl.local in your browser"
