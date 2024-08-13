#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# check user count 서비스 파일 등록
sudo tee /etc/systemd/system/check-user-count.service > /dev/null <<EOL
[Unit]
Description=Check User Count Service
After=network.target

[Service]
Type=oneshot
User=ubuntu
ExecStartPre=/bin/chown ubuntu:ubuntu /home/ubuntu/deeplant-admin/log
ExecStart=sudo /bin/bash -c 'source /home/ubuntu/deeplant-admin/venv/bin/activate && /home/ubuntu/deeplant-admin/venv/bin/python3.10 /home/ubuntu/deeplant-admin/check-user-count.py >> /home/ubuntu/deeplant-admin/log/check-user-count.log 2>&1'
WorkingDirectory=/home/ubuntu/deeplant-admin

[Install]
WantedBy=multi-user.target
EOL

# check user count 타이머 서비스 파일 등록
sudo tee /etc/systemd/system/check-user-count.timer > /dev/null <<EOL
[Unit]
Description=Run Check User Count Service Daily

[Timer]
OnCalendar=*-*-* 12:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOL

# 서비스 파일 리로드 및 시작
sudo systemctl daemon-reload
sudo systemctl start check-user-count.timer
sudo systemctl enable check-user-count.timer

