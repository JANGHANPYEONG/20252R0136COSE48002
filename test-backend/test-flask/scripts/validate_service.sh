#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive

# Send a request to the application and check for a response
curl -f http://localhost:8080 || exit 1

echo "Application is running successfully."



# Health check 수행 -> 구현 예정
# response=$(curl -sS -o /dev/null -w "%{http_code}" $HEALTH_CHECK_URL)

# if [ $response = "200" ]; then
#     echo "New version is healthy"
#     exit 0
# else
#     echo "Health check failed. HTTP response: $response"
#     exit 1
# fi