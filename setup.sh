#!/bin/bash

python3 -m venv snnif

source snnif/bin/activate

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Please ensure it exists in the current directory."
fi