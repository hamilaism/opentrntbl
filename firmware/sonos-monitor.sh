#!/bin/bash
# openTRNTBL — Sonos Monitor & Vinyl Priority
# Polls selected Sonos speakers every 10s
# Writes state to /tmp/trntbl-sonos-state as JSON
# Re-sends vinyl if priority enabled and vinyl is playing

CONFIG="/home/chip/opentrntbl/config.json"
STATE_FILE="/tmp/trntbl-sonos-state"
LOG="/tmp/trntbl-monitor.log"
POLL_INTERVAL=10
SILENCE_THRESHOLD="0.05"

log() { echo "$(date '+%H:%M:%S') $1" >> "$LOG"; }

get_targets() {
    python -c "
import json
try:
    with open('$CONFIG') as f:
        targets = json.load(f).get('sonos_targets', [])
        for t in targets:
            print('%s|%s' % (t['ip'], t['name']))
except:
    pass
" 2>/dev/null
}

get_config_value() {
    python -c "
import json
try:
    with open('$CONFIG') as f:
        print(json.load(f).get('$1', '$2'))
except:
    print('$2')
" 2>/dev/null
}

check_signal() {
    curl -s -m 4 http://localhost:8000/vinyl | mpg123 -q -w /tmp/monitor-test.wav - 2>/dev/null
    local rms=$(sox /tmp/monitor-test.wav -n stat 2>&1 | grep "RMS     amplitude" | head -1 | awk '{print $3}')
    rm -f /tmp/monitor-test.wav
    python -c "print('yes' if float('${rms:-0}') > float('$SILENCE_THRESHOLD') else 'no')" 2>/dev/null
}

get_sonos_uri() {
    local ip="$1"
    curl -s -m 2 -X POST "http://${ip}:1400/MediaRenderer/AVTransport/Control" \
        -H "Content-Type: text/xml" \
        -H 'SOAPAction: "urn:schemas-upnp-org:service:AVTransport:1#GetMediaInfo"' \
        -d '<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:GetMediaInfo xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:GetMediaInfo></s:Body></s:Envelope>' 2>/dev/null | \
        sed -n 's/.*<CurrentURI>\(.*\)<\/CurrentURI>.*/\1/p' 2>/dev/null
}

soap_play() {
    local ip="$1"
    local chip_ip=$(hostname -I | tr -d ' ')
    local stream="x-rincon-mp3radio://${chip_ip}:8000/vinyl"
    curl -s -m 3 -X POST "http://${ip}:1400/MediaRenderer/AVTransport/Control" \
        -H "Content-Type: text/xml" \
        -H 'SOAPAction: "urn:schemas-upnp-org:service:AVTransport:1#SetAVTransportURI"' \
        -d "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:SetAVTransportURI xmlns:u=\"urn:schemas-upnp-org:service:AVTransport:1\"><InstanceID>0</InstanceID><CurrentURI>${stream}</CurrentURI><CurrentURIMetaData></CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>" > /dev/null 2>&1
    curl -s -m 3 -X POST "http://${ip}:1400/MediaRenderer/AVTransport/Control" \
        -H "Content-Type: text/xml" \
        -H 'SOAPAction: "urn:schemas-upnp-org:service:AVTransport:1#Play"' \
        -d '<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Play></s:Body></s:Envelope>' > /dev/null 2>&1
}

log "Sonos monitor started"
echo '{}' > "$STATE_FILE"

while true; do
    sleep "$POLL_INTERVAL"

    targets=$(get_targets)
    if [ -z "$targets" ]; then
        echo '{}' > "$STATE_FILE"
        continue
    fi

    chip_ip=$(hostname -I | tr -d ' ')
    states="{"
    first=true
    need_priority=false
    taken_ips=""

    while IFS='|' read -r ip name; do
        [ -z "$ip" ] && continue
        uri=$(get_sonos_uri "$ip")

        if echo "$uri" | grep -q "${chip_ip}:8000/vinyl"; then
            state="playing"
        elif echo "$uri" | grep -q "^x-rincon:"; then
            # Speaker is grouped with another speaker (native Sonos sync)
            # If we set up the group, it's playing our stream
            state="playing"
        elif [ -z "$uri" ]; then
            state="unreachable"
        else
            state="taken"
            need_priority=true
            taken_ips="$taken_ips $ip"
        fi

        if [ "$first" = true ]; then
            first=false
        else
            states="$states,"
        fi
        states="$states \"$ip\": \"$state\""
    done <<< "$targets"

    states="$states}"
    echo "$states" > "$STATE_FILE"

    # Handle vinyl priority
    if [ "$need_priority" = true ]; then
        priority=$(get_config_value "vinyl_priority" "false")
        if [ "$priority" = "true" ] || [ "$priority" = "True" ]; then
            signal=$(check_signal)
            if [ "$signal" = "yes" ]; then
                for ip in $taken_ips; do
                    log "Re-sending vinyl to $ip"
                    soap_play "$ip"
                done
            else
                log "Vinyl silent — not overriding"
            fi
        fi
    fi
done
