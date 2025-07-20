#!/bin/bash

# SALbot Docker Restart Scheduler
# Restarts the Docker containers every 8 hours

echo "Starting SALbot restart scheduler..."
echo "Will restart containers every 8 hours"
echo "Press Ctrl+C to stop"

# Function to restart containers
restart_containers() {
    echo "$(date): Restarting SALbot containers..."
    cd "$(dirname "$0")"  # Change to script directory
    docker-compose restart
    echo "$(date): Restart completed"
}

# Initial restart
restart_containers

# Loop every 8 hours (28800 seconds)
while true; do
    echo "$(date): Sleeping for 8 hours..."
    sleep 28800  # 8 hours in seconds
    restart_containers
done 