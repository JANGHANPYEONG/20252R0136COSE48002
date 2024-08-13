#!/bin/bash
source /home/ubuntu/deeplant-admin/venv/bin/activate
cd /home/ubuntu/deeplant-admin
exec gunicorn --bind 0.0.0.0:8080 --workers 5 \
            --access-logfile /home/ubuntu/deeplant-admin/log/access.log \
            --error-logfile /home/ubuntu/deeplant-admin/log/error.log \
            --log-level debug app:app
