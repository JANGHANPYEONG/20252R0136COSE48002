#!/bin/bash
set -e

# Update the package list and install required packages
sudo apt update -y
sudo apt install -y python3 python3-pip

# Create virtual environment directory if not exists
if [ ! -d "/home/ubuntu/deeplant-admin/test-backend/venv" ]; then
  python3 -m venv /home/ubuntu/deeplant-admin/test-backend/venv
fi
