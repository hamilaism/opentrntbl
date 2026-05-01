# openTRNTBL API Reference

**Version:** openTRNTBL pre-alpha  
**Base URL:** `http://trntbl.local` or `http://<IP>`  
**Format:** JSON (all endpoints return `application/json`)

---

## Status & System

### GET `/api/status`

Complete dashboard state: WiFi, Sonos targets, streaming state, settings, and uptime.

**Response:**
```json
{
  "sonos_targets": [
    { "ip": "192.168.1.50", "name": "Roam" },
    { "ip": "192.168.1.51", "name": "Salon-One" }
  ],
  "sonos_names": "Roam, Salon-One",
  "sonos_state": "playing",
  "sonos_states": {
    "192.168.1.50": "playing",
    "192.168.1.51": "playing"
  },
  "vinyl_priority": false,
  "bitrate": 320,
  "output_mode": "sonos",
  "rca_enabled": false,
  "rca_show_ui": true,
  "uptime": "5h 42m",
  "version": "openTRNTBL pre-alpha",
  "wifi": {
    "connected": true,
    "ssid": "MyHomeWiFi",
    "ip": "<YOUR-CHIP-IP>",
    "signal": 85,
    "ap_mode": false
  }
}
```

**State values:**

- `sonos_state`: `"disconnected"` | `"connecting"` | `"playing"` | `"partial"` | `"taken"` | `"unreachable"` | `"unknown"`
- `output_mode`: `"sonos"` | `"rca"`

---

## WiFi Management

### GET `/api/wifi/status`

Current WiFi connection state (IP, SSID, signal strength, mode).

**Response (connected):**
```json
{
  "connected": true,
  "ssid": "MyHomeWiFi",
  "ip": "<YOUR-CHIP-IP>",
  "signal": 85,
  "ap_mode": false
}
```

**Response (AP mode):**
```json
{
  "connected": false,
  "ssid": "",
  "ip": "192.168.4.1",
  "signal": 0,
  "ap_mode": true
}
```

### GET `/api/wifi/scan`

List available WiFi networks (sorted by signal strength).

**Response:**
```json
{
  "networks": [
    { "ssid": "MyHomeWiFi", "signal": 92, "secured": true },
    { "ssid": "Guest", "signal": 78, "secured": true },
    { "ssid": "TRNTBL-5G", "signal": 45, "secured": true }
  ]
}
```

**Notes:**

- Signal: 0–100 (calculated from dBm)
- `TRNTBL-Setup` is always filtered out
- Normal mode (wpa_supplicant): ~50ms | AP mode (hostapd): ~3s

### POST `/api/wifi/rescan`

Trigger background WiFi scan. Return immediately; client polls `/api/wifi/scan` for results.

**Request:** `{}`

**Response:**
```json
{
  "success": true,
  "message": "Scan started, check /api/wifi/scan in 3s"
}
```

### POST `/api/wifi/connect`

Connect to a WiFi network. Triggers reboot via `wifi-switch.sh`.

**Request:**
```json
{
  "ssid": "MyHomeWiFi",
  "password": "mypassword"
}
```

**Response (success):**
```json
{
  "success": true,
  "switching": true
}
```

**Response (error):**
```json
{
  "success": false,
  "error": "Invalid password"
}
```

**Notes:**

- Reboot happens asynchronously after ~2 seconds
- CHIP will be unreachable for ~30 seconds
- On failure, CHIP boots into AP mode

### POST `/api/wifi/disconnect`

Clear saved WiFi and reboot. On next boot, `TRNTBL-Setup` AP will launch.

**Request:** `{}`

**Response:**
```json
{
  "success": true,
  "rebooting": true
}
```

---

## Sonos Speaker Discovery & Control

### GET `/api/sonos/scan`

Discover Sonos speakers. Returns cached results immediately; `?full=1` triggers background scan.

**Query params:**

- `full=1` (optional) — Trigger full subnet scan

**Response:**
```json
{
  "speakers": [
    {
      "ip": "192.168.1.50",
      "name": "Roam",
      "room": "Roam",
      "model": "Roam",
      "type": "portable",
      "playerId": "RINCON_XXXXXXXXXXXX",
      "members": []
    }
  ],
  "selected": ["192.168.1.50"],
  "scanning": false
}
```

**Speaker types:**

- `"soundbar"` — Beam, Arc, Ray, PlayBar, PlayBase
- `"portable"` — Roam
- `"compact"` — One, Era 100
- `"large"` — Move, Era 300, Five
- `"headphone"` — Ace
- `"infra"` — Amp, Port, Connect
- `"sub"` — Sub
- `"homecinema"` — Soundbar + surrounds

### GET `/api/sonos/scan/status`

Check if full scan is complete.

**Response (scanning):**
```json
{
  "scanning": true
}
```

**Response (complete):**
```json
{
  "scanning": false,
  "speakers": [...],
  "selected": ["192.168.1.50"]
}
```

### POST `/api/sonos/select`

Add or remove a speaker from targets. Native Sonos grouping for multiroom sync.

**Request (add):**
```json
{
  "ip": "192.168.1.50",
  "name": "Roam"
}
```

**Response (added):**
```json
{
  "success": true,
  "action": "added",
  "targets": [{"ip": "192.168.1.50", "name": "Roam"}]
}
```

**Special case — RCA:**
```json
{
  "ip": "rca",
  "name": ""
}
```

Selecting RCA stops all Sonos and switches to local RCA output. Selecting any Sonos while RCA is active switches back to Sonos mode.

### POST `/api/sonos/disconnect`

Stop all speakers and clear targets.

**Request:** `{}`

**Response:**
```json
{
  "success": true
}
```

---

## Settings

### GET `/api/settings/bitrate`

Current stream bitrate.

**Response:**
```json
{
  "bitrate": 320
}
```

### POST `/api/settings/bitrate`

Change bitrate and restart Darkice.

**Request:**
```json
{
  "bitrate": 256
}
```

**Response (success):**
```json
{
  "success": true,
  "bitrate": 256
}
```

**Valid values:** 128, 192, 256, 320 (kbps)

### GET/POST `/api/settings/priority`

Vinyl priority (auto-pause speakers when turntable stops).

**POST request:**
```json
{
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "enabled": true
}
```

### GET/POST `/api/settings/rca-enabled`

Hardware RCA presence flag (set at deploy time).

**GET Response:**
```json
{
  "enabled": false
}
```

**POST request:**
```json
{
  "enabled": true
}
```

**Notes:** When `false`, RCA section hidden from UI

### GET/POST `/api/settings/rca-show-ui`

User preference for showing RCA toggle.

**GET Response:**
```json
{
  "enabled": true
}
```

**POST request:**
```json
{
  "enabled": false
}
```

### GET/POST `/api/settings/output-mode`

Switch between Sonos streaming and RCA output.

**GET Response:**
```json
{
  "mode": "sonos"
}
```

**POST request:**
```json
{
  "mode": "rca"
}
```

**Valid values:** `"sonos"` | `"rca"`

**Notes:**

- Running both Darkice and alsaloop saturates single-core CHIP (load > 4)
- Only one output consumer at a time
- ~1s gap during switch

---

## Streaming URL

Once speakers are selected:

```text
http://<YOUR-CHIP-IP>:8000/vinyl
```

**Format:** MP3, 48 kHz, configurable bitrate (128/192/256/320 kbps)  
**Shareable to:** iOS/Android apps, desktop media players, manual UPnP/DLNA renderers

---

## Error Handling

All endpoints return JSON. Errors include an `error` field:

```json
{
  "success": false,
  "error": "Speaker unreachable"
}
```

**Common issues:**

- WiFi scan: 2.5s (normal) or 3s (AP) on first call, then cached
- Speaker unreachable: network issue or offline
- Invalid bitrate: must be 128, 192, 256, or 320
- Config file missing: auto-created on first run

---

## Quick Examples

### Connect to WiFi
```bash
curl -X POST http://trntbl.local/api/wifi/connect \
  -H 'Content-Type: application/json' \
  -d '{"ssid":"MyWiFi","password":"secret"}'
```

### Scan speakers (full)
```bash
curl 'http://trntbl.local/api/sonos/scan?full=1'
sleep 3
curl http://trntbl.local/api/sonos/scan/status
```

### Select speaker
```bash
curl -X POST http://trntbl.local/api/sonos/select \
  -H 'Content-Type: application/json' \
  -d '{"ip":"192.168.1.50","name":"Roam"}'
```

### Check status
```bash
curl http://trntbl.local/api/status | jq '.sonos_state, .bitrate, .wifi.ssid'
```
