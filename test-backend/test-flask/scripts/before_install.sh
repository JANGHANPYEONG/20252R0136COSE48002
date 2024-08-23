#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive

# Update the package list and install required packages
sudo apt update -y

# Create virtual environment directory if not exists
if [ ! -d "/home/ubuntu/deeplant-admin/venv" ]; then
  python3 -m venv /home/ubuntu/deeplant-admin/venv
fi