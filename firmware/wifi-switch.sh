#!/bin/bash
# openTRNTBL — WiFi Switch (AP -> Client)
# Called by Flask after user selects a WiFi network in the captive portal.
# The wpa_supplicant.conf is already saved before this script runs.
# We simply reboot — the boot script will detect the saved config and connect.

LOG="/tmp/trntbl-wifi-switch.log"
echo "$(date) WiFi configured ($1), rebooting in 3 seconds..." > "$LOG"
sleep 3
reboot
