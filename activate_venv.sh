#!/usr/bin/env bash
set -e

if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
  echo "Activated virtual environment from venv/bin/activate"
elif [ -f "venv/Scripts/activate" ]; then
  source venv/Scripts/activate
  echo "Activated virtual environment from venv/Scripts/activate"
else
  echo "No virtual environment directory found. Create one with: python -m venv venv"
  exit 1
fi
