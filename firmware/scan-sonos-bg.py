#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""openTRNTBL — Background Sonos Scanner (parallel)

Scans the full /24 subnet using 15 parallel threads.
Same interface as previous scan-sonos-bg.sh:
  - writes /tmp/trntbl-sonos-fullscan.json
  - updates /home/chip/opentrntbl/sonos_cache.json
  - uses /tmp/trntbl-scan.lock to prevent concurrent runs
"""

import json
import os
import subprocess
import sys
import threading
import urllib2

RESULT_FILE = '/tmp/trntbl-sonos-fullscan.json'
CACHE_FILE = '/home/chip/opentrntbl/sonos_cache.json'
LOCK_FILE = '/tmp/trntbl-scan.lock'
MAX_PARALLEL = 15
HTTP_TIMEOUT = 0.8


def probe(ip):
    # urllib2 is in-process: 10-50x faster than forking curl on the CHIP
    try:
        resp = urllib2.urlopen('http://{}:1400/info'.format(ip), timeout=HTTP_TIMEOUT)
        data = json.loads(resp.read())
        dev = data.get('device', {})
        return {
            'ip': ip,
            'name': dev.get('name', 'Unknown'),
            'model': dev.get('modelDisplayName', dev.get('model', '')),
            'playerId': data.get('playerId', ''),
            'groupId': data.get('groupId', '')
        }
    except:
        return None


def main():
    if os.path.exists(LOCK_FILE):
        sys.exit(0)
    open(LOCK_FILE, 'w').close()

    try:
        with open(RESULT_FILE, 'w') as f:
            json.dump({'scanning': True}, f)

        # Discover subnet from own IP (fallback to 10.0.0.x)
        try:
            own_ip = subprocess.check_output(['hostname', '-I']).strip().split()[0]
            subnet = '.'.join(own_ip.split('.')[:3])
        except:
            subnet = '10.0.0'

        ips = ['{}.{}'.format(subnet, i) for i in range(1, 255)]

        results = []
        lock = threading.Lock()
        sem = threading.Semaphore(MAX_PARALLEL)

        def worker(ip):
            sem.acquire()
            try:
                r = probe(ip)
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

        with open(RESULT_FILE, 'w') as f:
            json.dump({'scanning': False, 'devices': results}, f)

        with open(CACHE_FILE, 'w') as f:
            json.dump([r['ip'] for r in results], f)
    finally:
        try:
            os.remove(LOCK_FILE)
        except:
            pass


if __name__ == '__main__':
    main()
