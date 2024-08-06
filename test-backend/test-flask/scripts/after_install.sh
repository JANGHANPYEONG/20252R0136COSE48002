#!/bin/bash
set -e

# Activate virtual environment
source /home/ubuntu/deeplant-admin/test-backend/venv

# Navigate to application directory
cd /home/ubuntu/deeplant-admin/test-backend/test-flask

# Install dependencies
pip install -r requirements.txt

# Deactivate virtual environment
deactivate
