import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.models.blocks import SectionBlock, ActionsBlock, ButtonElement
import time
import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OUTPUT_PLATFORM = os.getenv('OUTPUT_PLATFORM', 'slack').lower()
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
TEAM_MEMBER_IDS = [int(id) for id in os.getenv('TEAM_MEMBER_IDS', '').split(',') if id]
UNANSWERED_THRESHOLD = 3600  # 1 hour in seconds

# Initialize clients
slack_client = WebClient(token=SLACK_BOT_TOKEN) if OUTPUT_PLATFORM == 'slack' else None

messages = {}
output_messages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Bot started. Monitoring messages for unanswered ones.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    chat = message.chat

    if user.id in TEAM_MEMBER_IDS:
        handle_team_member_message(chat.id, message)
    elif not message.reply_to_message:
        add_message_to_queue(message, user, chat)

def handle_team_member_message(chat_id, message):
    if message.reply_to_message:
        original_msg_id = message.reply_to_message.message_id
        if original_msg_id in messages:
            messages[original_msg_id]['answered'] = True
            print(f"Message {original_msg_id} marked as answered by team member")
            if original_msg_id in output_messages:
                delete_output_message(output_messages[original_msg_id])
                del output_messages[original_msg_id]

def add_message_to_queue(message, user, chat):
    message_link = f"https://t.me/c/{str(chat.id)[4:]}/{message.message_id}"
    messages[message.message_id] = {
        'text': message.text,
        'user_name': user.first_name,
        'chat_id': chat.id,
        'chat_title': chat.title,
        'timestamp': time.time(),
        'answered': False,
        'message_link': message_link
    }
    print(f"Added partner message to queue: {messages[message.message_id]}")

async def check_unanswered_messages(context: ContextTypes.DEFAULT_TYPE):
    current_time = time.time()
    print(f"Checking for unanswered messages. Count: {len(messages)}")
    for msg_id, msg_data in list(messages.items()):
        if not msg_data['answered'] and (current_time - msg_data['timestamp']) > UNANSWERED_THRESHOLD:
            handle_unanswered_message(msg_id, msg_data)
    print("Check complete.")

def handle_unanswered_message(msg_id, msg_data):
    print(f"Unanswered partner message found: {msg_data['text']}")
    output_id = notify_output(msg_data['text'], msg_data['chat_title'], msg_data['user_name'], msg_data['message_link'])
    if output_id:
        output_messages[msg_id] = output_id
        print(f"Message sent to {OUTPUT_PLATFORM} with ID: {output_id}")
        del messages[msg_id]
    else:
        print(f"Failed to send message to {OUTPUT_PLATFORM}")

# The rest of the functions (notify_output, notify_slack, notify_discord, delete_output_message, delete_slack_message) remain unchanged

def main():
    print("Starting the bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.job_queue.run_repeating(check_unanswered_messages, interval=600)  # Check every 10 minutes

    print(f"Bot is running with {OUTPUT_PLATFORM.capitalize()} integration. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
