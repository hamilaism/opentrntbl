#!/bin/bash
# openTRNTBL — Background Sonos Scanner
# Scans the full subnet and writes results to a JSON file
# Called by Flask when user clicks "Rescanner"

RESULT_FILE="/tmp/trntbl-sonos-fullscan.json"
CACHE_FILE="/home/chip/opentrntbl/sonos_cache.json"
LOCK_FILE="/tmp/trntbl-scan.lock"

# Prevent multiple scans
if [ -f "$LOCK_FILE" ]; then
    exit 0
fi
touch "$LOCK_FILE"

# Write "scanning" status
echo '{"scanning": true}' > "$RESULT_FILE"

found_ips=""
results="["
first=true

for i in $(seq 1 69); do
    ip="10.0.0.$i"
    data=$(curl -s -m 0.4 "http://${ip}:1400/info" 2>/dev/null)
    if [ -n "$data" ] && echo "$data" | python -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        entry=$(echo "$data" | python -c "
import sys, json
try:
    d = json.load(sys.stdin)
    dev = d.get('device', {})
    print(json.dumps({
        'ip': '${ip}',
        'name': dev.get('name', 'Unknown'),
        'model': dev.get('modelDisplayName', dev.get('model', '')),
        'playerId': d.get('playerId', ''),
        'groupId': d.get('groupId', '')
    }))
except:
    pass
" 2>/dev/null)
        if [ -n "$entry" ]; then
            if [ "$first" = true ]; then
                first=false
            else
                results="$results,"
            fi
            results="$results $entry"
            found_ips="$found_ips \"$ip\""
        fi
    fi
done

results="$results ]"

# Write results
echo "{\"scanning\": false, \"devices\": $results}" > "$RESULT_FILE"

# Update cache
if [ -n "$found_ips" ]; then
    echo "[$found_ips]" | sed 's/ /,/g' | sed 's/,\[/[/' > "$CACHE_FILE"
fi

rm -f "$LOCK_FILE"
