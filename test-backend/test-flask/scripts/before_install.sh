#!/bin/bash
set -e

# Define log file
LOG_FILE="/home/ubuntu/deeplant-admin/logs/before_install.log"

{
  echo "Starting BeforeInstall phase..."

  # Update the package list and install required packages
  echo "Updating package list and installing dependencies..."
  sudo apt update -y
  sudo apt install -y python3.10 python3-pip

  # Create virtual environment directory if not exists
  echo "Setting up virtual environment..."
  if [ ! -d "/home/ubuntu/deeplant-admin/venv" ]; then
    python3 -m venv /home/ubuntu/deeplant-admin/venv
  fi

  echo "BeforeInstall phase completed."
} >> "$LOG_FILE" 2>&1 # Ensures that both standard output (1) and standard error (2) are redirected to the log file.
