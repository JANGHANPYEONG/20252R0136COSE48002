#! /bin/bash
cd /home/ubuntu/deeplant-admin
source venv/bin/activate

# Gunicorn 설치
pip install gunicorn

# 서비스 파일 등록
sudo tee /etc/systemd/system/flask-app.service > /dev/null <<EOL
[Unit]
Description=Flask Application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/deeplant-admin
ExecStart=/home/ubuntu/deeplant-admin/scripts/start_flask.sh
Restart=always
RestartSec=5
Environment="PATH=/home/ubuntu/Deeplant-Dev/venv/bin"

[Install]
WantedBy=multi-user.target
EOL

# 서비스 파일 리로드 및 시작
sudo systemctl daemon-reload
sudo systemctl start flask-app
sudo systemctl enable flask-app

# Flask 앱 실행
cd /home/ubuntu/deeplant-admin
source venv/bin/activate
exec gunicorn --bind 0.0.0.0:8080 --workers 5 \
            --access-logfile /home/ubuntu/deeplant-admin/log/access.log \
            --error-logfile /home/ubuntu/deeplant-admin/log/error.log \
            --log-level debug app:app
