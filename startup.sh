#!/bin/bash

# Add the Debian stable main repository to the sources list
echo "deb http://ftp.debian.org/debian stable main" | tee -a /etc/apt/sources.list

# Update the package list
apt-get update

# Upgrade SQLite3
apt-get install -y sqlite3

# Activate custom venv (on Linux)
# source venv/bin/activate

# Start Gunicorn server with the specified settings
gunicorn --bind 0.0.0.0 --worker-class aiohttp.worker.GunicornWebWorker --timeout 600 app:app