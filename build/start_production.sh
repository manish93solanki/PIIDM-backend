#!/bin/bash
echo "Starting PIIDM Backend in production mode..."
source .venv/bin/activate
gunicorn -b 0.0.0.0:3002 -w 4 --worker-class gevent app:app --log-level info --limit-request-line 8000
