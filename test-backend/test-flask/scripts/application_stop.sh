#! /bin/bash
set -e

# Find the process ID of the running application and kill it gracefully
if pgrep gunicorn > /dev/null
then
    pkill -SIGTERM gunicorn
    # Wait for the application to stop
    sleep 10
else
    echo "Gunicorn process not found."
fi
