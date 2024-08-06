#!/bin/bash
cd /home/ubuntu/deeplant-admin
source venv/bin/activate
cd test-flask
exec gunicorn --bind 0.0.0.0:8080 --workers 5 \
            --access-logfile /home/ubuntu/deeplant-admin/logs/access.log \
            --error-logfile /home/ubuntu/deeplant-admin/logs/error.log \
            --log-level debug app:app