#! /bin/bash
cd /home/ubuntu/deeplant-admin
source venv/bin/activate
exec gunicorn --bind 0.0.0.0:8080 --workers 5 \
            --access-logfile /home/ubuntu/deeplant-admin/log/access.log \
            --error-logfile /home/ubuntu/deeplant-admin/log/error.log \
            --log-level debug app:app