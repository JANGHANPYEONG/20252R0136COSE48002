#!/bin/bash
set -e

# Send a request to the application and check for a response
curl -f http://localhost:8080 || exit 1

echo "Application is running successfully."
