# openTRNTBL — CHIP NAND reflash guide

This guide documents the complete procedure for reflashing the NAND of a C.H.I.P.
when the UBIFS filesystem is corrupted (read-only, bad nodes, boot loops).

## Prerequisites

- Mac with Apple Silicon (tested on M3 Max)
- UTM installed (`brew install --cask utm`)
- Micro-USB cable
- USB UART adapter (CP2102 recommended)
- CHIP with access to the FEL header (jumper or wire)

## Overview

The flash is done in 3 phases:
1. **FEL phase** — Write SPL + U-Boot via USB (Linux VM)
2. **Fastboot phase** — Write UBI/rootfs via USB (Mac directly)
3. **Post-flash** — System config + openTRNTBL deploy

The Linux VM handles FEL (reliable Linux USB drivers). The Mac handles fastboot (faster, no UTM USB timing issues).

---

## Phase 1: Prepare the UTM VM

### Download Ubuntu Server ARM

```bash
cd ~/Downloads
curl -L -o ubuntu-server-arm.iso \
  "https://cdimage.ubuntu.com/releases/24.04.4/release/ubuntu-24.04.4-live-server-arm64.iso"
```

### Create the VM

1. UTM → Create New VM → **Virtualize** → Linux
2. Boot ISO: `ubuntu-server-arm.iso`
3. RAM: 2048 MB / Disk: 10 GB
4. Install Ubuntu (user: `chip`, pass: `chip`, hostname: `flasher`)
5. After install, in UTM: **Input → USB → Share USB devices**

### Install the tools in the VM

```bash
ssh chip@<VM_IP>
sudo apt update
sudo apt install -y git sunxi-tools u-boot-tools fastboot adb
git clone https://github.com/Thore-Krug/Flash-CHIP.git ~/Flash-CHIP
cd ~/Flash-CHIP/CHIP-tools
sed -i 's/-i 0x1f3a//g' common.sh chip-fel-flash.sh
sed -i 's/ -u//g' common.sh chip-fel-flash.sh
```

---

## Phase 2: FEL flash (SPL + U-Boot)

### Put the CHIP into FEL mode

1. Jumper FEL → GND on the U14 header
2. Connect the micro-USB to the Mac
3. In UTM, attach the "Allwinner" device to the VM

### Run the flash

```bash
cd ~/Flash-CHIP && sudo ./Flash.sh
```

Type **s** (server headless).

The script will:
- Detect the NAND (erasesize, pagesize, oobsize)
- Download the images from the NTC mirror
- Write SPL + U-Boot via FEL
- Switch to fastboot mode

### Critical USB timing

When you see `waiting for fastboot...`:
- The CHIP changes USB identity (FEL → fastboot)
- **Detach the USB from the VM** in UTM
- The Mac will see the fastboot device

### Install fastboot on the Mac

```bash
brew install android-platform-tools
```

---

## Phase 3: UBI flash (rootfs) via fastboot on the Mac

### Prepare the sparse image

The file `chip-400000-4000-500.ubi.sparse` is in the VM's images folder.

```bash
scp chip@<VM_IP>:~/Flash-CHIP/CHIP-tools/.dl/stable-server-b149/chip-400000-4000-500.ubi.sparse \
  ~/Downloads/chip.ubi.sparse
```

### Flash

Terminal 1 (Mac — waiting):
```bash
fastboot flash UBI ~/Downloads/chip.ubi.sparse
```

Re-run Flash.sh in the VM to write SPL + U-Boot, then as soon as `waiting for fastboot` appears, detach the USB from UTM. The Mac picks up the device and flashes the UBI (~3 min, 11 chunks).

### Verification

You should see:
```
Sending sparse 'UBI' 1/11 ... OKAY
Writing 'UBI' ... OKAY
...
Sending sparse 'UBI' 11/11 ... OKAY
Writing 'UBI' ... OKAY
Finished. Total time: ~187s
```

---

## Phase 4: Post-flash

### First boot

1. Remove the FEL jumper
2. Unplug the micro-USB
3. Plug in the UART (GND→Pin1, RXD→Pin3, TXD→Pin5)
4. Plug the micro-USB back in (normal boot)
5. `screen /dev/tty.usbserial-0001 115200`

Login: `chip` / `chip`

### Verify the filesystem

```bash
mount | grep rootfs
# Should show: ubi0:rootfs on / type ubifs (rw,relatime)
df -h
```

### Fix the system users/groups (if missing)

After a reflash, `/etc/passwd` and `/etc/group` may be empty. If `systemd-tmpfiles` crashes at boot, see the "passwd/group repair" section in INSTALL-GUIDE.md.

### Connect to WiFi

```bash
sudo nmcli dev wifi connect "SSID" password "PASSWORD"
```

### Next

Follow `docs/INSTALL-GUIDE.md` for the openTRNTBL installation.

---

## Troubleshooting

### `nand write failed -5`
NAND bad blocks are not handled by raw `nand write`. Use fastboot (which skips bad blocks automatically).

### `musb-hdrc: peripheral reset irq lost!`
Non-fatal warning. The CHIP's USB driver times out on the handshake — the transfer continues anyway.

### `waiting for fastboot... TIMEOUT`
The CHIP changes USB identity between FEL and fastboot. Detach the USB from the VM so the Mac can see it.

### `Address already in use` (port 80)
```bash
pkill -9 -f "python app.py"
sleep 2
cd /home/chip/opentrntbl && python app.py > /tmp/trntbl-portal.log 2>&1 &
```

### NAND with many bad blocks
Check at UART boot: `Bad eraseblock X at 0xYYY`. Up to ~20 bad blocks out of 1024 is normal for an MLC NAND of this age. Beyond that, the NAND is at end-of-life.
