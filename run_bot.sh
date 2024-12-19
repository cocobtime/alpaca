#!/bin/bash

# Change to the script's directory
cd "$(dirname "$0")"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Run the trading bot
python3 trading_bot.py

# Deactivate virtual environment
deactivate
