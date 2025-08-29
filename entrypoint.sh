#!/bin/sh

# Short wait to allow FS/DB to be ready (optional)
sleep 2

# Apply migrations; do not init/migrate inside the container
flask db upgrade

# Start the Flask application (command provided by Dockerfile/compose)
exec "$@"
