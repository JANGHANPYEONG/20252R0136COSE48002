#! /bin/bash
set -e

# Define log file
LOG_FILE="/home/ubuntu/deeplant-admin/logs/after_install.log"

{
    echo "Starting AfterInstall phase..."

    # Activate virtual environment
    echo "Activating virtual environment..."
    source /home/ubuntu/deeplant-admin/venv/bin/activate

    # Navigate to application directory
    echo "Navigating to application directory..."
    cd /home/ubuntu/deeplant-admin

    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt

    # Deactivate virtual environment
    echo "Deactivating virtual environment..."
    deactivate

    echo "AfterInstall phase completed."
} >> "$LOG_FILE" 2>&1
