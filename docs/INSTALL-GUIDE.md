# openTRNTBL — Installation guide

Installing openTRNTBL on a freshly flashed CHIP.

## Prerequisites

- CHIP flashed with Debian Jessie (see `FLASH-GUIDE.md`)
- CHIP connected to WiFi (`nmcli dev wifi connect "SSID" password "PASSWORD"`)
- Working SSH (`ssh root@<IP>`, password `chip`)

---

## 1. Configure the APT repositories

The official Jessie repos are dead. Use the archives:

```bash
ssh root@<IP>
cat > /etc/apt/sources.list << 'EOF'
deb http://archive.debian.org/debian jessie main contrib non-free
deb http://archive.debian.org/debian-security jessie/updates main contrib non-free
EOF
apt-get -o Acquire::Check-Valid-Until=false update
```

## 2. Install the dependencies

```bash
apt-get -o Acquire::Check-Valid-Until=false install -y --force-yes \
  python python-flask \
  icecast2 darkice \
  avahi-daemon \
  alsa-utils \
  sox libsox-fmt-mp3 mpg123 \
  hostapd dnsmasq
```

If icecast2 asks for an interactive config:
```bash
DEBIAN_FRONTEND=noninteractive apt-get install -y --force-yes icecast2
```

## 3. Repair passwd/group (if needed)

After a NAND reflash, `/etc/passwd` and `/etc/group` may be empty or corrupted. Symptom: `systemd-tmpfiles` crashes at boot, `systemd-logind` fails, no `login:` prompt.

### Diagnosis

Boot with `init=/bin/bash` (catch U-Boot, type):
```
setenv bootargs root=ubi0:rootfs rootfstype=ubifs rw earlyprintk ubi.mtd=4 init=/bin/bash
boot
```

Then:
```bash
grep -c "" /etc/passwd /etc/group
```

If < 10 lines, the files are corrupted.

### Repair

Recreate `/etc/passwd` and `/etc/group` with the standard Jessie system users/groups. See the reference files in `docs/reference/passwd.default` and `docs/reference/group.default`.

Then:
```bash
echo "root:chip" | chpasswd
echo "chip:chip" | chpasswd
```

## 4. Fix the hostname

```bash
echo "trntbl" > /etc/hostname
hostname trntbl
echo "127.0.0.1 trntbl" >> /etc/hosts
```

## 5. Configure wpa_supplicant

```bash
mkdir -p /etc/wpa_supplicant
cat > /etc/wpa_supplicant/wpa_supplicant.conf << 'EOF'
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YOUR_SSID"
    psk="YOUR_PASSWORD"
    key_mgmt=WPA-PSK
}
EOF
```

## 6. Purge corrupted Python bytecode

After a reflash, the `.pyc` files may be corrupted:

```bash
find /usr/lib/python2.7 -name "*.pyc" -delete
```

## 7. Fix dpkg statoverride

```bash
sed -i '/crontab/d' /var/lib/dpkg/statoverride 2>/dev/null
```

## 8. Deploy openTRNTBL

From the Mac:
```bash
bash firmware/deploy.sh <CHIP_IP>
```

The script:
- Uploads all files
- Configures hostapd, dnsmasq, avahi
- Writes `/etc/rc.local` for auto-boot
- Purges the pyc files
- Starts the portal

## 9. Verify

```bash
curl -s http://trntbl.local/api/wifi/status
# Should return: {"connected": true, "ssid": "...", ...}
```

Open `http://trntbl.local` in a browser → dashboard with the Sonos speakers.

## 10. Power cycle

Unplug/replug the CHIP. Verify that:
- The dashboard shows up (not the WiFi screen)
- The Sonos speakers appear
- The filesystem is `rw`: `mount | grep rootfs`
