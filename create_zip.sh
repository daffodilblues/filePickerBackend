#!/bin/bash

# Check if filename is provided as an argument
if [[ $# -eq 0 ]]; then
    echo "Please provide filename as argument"
    exit 1
fi

# Extract the base filename (without extension) from the provided filename
base_filename=$(basename $1 .zip)

# Navigate to site-packages directory
cd venv/lib/python3.11/site-packages

# Zip up the contents into the root of the project
zip -r9 ../../../../"$base_filename".zip .

# Navigate back to the root of the project
cd ../../../../

# Add the contents of the app folder into the zip file
zip -g "$base_filename".zip -r app

echo "Zip file created: $base_filename.zip"
