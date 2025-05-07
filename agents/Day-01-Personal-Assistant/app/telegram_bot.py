#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram interface for the Personal Assistant.

This module provides a Telegram bot interface for interacting
with the Personal Assistant agent.
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Import from the app package
from agent import create_agent
from langgraph_memory import LangGraphMemory
from interface_adapter import InterfaceAdapter
from config import init_user_preferences

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Global variables
interface_adapter = InterfaceAdapter()
agent_executors = {}  # Maps user_id to agent_executor


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! I'm your Personal Assistant bot.\n\n"
        "I can help with:\n"
        "- Weather information\n"
        "- Setting reminders and tasks\n"
        "- Answering general knowledge questions\n"
        "- Finding recent news\n"
        "- Searching the web for current information\n\n"
        "Just send me a message with your request!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Here's how to use me:\n\n"
        "Just type your question or request, and I'll do my best to help.\n\n"
        "Examples:\n"
        "- What's the weather like in New York?\n"
        "- Remind me to call mom tomorrow at 5pm\n"
        "- Tell me about quantum computing\n"
        "- What's the latest news in technology?\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/reset - Reset your conversation history"
    )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset the conversation when the command /reset is issued."""
    user_id = str(update.effective_user.id)
    
    # Create a new agent executor for this user
    thread_id = f"telegram_{user_id}"
    agent_executors[user_id] = create_agent(
        verbose=False,
        use_langgraph_memory=True,
        thread_id=thread_id
    )
    
    await update.message.reply_text(
        "I've reset our conversation. What would you like to talk about?"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages."""
    user_id = str(update.effective_user.id)
    message_text = update.message.text
    
    # Send typing action to show the bot is processing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    try:
        # Get or create agent executor for this user
        if user_id not in agent_executors:
            thread_id = f"telegram_{user_id}"
            agent_executors[user_id] = create_agent(
                verbose=False,
                use_langgraph_memory=True,
                thread_id=thread_id
            )
        
        # Prepare input for the agent using the interface adapter
        raw_input = {
            "message": {
                "text": message_text,
                "from": {
                    "id": user_id,
                    "username": update.effective_user.username
                }
            }
        }
        
        standardized_input = interface_adapter.standardize_input(
            raw_input,
            "telegram"
        )
        
        # Process the message with the agent
        # Run in a separate thread to avoid blocking
        agent_response = await asyncio.to_thread(
            agent_executors[user_id].run,
            input=standardized_input["message"]
        )
        
        # Format the response for Telegram
        formatted_response = interface_adapter.format_output(
            {"text": agent_response},
            "telegram"
        )
        
        # Send the response
        await update.message.reply_text(
            formatted_response["text"],
            parse_mode=formatted_response.get("parse_mode", None)
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "I'm sorry, I encountered an error while processing your request. "
            f"Error details: {str(e)}"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Send a message to the user
    if update and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, something went wrong. Please try again later."
        )


def main() -> None:
    """Start the bot."""
    # Load environment variables
    load_dotenv()
    
    # Check for Telegram bot token
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not telegram_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        print("Please add it to your .env file or set it as an environment variable.")
        sys.exit(1)
    
    # Initialize user preferences
    init_user_preferences()
    
    # Create the application
    application = Application.builder().token(telegram_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    print("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
