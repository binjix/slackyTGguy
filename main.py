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
TEAM_MEMBER_IDS = []  # Add team member IDs here
UNANSWERED_THRESHOLD = 10  # seconds

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
        handle_team_member_message(chat.id)
    else:
        add_message_to_queue(message, user, chat)

def handle_team_member_message(chat_id):
    for msg_id, msg_data in list(messages.items()):
        if msg_data['chat_id'] == chat_id and not msg_data['answered']:
            msg_data['answered'] = True
            if msg_id in output_messages:
                delete_output_message(output_messages[msg_id])
                del output_messages[msg_id]

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
    print(f"Added message to queue: {messages[message.message_id]}")

async def check_unanswered_messages(context: ContextTypes.DEFAULT_TYPE):
    current_time = time.time()
    print(f"Checking for unanswered messages. Count: {len(messages)}")
    for msg_id, msg_data in list(messages.items()):
        if not msg_data['answered'] and (current_time - msg_data['timestamp']) > UNANSWERED_THRESHOLD:
            handle_unanswered_message(msg_id, msg_data)
    print("Check complete.")

def handle_unanswered_message(msg_id, msg_data):
    print(f"Unanswered message found: {msg_data['text']}")
    output_id = notify_output(msg_data['text'], msg_data['chat_title'], msg_data['user_name'], msg_data['message_link'])
    if output_id:
        output_messages[msg_id] = output_id
        print(f"Message sent to {OUTPUT_PLATFORM} with ID: {output_id}")
        msg_data['answered'] = True
        del messages[msg_id]
    else:
        print(f"Failed to send message to {OUTPUT_PLATFORM}")

def notify_output(message_text, chat_title, user_name, message_link):
    if OUTPUT_PLATFORM == 'slack':
        return notify_slack(message_text, chat_title, user_name, message_link)
    elif OUTPUT_PLATFORM == 'discord':
        return notify_discord(message_text, chat_title, user_name, message_link)
    else:
        print(f"Unsupported output platform: {OUTPUT_PLATFORM}")
        return None

def notify_slack(message_text, chat_title, user_name, message_link):
    try:
        blocks = [
            SectionBlock(text=f"New message in {chat_title}"),
            SectionBlock(text=f"From: {user_name}\nMessage: {message_text}"),
            ActionsBlock(elements=[
                ButtonElement(text="View in Telegram", url=message_link, action_id="view_telegram")
            ])
        ]
        response = slack_client.chat_postMessage(channel=SLACK_CHANNEL_ID, blocks=blocks)
        print(f"Notification sent to Slack for message: {message_text}")
        return response['ts']
    except SlackApiError as e:
        print(f"Error posting message to Slack: {e}")
        return None

def notify_discord(message_text, chat_title, user_name, message_link):
    print(f"Attempting to send message to Discord: {message_text}")
    embed = {
        "title": f"New message in {chat_title}",
        "description": f"**From:** {user_name}\n**Message:** {message_text}",
        "color": 3447003,
        "fields": [{"name": "View in Telegram", "value": f"[Click here]({message_link})"}]
    }
    payload = {"embeds": [embed]}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, verify=True)
        if response.status_code == 204:
            print(f"Notification sent to Discord for message: {message_text}")
            return int(time.time() * 1000)
        else:
            print(f"Error posting to Discord. Status: {response.status_code}")
            print(f"Response body: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Network error when sending to Discord: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error when sending to Discord: {e}")
        return None

def delete_output_message(message_id):
    if OUTPUT_PLATFORM == 'slack':
        delete_slack_message(message_id)
    elif OUTPUT_PLATFORM == 'discord':
        print(f"Cannot delete Discord webhook message with ID: {message_id}")
    else:
        print(f"Unsupported output platform: {OUTPUT_PLATFORM}")

def delete_slack_message(message_id):
    try:
        slack_client.chat_delete(channel=SLACK_CHANNEL_ID, ts=message_id)
        print(f"Deleted Slack message with ID: {message_id}")
    except SlackApiError as e:
        print(f"Error deleting Slack message: {e}")

def main():
    print("Starting the bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.job_queue.run_repeating(check_unanswered_messages, interval=10)

    print(f"Bot is running with {OUTPUT_PLATFORM.capitalize()} integration. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()