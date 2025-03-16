#!/bin/bash

# Load environment variables
set -a
source .env
set +a

# Run the server on all network interfaces
python -m uvicorn app.main:app --host 0.0.0.0 --reload 