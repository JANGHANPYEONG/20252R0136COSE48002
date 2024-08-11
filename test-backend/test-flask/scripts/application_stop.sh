#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive

# Grant execute permissions to all files in the scripts/
if [ -d "/home/ubuntu/deeplant-admin/scripts" ]; then
    echo "Granting execute permissions to all files in the scripts folder"
    chmod +x /home/ubuntu/deeplant-admin/scripts/*
else
    echo "Scripts folder does not exist yet. Skipping permission change."
fi

# Find the process ID of the running application and kill it gracefully
if pgrep gunicorn > /dev/null
then
    pkill -SIGTERM gunicorn
    # Wait for the application to stop
    sleep 10
else
    echo "Gunicorn process not found."
fi
