#!/bin/sh

while true; do
    read -p "Have you set the necessary environment variables [y/n]?" yn
    case $yn in
        [Yy]* ) echo "Starting..."; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

# # Source the .env file to set environment variables
# set -a
# source <.ENV FILEPATH>
# set +a

# Create Docker network(s)
# docker network create <NETWORK NAME>

# Start Traefik
# Pass all command-line parameters using `$@` 
docker compose -f docker-compose.traefik.yml up --detach "$@"

# Start message queue and backend
# Pass all command-line parameters using `$@` 
docker compose -f docker-compose.messaging.yml up --detach "$@"

# Start Uvicorn
# Pass all command-line parameters using `$@`
docker compose -f docker-compose.api.yml up --detach "$@"
