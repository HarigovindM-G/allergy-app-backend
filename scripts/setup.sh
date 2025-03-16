#!/bin/bash

# Load environment variables
set -a
source ../.env
set +a

# Install dependencies
pip install -r ../requirements.txt

# Initialize the database
python init_db.py

echo "Setup complete!" 