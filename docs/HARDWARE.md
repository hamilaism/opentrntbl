# openTRNTBL — Hardware Reference

## Bill of Materials

| Component | Model | Role | Approx price |
|-----------|-------|------|--------------|
| Turntable | TRNTBL by VNYL (any color) | Mechanical base + PCB | Used |
| SBC | C.H.I.P. v1.0 (Next Thing Co.) | Brain — Allwinner R8/A13, 512MB RAM | Used |
| ADC | PCM2900C BurrBrown (on VNYL PCB) | USB audio capture 48kHz | Built-in |
| Amplifier | PAM8403 Gebildet 3W+3W 5V | Boost jack signal → RCA | ~€8 |
| Motor | HYEJET-01 / EG-530SD-3F | Platter drive | Built-in |
| PSU | Mean Well IRM-10-12 | 12V 0.85A | Built-in |
| WiFi/BT | RTL8723BS | WiFi + Bluetooth | Built-in |
| UART | CP2102 USB-Serial | Debug console | ~€5 |
| RCA connectors | Standard (chassis-mounted) | Analog audio output | ~€3 |

## Connections

### UART (U14 header on the main board)

```
Pin 1 — GND  → GND of CP2102
Pin 3 — RXD  → TXD of CP2102
Pin 5 — TXD  → RXD of CP2102
Baudrate: 115200
```

```bash
screen /dev/tty.usbserial-0001 115200
```

### FEL mode

Jumper between FEL and GND on the CHIP header, then plug in micro-USB.

```bash
sunxi-fel ver  # Should respond with the A13 version
```

### Audio

```
BurrBrown PCM2900C (hw:1,0)
  → USB capture 48kHz (MANDATORY, not 44100)
  → Darkice → Icecast → Sonos

sun4i-codec (hw:0,0)
  → 3.5mm jack (signal too weak for direct line-in)
  → PAM8403 (boost)
  → RCA (chassis output)
```

### PAM8403 wiring

```
CHIP 3.5mm jack → PAM8403 input (L/R/GND)
PAM8403 output L → RCA left (tip)
PAM8403 output R → RCA right (tip)
PAM8403 GND → RCA sleeves (common ground)
PAM8403 5V → CHIP USB 5V (or PSU)
```

## Sonos network (reference)

| Speaker | IP |
|---------|-----|
| Roam | 192.168.1.50 |
| Salon-One | 192.168.1.51 |
| Salon-Beam | 192.168.1.52 |
| Salon-One | 192.168.1.53 |
| Chambre | 192.168.1.54 |
| Cuisine | 192.168.1.55 |
| Vynil-Port | 192.168.1.56 |

## NAND

```
Toshiba TC58TEG5DCLTA00
4096 MiB MLC
Erase size: 4096 KiB (0x400000)
Page size: 16384 (0x4000)
OOB size: 1280 (0x500)
Typical bad blocks: 13-16 out of 1024
```
