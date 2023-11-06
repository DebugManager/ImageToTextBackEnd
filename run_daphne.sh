#!/bin/bash

DAHPNE_CMD="daphne -b 0.0.0.0  text_to_img.asgi:application"

# Function to start Daphne
start_daphne() {
    $DAHPNE_CMD
}

# Start Daphne initially
start_daphne

# Monitor the project directory for changes and restart Daphne
watchmedo auto-restart --directory=/image_to_text/ImageToTextBackend --recursive --pattern="*.py" -- $DAHPNE_CMD