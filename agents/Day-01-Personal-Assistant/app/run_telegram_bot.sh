#!/bin/bash

# Run the Telegram bot for the Personal Assistant

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Check if python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    exit 1
fi

# Check if the .env file exists
if [ ! -f .env ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env file. Please edit it to add your API keys."
        exit 1
    else
        echo "Error: .env.example file not found. Cannot create .env file."
        exit 1
    fi
fi

# Check if TELEGRAM_BOT_TOKEN is set in .env
if ! grep -q "TELEGRAM_BOT_TOKEN=" .env || grep -q "TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here" .env; then
    echo "Error: TELEGRAM_BOT_TOKEN is not set in .env file."
    echo "Please edit the .env file and add your Telegram bot token."
    exit 1
fi

# Run the bot
echo "Starting Telegram bot..."
python3 telegram_bot.py
