#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

cd /home/ubuntu/deeplant-admin
source venv/bin/activate

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
Environment="PATH=/home/ubuntu/deeplant-admin/venv/bin"

[Install]
WantedBy=multi-user.target
EOL

# 서비스 파일 리로드 및 시작
sudo systemctl daemon-reload
sudo systemctl start flask-app
sudo systemctl enable flask-app