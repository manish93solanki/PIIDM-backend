#!/bin/bash
echo "Installing PIIDM Backend..."

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set Flask app
export FLASK_APP=app.py

# Run database migrations
flask db upgrade

echo "Installation complete!"
echo "Run './start.sh' to start the application in development mode"
echo "Run './start_production.sh' to start the application in production mode"
