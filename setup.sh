#!/bin/bash

# Quick setup script for PulseWatch

echo "Setting up PulseWatch..."

# Backend setup
echo "Setting up backend..."
cd apps/backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
cd ../..

# Frontend setup
echo "Setting up frontend..."
cd apps/frontend
npm install
cd ../..

# Copy env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "Created .env file. Please edit it with your Reddit credentials."
fi

echo "Setup complete!"
echo ""
echo "To start the application:"
echo "1. Edit .env with your Reddit credentials"
echo "2. Run: docker compose up"
echo "   Or run backend and frontend separately"

