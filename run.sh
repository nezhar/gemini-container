#!/bin/bash
set -e

# Build the docker images
docker compose build

# Run the services
docker compose run --rm gemini-cli "$@"
