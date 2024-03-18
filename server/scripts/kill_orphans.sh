#!/bin/bash

# Check if netstat command is available
if ! command -v netstat &> /dev/null; then
    echo "Netstat command not found. Please make sure you are running this script in Windows Subsystem for Linux (WSL)."
    exit 1
fi

# Find the PID of the process listening on port 2000
PID=$(netstat -aon | grep ":2000.*LISTENING" | awk '{print $5}')

if [ -z "$PID" ]; then
    echo "No process found listening on port 2000"
else
    # Terminate the process
    taskkill /f /pid $PID
    echo "Terminated process with PID $PID listening on port 2000"
fi
