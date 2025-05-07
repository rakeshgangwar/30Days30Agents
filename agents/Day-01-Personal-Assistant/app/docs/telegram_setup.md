# Setting Up the Telegram Bot Interface

This guide will help you set up the Telegram bot interface for your Personal Assistant.

## Prerequisites

- Python 3.8 or higher
- Personal Assistant dependencies installed
- A Telegram account

## Step 1: Create a Telegram Bot

1. Open Telegram and search for "BotFather" (@BotFather)
2. Start a chat with BotFather and use the `/newbot` command
3. Follow the instructions to create a new bot:
   - Provide a name for your bot (e.g., "My Personal Assistant")
   - Provide a username for your bot (must end with "bot", e.g., "my_personal_assistant_bot")
4. BotFather will give you a token for your new bot. This token is used to authenticate your bot with the Telegram API.

Example:
```
1234567890:ABCDefGhIJKlmNoPQRsTUVwxyZ
```

## Step 2: Configure Your Environment

1. Copy the token provided by BotFather
2. Add it to your `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```
3. Make sure all other required API keys are also in your `.env` file

## Step 3: Run the Telegram Bot

1. Navigate to the Personal Assistant directory
2. Run the Telegram bot:
   ```bash
   python telegram_bot.py
   ```
3. You should see a message indicating that the bot has started

## Step 4: Interact with Your Bot

1. Open Telegram and search for your bot using the username you provided
2. Start a chat with your bot
3. Use the following commands:
   - `/start` - Start the bot and get a welcome message
   - `/help` - Get help on how to use the bot
   - `/reset` - Reset your conversation history

4. Send messages to your bot just like you would in the CLI or Streamlit interface

## Troubleshooting

- **Bot not responding**: Make sure the bot is running and the token is correct
- **Error messages**: Check the console output for error details
- **API errors**: Ensure all required API keys are correctly set in your `.env` file

## Advanced Configuration

- The bot uses the same agent and tools as the CLI and Streamlit interfaces
- Each user gets their own conversation thread, identified by their Telegram user ID
- The bot uses the InterfaceAdapter to standardize input and format output

## Security Considerations

- Keep your bot token secure and never share it publicly
- The bot processes messages through your local machine, so ensure your environment is secure
- Consider implementing additional authentication if your bot handles sensitive information
