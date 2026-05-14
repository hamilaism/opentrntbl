#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""openTRNTBL by ismo — Portal & API v9 (pre-alpha)
All fixes applied:
- threaded=True (no more UI freeze)
- Native Sonos grouping via x-rincon: (speakers stay in sync)
- Status reads from sonos-monitor state file (no more phantom status)
- Scan keeps cached results visible during full scan
- Proper disconnect with ungroup
- No dependency on wireless-tools (iwgetid/iwconfig/iwlist)
"""

from flask import Flask, request, jsonify, Response
import subprocess
import json
import os
import re
import time as _time
import threading
import urllib2

# Force close_fds=True on every subprocess. Python 2 defaults to False on
# POSIX, so children spawned from API routes (wpa_supplicant -B, dhclient,
# bash &, ...) inherit Flask's :80 listen socket. When Flask later dies
# those orphans keep the socket alive → port :80 zombie until reboot.
_orig_popen_init = subprocess.Popen.__init__
def _popen_init_close_fds(self, *args, **kwargs):
    kwargs.setdefault('close_fds', True)
    _orig_popen_init(self, *args, **kwargs)
subprocess.Popen.__init__ = _popen_init_close_fds

app = Flask(__name__)

CONFIG_FILE = '/home/chip/opentrntbl/config.json'
CACHE_FILE = '/home/chip/opentrntbl/sonos_cache.json'
STATE_FILE = '/tmp/trntbl-sonos-state'
FULLSCAN_FILE = '/tmp/trntbl-sonos-fullscan.json'
DARKICE_CFG = '/etc/darkice.cfg'

# ===================================
# CONFIG
# ===================================

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            cfg = json.load(f)
        if 'sonos_targets' not in cfg:
            cfg['sonos_targets'] = []
        if 'output_mode' not in cfg:
            cfg['output_mode'] = 'sonos'
        if 'rca_enabled' not in cfg:
            cfg['rca_enabled'] = False
        if 'rca_show_ui' not in cfg:
            cfg['rca_show_ui'] = True
        return cfg
    except Exception:
        return {'sonos_targets': [], 'wifi_ssid': None, 'vinyl_priority': False,
                'bitrate': 320, 'output_mode': 'sonos', 'rca_enabled': False, 'rca_show_ui': True}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(cfg, f)
    except Exception:
        pass

def load_cached_ips():
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_cached_ips(ips):
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(ips, f)
    except Exception:
        pass

# ===================================
# SONOS — SOAP helpers
# ===================================

_SOAP_NS = (
    '<?xml version="1.0"?>'
    '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"'
    ' s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
    '<s:Body>'
)
_SOAP_NS_CLOSE = '</s:Body></s:Envelope>'
_SOAP_AVT = 'xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"'

_SOAP_SET_URI = (
    _SOAP_NS
    + '<u:SetAVTransportURI ' + _SOAP_AVT + '>'
    + '<InstanceID>0</InstanceID><CurrentURI>{uri}</CurrentURI>'
    + '<CurrentURIMetaData></CurrentURIMetaData>'
    + '</u:SetAVTransportURI>' + _SOAP_NS_CLOSE
)
_SOAP_PLAY = (
    _SOAP_NS
    + '<u:Play ' + _SOAP_AVT + '>'
    + '<InstanceID>0</InstanceID><Speed>1</Speed>'
    + '</u:Play>' + _SOAP_NS_CLOSE
)
_SOAP_STOP = (
    _SOAP_NS
    + '<u:Stop ' + _SOAP_AVT + '>'
    + '<InstanceID>0</InstanceID>'
    + '</u:Stop>' + _SOAP_NS_CLOSE
)
_SOAP_GET_TRANSPORT = (
    _SOAP_NS
    + '<u:GetTransportInfo ' + _SOAP_AVT + '>'
    + '<InstanceID>0</InstanceID>'
    + '</u:GetTransportInfo>' + _SOAP_NS_CLOSE
)
_SOAP_BECOME_COORD = (
    _SOAP_NS
    + '<u:BecomeCoordinatorOfStandaloneGroup ' + _SOAP_AVT + '>'
    + '<InstanceID>0</InstanceID>'
    + '</u:BecomeCoordinatorOfStandaloneGroup>' + _SOAP_NS_CLOSE
)


def soap_call(ip, action, body):
    try:
        subprocess.call([
            'curl', '-s', '-m', '3', '-X', 'POST',
            'http://{}:1400/MediaRenderer/AVTransport/Control'.format(ip),
            '-H', 'Content-Type: text/xml',
            '-H', 'SOAPAction: "urn:schemas-upnp-org:service:AVTransport:1#{}"'.format(action),
            '-d', body
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        pass

def get_player_id(ip):
    """Get Sonos playerId (RINCON_xxx) for an IP."""
    try:
        resp = urllib2.urlopen('http://{}:1400/info'.format(ip), timeout=2)
        data = json.loads(resp.read())
        return data.get('playerId', '')
    except Exception:
        return ''

def sonos_play_on(ip):
    """Send vinyl stream to a speaker and start playback."""
    chip_ip = subprocess.check_output(['hostname', '-I']).strip()
    stream = 'x-rincon-mp3radio://{}:8000/vinyl'.format(chip_ip)
    soap_call(ip, 'SetAVTransportURI', _SOAP_SET_URI.format(uri=stream))
    soap_call(ip, 'Play', _SOAP_PLAY)

def sonos_stop_on(ip):
    """Stop playback on a speaker."""
    soap_call(ip, 'Stop', _SOAP_STOP)

def sonos_join_group(ip, coordinator_rincon):
    """Join a speaker to a coordinator's group (native Sonos sync)."""
    soap_call(ip, 'SetAVTransportURI',
              _SOAP_SET_URI.format(uri='x-rincon:{}'.format(coordinator_rincon)))

def sonos_leave_group(ip):
    """Remove a speaker from its current group (become standalone)."""
    soap_call(ip, 'BecomeCoordinatorOfStandaloneGroup', _SOAP_BECOME_COORD)

def get_transport_state(ip):
    """Query Sonos GetTransportInfo. Returns 'PLAYING', 'PAUSED_PLAYBACK', 'STOPPED' or '' on error."""
    try:
        out = subprocess.check_output([
            'curl', '-s', '-m', '3', '-X', 'POST',
            'http://{}:1400/MediaRenderer/AVTransport/Control'.format(ip),
            '-H', 'Content-Type: text/xml',
            '-H', 'SOAPAction: "urn:schemas-upnp-org:service:AVTransport:1#GetTransportInfo"',
            '-d', _SOAP_GET_TRANSPORT,
        ], stderr=subprocess.PIPE)
        m = re.search(r'<CurrentTransportState>([^<]+)</CurrentTransportState>', out.decode('utf-8', errors='replace'))
        if m:
            return m.group(1)
    except Exception:
        pass
    return ''

def verify_targets_state_at_boot():
    """At boot, clear selected speakers and reset state.

    Why: the CHIP reboot tore down any x-rincon: group the Sonos was part of,
    but config.json keeps the persisted sonos_targets list. UI was showing
    speakers as "selected" but no actual stream was routed — user had to
    manually disconnect/reconnect to fix it.

    A fresh boot has logically zero selected speakers; user re-selects
    explicitly, which triggers a clean SOAP join group call."""
    try:
        cfg = load_config()
        cfg['sonos_targets'] = []
        save_config(cfg)
    except Exception:
        pass
    try:
        with open(STATE_FILE, 'w') as f:
            f.write('{}')
    except Exception:
        pass

# ===================================
# WIFI
# ===================================

@app.route('/api/wifi/scan')
def wifi_scan():
    # In normal mode (wpa_supplicant running): use wpa_cli (instant, ~50ms)
    # In AP mode (hostapd running): use iw (driver scan, ~3s) since wpa_cli unavailable
    # Both methods produce the same output format (BSSID, freq, signal, flags, SSID)

    networks = []

    # Try wpa_cli first (normal mode)
    wpa_available = subprocess.call(['wpa_cli', '-i', 'wlan0', 'scan'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

    if wpa_available:
        # Cold scans on RTL8723BS often return only the associated AP after
        # the first 2.5s wait. Retry once with a fresh scan trigger if the
        # cache looks sparse (<3 networks), to give the radio time to
        # finish all channels.
        _time.sleep(2.5)
        for _attempt in (1, 2):
            networks = []
            try:
                out = subprocess.check_output(['wpa_cli', '-i', 'wlan0', 'scan_results'],
                                              stderr=subprocess.PIPE)
                for line in out.decode('utf-8', errors='replace').split('\n'):
                    parts = line.split('\t')
                    if len(parts) < 5:
                        continue
                    _, _, signal_dbm, flags, ssid = parts[0], parts[1], parts[2], parts[3], parts[4].strip()
                    if not ssid or ssid == 'TRNTBL-Setup':
                        continue
                    if not signal_dbm.lstrip('-').isdigit():
                        continue
                    dbm = int(signal_dbm)
                    networks.append({
                        'ssid': ssid,
                        'signal': max(0, min(100, 2 * (dbm + 100))),
                        'secured': ('WPA' in flags) or ('WEP' in flags),
                    })
            except Exception:
                pass
            if len(networks) >= 3:
                break
            subprocess.call(['wpa_cli', '-i', 'wlan0', 'scan'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _time.sleep(2.0)
    else:
        # AP mode: wpa_cli unavailable, use iw blocking scan.
        # `iw dev wlan0 scan` (sync) is what worked before — it triggers and
        # waits for the result in one call. Non-disruptive on RTL8723BS in AP
        # mode (verified historically). The earlier "dump-only" optimization
        # broke this flow because the cache is empty in AP mode (no
        # wpa_supplicant maintains it).
        # Optional logging to /tmp/scan-debug.log to keep diag handy.
        debug_log = open('/tmp/scan-debug.log', 'a')
        debug_log.write('=== %s AP scan ===\n' % _time.strftime('%Y-%m-%d %H:%M:%S'))
        _time.sleep(1)  # let any concurrent radio activity settle
        out = ''
        try:
            out = subprocess.check_output(['iw', 'dev', 'wlan0', 'scan'],
                                          stderr=subprocess.PIPE).decode('utf-8', errors='replace')
            debug_log.write('iw scan: %d bytes\n' % len(out))
        except Exception as e:
            debug_log.write('iw scan ERROR: %s\n' % e)
            # Fallback : if blocking scan fails (resource busy), try dump
            # of whatever cache we may have.
            try:
                out = subprocess.check_output(['iw', 'dev', 'wlan0', 'scan', 'dump'],
                                              stderr=subprocess.PIPE).decode('utf-8', errors='replace')
                debug_log.write('fallback dump: %d bytes\n' % len(out))
            except Exception as e2:
                debug_log.write('fallback dump ERROR: %s\n' % e2)
        debug_log.close()
        try:
            current_ssid = None
            current_signal = None
            current_flags = ''

            for line in out.split('\n'):
                line = line.strip()
                if line.startswith('BSS '):
                    if current_ssid and current_signal:
                        if current_ssid != 'TRNTBL-Setup':
                            try:
                                dbm = int(float(current_signal))
                                networks.append({
                                    'ssid': current_ssid,
                                    'signal': max(0, min(100, 2 * (dbm + 100))),
                                    'secured': 'WPA' in current_flags or 'WEP' in current_flags,
                                })
                            except Exception:
                                pass
                    current_ssid = None
                    current_signal = None
                    current_flags = ''
                elif 'SSID: ' in line:
                    current_ssid = line.replace('SSID: ', '').strip()
                elif 'signal: ' in line:
                    try:
                        current_signal = line.split('signal: ')[1].split()[0]
                    except Exception:
                        pass
                elif 'capability: ' in line or 'RSN:' in line or 'WPA:' in line:
                    current_flags += ' ' + line

            if current_ssid and current_signal and current_ssid != 'TRNTBL-Setup':
                try:
                    dbm = int(float(current_signal))
                    networks.append({
                        'ssid': current_ssid,
                        'signal': max(0, min(100, 2 * (dbm + 100))),
                        'secured': 'WPA' in current_flags or 'WEP' in current_flags,
                    })
                except Exception:
                    pass
        except Exception:
            pass

    best = {}
    for n in networks:
        if n['ssid'] not in best or n['signal'] > best[n['ssid']]['signal']:
            best[n['ssid']] = n
    unique = sorted(best.values(), key=lambda x: x['signal'], reverse=True)
    return jsonify({'networks': unique})

@app.route('/api/wifi/rescan', methods=['POST'])
def wifi_rescan():
    # Force a fresh WiFi scan (async, returns immediately)
    # Client polls /api/wifi/scan to get results
    # `iw dev wlan0 scan trigger` is non-disruptive on RTL8723BS, even in AP mode
    # (verified 2026-04-27: hostapd/dnsmasq stay up, AP clients stay connected).
    # The previous AP-mode workaround (kill hostapd → scan → restart) was incorrect
    # and caused the regression "rescan disconnects the phone".
    try:
        subprocess.Popen(['iw', 'dev', 'wlan0', 'scan', 'trigger'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        pass
    return jsonify({'success': True, 'message': 'Scan started, check /api/wifi/scan in 3s'})

@app.route('/api/wifi/connect', methods=['POST'])
def wifi_connect():
    data = request.get_json()
    ssid = data.get('ssid', '')
    password = data.get('password', '')
    try:
        wpa_out = subprocess.check_output(['wpa_passphrase', ssid, password], stderr=subprocess.STDOUT)
        # wpa_passphrase returns only the network={...} block; prepend required header
        config_content = 'ctrl_interface=/var/run/wpa_supplicant\nupdate_config=1\n\n' + wpa_out.decode()
        with open('/tmp/wpa_new.conf', 'w') as f:
            f.write(config_content)
        subprocess.call(['cp', '/tmp/wpa_new.conf', '/etc/wpa_supplicant/wpa_supplicant.conf'])
        cfg = load_config()
        cfg['wifi_ssid'] = ssid
        save_config(cfg)
        # Graceful AP→client transition (no reboot). wifi-to-client.sh starts
        # in background after a short delay so the HTTP response goes out
        # before we drop the AP. If association/DHCP fails, the script
        # auto-falls-back to AP mode via wifi-to-ap.sh.
        subprocess.Popen(['bash', '-c',
                          'sleep 2 && bash /home/chip/opentrntbl/wifi-to-client.sh "$0"', ssid],
                         stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
        return jsonify({'success': True, 'switching': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/wifi/disconnect', methods=['POST'])
def wifi_disconnect():
    """Clear saved WiFi + transition runtime to AP mode (no reboot).

    The previous flow rebooted, but the RTL8723BS driver had a tendency to
    lock up on shutdown → endless SDIO RD RTO spam, requiring hard reset.
    Now we run wifi-to-ap.sh which stops services in the right order and
    rebinds wlan0 as AP host without a kernel-level transition.
    """
    try:
        # Blank out the config first — guarantees a clean AP fallback even
        # if wifi-to-ap.sh crashes mid-flight and we end up rebooting.
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as f:
            f.write('ctrl_interface=/var/run/wpa_supplicant\nupdate_config=1\n')
        cfg = load_config()
        cfg['wifi_ssid'] = None
        save_config(cfg)
        # Run the runtime transition in background, detached from Flask so the
        # HTTP response goes out before we drop the client connection.
        subprocess.Popen(['bash', '-c',
                          'sleep 2 && bash /home/chip/opentrntbl/wifi-to-ap.sh'],
                         stdout=open('/dev/null', 'w'),
                         stderr=open('/dev/null', 'w'))
        return jsonify({'success': True, 'switching_to_ap': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_wifi_info():
    """Shared between /api/wifi/status and /api/status to avoid double polling."""
    try:
        ip = subprocess.check_output(['hostname', '-I'], stderr=subprocess.PIPE).decode().strip()
    except Exception:
        ip = ''
    ssid = ''
    try:
        output = subprocess.check_output(['iw', 'dev', 'wlan0', 'link'], stderr=subprocess.PIPE).decode()
        for line in output.split('\n'):
            if 'SSID:' in line:
                ssid = line.split('SSID:')[1].strip()
                break
    except Exception:
        pass
    signal = 0
    try:
        with open('/proc/net/wireless', 'r') as f:
            for line in f:
                if 'wlan0' in line:
                    parts = line.split()
                    dbm = int(float(parts[3].rstrip('.')))
                    signal = max(0, min(100, 2 * (dbm + 100)))
    except Exception:
        pass
    ap_mode = False
    try:
        with open('/tmp/trntbl-wifi-mode', 'r') as f:
            ap_mode = f.read().strip() == 'ap'
    except Exception:
        pass
    if ap_mode:
        return {'connected': False, 'ssid': '', 'ip': ip, 'signal': 0, 'ap_mode': True}
    connected = bool(ip and not ip.startswith('169.254') and not ip.startswith('192.168.4'))
    return {'connected': connected, 'ssid': ssid, 'ip': ip, 'signal': signal, 'ap_mode': False}

@app.route('/api/wifi/status')
def wifi_status():
    return jsonify(get_wifi_info())

# ===================================
# SONOS — Device type detection
# ===================================

SOUNDBAR_MODELS = ['beam', 'arc', 'ray', 'playbar', 'playbase']

def get_device_type(model):
    ml = model.lower()
    if any(m in ml for m in SOUNDBAR_MODELS):
        return 'soundbar'
    if 'roam' in ml:
        return 'portable'
    if any(m in ml for m in ['one', 'era 100']):
        return 'compact'
    if any(m in ml for m in ['move', 'era 300', 'five']):
        return 'large'
    if 'ace' in ml:
        return 'headphone'
    if any(m in ml for m in ['amp', 'port', 'connect']):
        return 'infra'
    if 'sub' in ml:
        return 'sub'
    return 'unknown'

def enrich_device(d):
    d['type'] = get_device_type(d.get('model', ''))
    pid = d.get('playerId', '')
    gid = d.get('groupId', '')
    d['is_coordinator'] = gid.startswith(pid) if pid else True
    return d

# ===================================
# SONOS — Scan
# ===================================

def probe_sonos(ip):
    # urllib2 is in-process: avoids fork/exec of curl per probe (huge on CHIP)
    try:
        resp = urllib2.urlopen('http://{}:1400/info'.format(ip), timeout=0.8)
        data = json.loads(resp.read())
        dev = data.get('device', {})
        return enrich_device({
            'ip': ip,
            'name': dev.get('name', 'Unknown'),
            'model': dev.get('modelDisplayName', dev.get('model', '')),
            'playerId': data.get('playerId', ''),
            'groupId': data.get('groupId', '')
        })
    except Exception:
        return None

def probe_many(ips, max_concurrent=15):
    """Probe a list of IPs in parallel, return list of results (non-None only)."""
    results = []
    lock = threading.Lock()
    sem = threading.Semaphore(max_concurrent)

    def worker(ip):
        sem.acquire()
        try:
            r = probe_sonos(ip)
            if r:
                with lock:
                    results.append(r)
        finally:
            sem.release()

    threads = [threading.Thread(target=worker, args=(ip,)) for ip in ips]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=3)
    return results

def scan_cached():
    cached = load_cached_ips()
    raw = probe_many(cached)
    found_ips = [r['ip'] for r in raw]
    if found_ips:
        save_cached_ips(found_ips)
    return raw

def group_by_rooms(raw):
    """Group by room name to handle surround setups (same name = pick soundbar).
    Multiroom groups are NOT merged — each speaker shows individually."""
    rooms = {}
    for d in raw:
        if d.get('type') == 'sub':
            continue
        if d['name'] not in rooms:
            rooms[d['name']] = []
        rooms[d['name']].append(d)

    speakers = []
    for name, devs in rooms.items():
        # Surround setup: same room name, multiple devices → pick the soundbar
        sbars = [d for d in devs if d.get('type') == 'soundbar']
        if sbars:
            t = sbars[0]
            t['display_type'] = 'homecinema' if len(devs) > 1 else 'soundbar'
        elif len(devs) == 1:
            t = devs[0]
            t['display_type'] = t.get('type', 'unknown')
        else:
            coords = [d for d in devs if d.get('is_coordinator')]
            t = coords[0] if coords else devs[0]
            t['display_type'] = t.get('type', 'unknown')

        speakers.append({
            'ip': t['ip'],
            'name': name,
            'room': name,
            'model': t.get('model', ''),
            'type': t.get('display_type', t.get('type', 'unknown')),
            'playerId': t.get('playerId', ''),
            'members': []
        })

    speakers.sort(key=lambda s: s['name'])
    return speakers

# ===================================
# SONOS — Scan endpoints
# ===================================

@app.route('/api/sonos/scan')
def sonos_scan():
    try:
        full = request.args.get('full', '0') == '1'
        if full:
            subprocess.Popen(
                ['python', '/home/chip/opentrntbl/scan-sonos-bg.py'],
                stdout=open('/dev/null', 'w'),
                stderr=open('/dev/null', 'w')
            )
        raw = scan_cached()
        speakers = group_by_rooms(raw)
        cfg = load_config()
        selected_ips = [t['ip'] for t in cfg.get('sonos_targets', [])]
        if cfg.get('output_mode') == 'rca':
            selected_ips = ['rca']
        return jsonify({
            'speakers': speakers,
            'selected': selected_ips,
            'scanning': full
        })
    except Exception as e:
        return jsonify({'speakers': [], 'selected': [], 'scanning': False, 'error': str(e)})

@app.route('/api/sonos/scan/status')
def sonos_scan_status():
    try:
        with open(FULLSCAN_FILE, 'r') as f:
            data = json.load(f)
        if data.get('scanning'):
            return jsonify({'scanning': True})
        devices = data.get('devices', [])
        raw = [enrich_device(d) for d in devices]
        speakers = group_by_rooms(raw)
        cfg = load_config()
        selected_ips = [t['ip'] for t in cfg.get('sonos_targets', [])]
        if cfg.get('output_mode') == 'rca':
            selected_ips = ['rca']
        try:
            os.remove(FULLSCAN_FILE)
        except Exception:
            pass
        return jsonify({
            'scanning': False,
            'speakers': speakers,
            'selected': selected_ips
        })
    except Exception:
        return jsonify({'scanning': False})

# ===================================
# SONOS — Select with native grouping
# ===================================

@app.route('/api/sonos/select', methods=['POST'])
def sonos_select():
    data = request.get_json()
    ip = data.get('ip', '')
    name = data.get('name', '')
    cfg = load_config()
    targets = cfg.get('sonos_targets', [])

    # Special case: RCA is treated as a pseudo-speaker. Selecting RCA is
    # mutually exclusive with any Sonos — switches the single audio
    # consumer from Darkice (→ Icecast) to alsaloop (→ jack/RCA).
    if ip == 'rca':
        if cfg.get('output_mode') == 'rca':
            # Deselect RCA: go back to idle (no output consumer)
            cfg['output_mode'] = 'sonos'
            save_config(cfg)
            subprocess.call(['pkill', 'alsaloop'])
            return jsonify({'success': True, 'action': 'removed', 'targets': targets})
        # Select RCA: disconnect any Sonos first (in parallel)
        parallel_soap(targets, sonos_leave_group)
        _time.sleep(0.5)
        parallel_soap(targets, sonos_stop_on)
        cfg['sonos_targets'] = []
        cfg['output_mode'] = 'rca'
        save_config(cfg)
        apply_output_mode('rca')
        return jsonify({'success': True, 'action': 'added', 'targets': [], 'output_mode': 'rca'})

    # If RCA was active and we're now selecting a Sonos, switch back to Sonos mode
    if cfg.get('output_mode') == 'rca':
        cfg['output_mode'] = 'sonos'
        save_config(cfg)
        apply_output_mode('sonos')
        # Give Darkice ~2s to register with Icecast before we tell Sonos to pull
        _time.sleep(2)

    existing = [t for t in targets if t['ip'] == ip]

    if existing:
        # Deselect: ungroup from Sonos, remove from targets
        targets = [t for t in targets if t['ip'] != ip]
        sonos_leave_group(ip)
        _time.sleep(0.5)
        sonos_stop_on(ip)
        cfg['sonos_targets'] = targets
        save_config(cfg)
        return jsonify({'success': True, 'action': 'removed', 'targets': targets})
    else:
        # Select: add to targets
        targets.append({'ip': ip, 'name': name})
        cfg['sonos_targets'] = targets
        save_config(cfg)

        if len(targets) == 1:
            # First speaker — send stream directly
            sonos_play_on(ip)
        else:
            # Additional speaker — group with first speaker (native Sonos sync)
            coordinator_ip = targets[0]['ip']
            coordinator_rincon = get_player_id(coordinator_ip)
            if coordinator_rincon:
                sonos_join_group(ip, coordinator_rincon)
            else:
                # Fallback: send stream directly (no sync but works)
                sonos_play_on(ip)

        return jsonify({'success': True, 'action': 'added', 'targets': targets})

def parallel_soap(targets, fn):
    """Run a single-arg SOAP function against every target in parallel threads."""
    threads = [threading.Thread(target=fn, args=(t['ip'],)) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)

@app.route('/api/sonos/disconnect', methods=['POST'])
def sonos_disconnect():
    cfg = load_config()
    targets = cfg.get('sonos_targets', [])
    # Ungroup in parallel (was sequential: N * 3s → now ~3s total)
    parallel_soap(targets, sonos_leave_group)
    _time.sleep(0.5)
    parallel_soap(targets, sonos_stop_on)
    cfg['sonos_targets'] = []
    save_config(cfg)
    return jsonify({'success': True})

# ===================================
# SETTINGS
# ===================================

@app.route('/api/settings/priority', methods=['GET', 'POST'])
def settings_priority():
    cfg = load_config()
    if request.method == 'POST':
        data = request.get_json()
        cfg['vinyl_priority'] = data.get('enabled', False)
        save_config(cfg)
        return jsonify({'success': True, 'enabled': cfg['vinyl_priority']})
    return jsonify({'enabled': cfg.get('vinyl_priority', False)})

@app.route('/api/settings/bitrate', methods=['GET', 'POST'])
def settings_bitrate():
    if request.method == 'POST':
        data = request.get_json()
        bitrate = data.get('bitrate', 320)
        if bitrate not in [128, 192, 256, 320]:
            return jsonify({'success': False, 'error': 'Invalid bitrate'})
        try:
            with open(DARKICE_CFG, 'r') as f:
                content = f.read()
            content = re.sub(r'bitrate\s*=\s*\d+', 'bitrate        = {}'.format(bitrate), content)
            with open(DARKICE_CFG, 'w') as f:
                f.write(content)
            subprocess.call(['pkill', 'darkice'])
            _time.sleep(1)
            subprocess.Popen(['darkice', '-c', DARKICE_CFG],
                             stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
            cfg = load_config()
            cfg['bitrate'] = bitrate
            save_config(cfg)
            return jsonify({'success': True, 'bitrate': bitrate})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
        cfg = load_config()
        return jsonify({'bitrate': cfg.get('bitrate', 320)})

@app.route('/api/settings/rca-enabled', methods=['GET', 'POST'])
def settings_rca_enabled():
    cfg = load_config()
    if request.method == 'POST':
        data = request.get_json()
        enabled = data.get('enabled', False)
        cfg['rca_enabled'] = enabled
        save_config(cfg)
        return jsonify({'success': True, 'enabled': cfg['rca_enabled']})
    return jsonify({'enabled': cfg.get('rca_enabled', False)})

@app.route('/api/settings/rca-show-ui', methods=['GET', 'POST'])
def settings_rca_show_ui():
    cfg = load_config()
    if request.method == 'POST':
        data = request.get_json()
        enabled = data.get('enabled', True)
        cfg['rca_show_ui'] = enabled
        save_config(cfg)
        return jsonify({'success': True, 'enabled': cfg['rca_show_ui']})
    return jsonify({'enabled': cfg.get('rca_show_ui', True)})

# ===================================
# OUTPUT MODE — sonos (WiFi streaming) vs rca (local jack/PAM)
# ===================================
# Running both Darkice and alsaloop saturates the single-core CHIP
# (load avg 4+). One consumer at a time keeps the CPU under control.

def apply_output_mode(mode):
    """Kill all audio consumers, then start only the one matching mode."""
    subprocess.call(['pkill', 'darkice'])
    subprocess.call(['pkill', 'alsaloop'])
    _time.sleep(1)
    if mode == 'sonos':
        subprocess.Popen(['darkice', '-c', DARKICE_CFG],
                         stdout=open('/dev/null', 'w'),
                         stderr=open('/dev/null', 'w'))
    elif mode == 'rca':
        # Single consumer of hw:1,0 → no need for dsnoop indirection
        subprocess.Popen([
            'alsaloop', '-C', 'plughw:1,0', '-P', 'boosted_jack',
            '-r', '48000', '-c', '2', '-f', 'S16_LE', '-t', '50000'
        ], stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))

@app.route('/api/settings/output-mode', methods=['GET', 'POST'])
def settings_output_mode():
    cfg = load_config()
    if request.method == 'POST':
        data = request.get_json()
        mode = data.get('mode', 'sonos')
        if mode not in ('sonos', 'rca'):
            return jsonify({'success': False, 'error': 'Invalid mode'})
        cfg['output_mode'] = mode
        save_config(cfg)
        apply_output_mode(mode)
        return jsonify({'success': True, 'mode': mode})
    return jsonify({'mode': cfg.get('output_mode', 'sonos')})

# ===================================
# STATUS — reads from sonos-monitor state file
# ===================================

@app.route('/api/status')
def status():
    cfg = load_config()
    targets = cfg.get('sonos_targets', [])

    # Read live state from sonos-monitor (not config)
    sonos_states = {}
    if targets:
        try:
            with open(STATE_FILE, 'r') as f:
                content = f.read().strip()
                if content.startswith('{'):
                    sonos_states = json.loads(content)
                else:
                    for t in targets:
                        sonos_states[t['ip']] = content
        except Exception:
            pass

    # Determine overall state from monitor data
    if not targets:
        overall = 'disconnected'
    elif not sonos_states:
        # Monitor hasn't reported yet — show as connecting
        overall = 'connecting'
    elif all(sonos_states.get(t['ip']) == 'playing' for t in targets):
        overall = 'playing'
    elif any(sonos_states.get(t['ip']) == 'playing' for t in targets):
        overall = 'partial'
    elif any(sonos_states.get(t['ip']) == 'taken' for t in targets):
        overall = 'taken'
    elif any(sonos_states.get(t['ip']) == 'unreachable' for t in targets):
        overall = 'unreachable'
    else:
        overall = 'unknown'

    target_names = ', '.join(t['name'] for t in targets) if targets else None
    uptime = ''
    try:
        with open('/proc/uptime', 'r') as f:
            secs = int(float(f.read().split()[0]))
            uptime = '{}h {:02d}m'.format(secs // 3600, (secs % 3600) // 60)
    except Exception:
        pass

    return jsonify({
        'sonos_targets': targets,
        'sonos_names': target_names,
        'sonos_state': overall,
        'sonos_states': sonos_states,
        'vinyl_priority': cfg.get('vinyl_priority', False),
        'bitrate': cfg.get('bitrate', 320),
        'output_mode': cfg.get('output_mode', 'sonos'),
        'rca_enabled': cfg.get('rca_enabled', False),
        'rca_show_ui': cfg.get('rca_show_ui', True),
        'uptime': uptime,
        'version': 'openTRNTBL pre-alpha',
        'wifi': get_wifi_info()
    })

# ===================================
# HTML
# ===================================

@app.route('/')
def index():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
    try:
        with open(p, 'r') as f:
            return Response(f.read(), mimetype='text/html')
    except Exception:
        return '<h1>openTRNTBL</h1><p>index.html not found</p>'

@app.route('/i18n.js')
def i18n_js():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'i18n.js')
    try:
        with open(p, 'r') as f:
            return Response(f.read(), mimetype='application/javascript')
    except Exception:
        return Response('// i18n.js not found', mimetype='application/javascript', status=404)

@app.route('/tokens.css')
def tokens_css():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tokens.css')
    try:
        with open(p, 'r') as f:
            return Response(f.read(), mimetype='text/css')
    except Exception:
        return Response('/* tokens.css not found */', mimetype='text/css', status=404)

@app.route('/components.css')
def components_css():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'components.css')
    try:
        with open(p, 'r') as f:
            return Response(f.read(), mimetype='text/css')
    except Exception:
        return Response('/* components.css not found */', mimetype='text/css', status=404)

@app.route('/themes.css')
def themes_css():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'themes.css')
    try:
        with open(p, 'r') as f:
            return Response(f.read(), mimetype='text/css')
    except Exception:
        return Response('/* themes.css not found */', mimetype='text/css', status=404)

@app.route('/<path:path>')
def catch_all(path):
    if path.startswith('api/'):
        return jsonify({'error': 'not found'}), 404
    return index()

if __name__ == '__main__':
    if not os.path.exists(CONFIG_FILE):
        save_config({
            'sonos_targets': [], 'wifi_ssid': None, 'vinyl_priority': False,
            'bitrate': 320, 'output_mode': 'sonos', 'rca_enabled': False, 'rca_show_ui': True,
        })
    # Validate Sonos targets state at boot — avoids stale "playing" UI after reboot
    # Run in background thread so Flask starts without waiting for SOAP queries (3s × N speakers)
    threading.Thread(target=verify_targets_state_at_boot).start()
    app.run(host='0.0.0.0', port=80, threaded=True)
