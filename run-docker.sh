#!/bin/bash

# Check if environment variables are set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable is not set"
    exit 1
fi

if [ -z "$LOGFIRE_TOKEN" ]; then
    echo "Error: LOGFIRE_TOKEN environment variable is not set"
    exit 1
fi

# Run the container with required environment variables
docker run -p 8000:8000 \
    -e ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} \
    -e LOGFIRE_TOKEN=${LOGFIRE_TOKEN} \
    entiendo
