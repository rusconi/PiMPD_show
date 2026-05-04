#!/bin/bash

# Define the primary and fallback files
PRIMARY_FILE="/opt/PiMPD_show/settings.yaml"
FALLBACK_FILE="settings.yaml"

# Check if the primary file exists
if [ -f "$PRIMARY_FILE" ]; then
    echo "Primary file found. Opening $PRIMARY_FILE with sudo..."
    sudo nano "$PRIMARY_FILE"

# Check if the fallback file exists in the current directory
elif [ -f "$FALLBACK_FILE" ]; then
    echo "Primary not found. Opening local $FALLBACK_FILE with sudo..."
    sudo nano "$FALLBACK_FILE"

# Neither file exists
else
    echo "Error: Neither $PRIMARY_FILE nor a local settings.yaml was found."
fi
