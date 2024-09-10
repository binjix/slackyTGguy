import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.models.blocks import SectionBlock, ActionsBlock, ButtonElement
import time
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')

slack_client = WebClient(token=SLACK_BOT_TOKEN)

messages = {}
slack_messages = {}
TEAM_MEMBER_IDS = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running and monitoring this group.")
    print(f"Start command received in chat {update.effective_chat.id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.chat.type in ['group', 'supergroup']:
        if message.reply_to_message:
            original_msg_id = message.reply_to_message.message_id
            if original_msg_id in messages:
                if message.from_user.id in TEAM_MEMBER_IDS or not TEAM_MEMBER_IDS:
                    messages[original_msg_id]['answered'] = True
                    print(f"Message {original_msg_id} marked as answered")
                    if original_msg_id in slack_messages:
                        delete_slack_message(slack_messages[original_msg_id])
                        del slack_messages[original_msg_id]
        else:
            messages[message.message_id] = {
                'timestamp': time.time(),
                'text': message.text,
                'answered': False,
                'chat_id': message.chat_id,
                'chat_title': message.chat.title,
                'user_name': message.from_user.full_name,
                'message_link': f"https://t.me/c/{str(message.chat_id)[4:]}/{message.message_id}"
            }
            print(f"New message received in {message.chat.title}: {message.text}")

async def check_unanswered_messages(context: ContextTypes.DEFAULT_TYPE):
    current_time = time.time()
    print(f"Checking for unanswered messages. Current message count: {len(messages)}")
    for msg_id, msg_data in list(messages.items()):
        if not msg_data['answered'] and (current_time - msg_data['timestamp']) > 30:
            print(f"Unanswered message found: {msg_data['text']}")
            slack_ts = notify_slack(msg_data['text'], msg_data['chat_title'], msg_data['user_name'], msg_data['message_link'])
            if slack_ts:
                slack_messages[msg_id] = slack_ts
            del messages[msg_id]
    print("Check complete.")

def notify_slack(message_text, chat_title, user_name, message_link):
    try:
        blocks = [
            SectionBlock(
                text=f"*{chat_title}:* | *From:* {user_name}\n*Message:* {message_text}"
            ),
            ActionsBlock(
                elements=[
                    ButtonElement(
                        text="View in Telegram",
                        url=message_link,
                        style="primary"
                    )
                ]
            )
        ]
        
        response = slack_client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            blocks=blocks,
            text=f"Unanswered message in Telegram group '{chat_title}' from {user_name}"
        )
        print(f"Notification sent to Slack for message: {message_text}")
        return response['ts']
    except SlackApiError as e:
        print(f"Error posting message to Slack: {e}")
        return None

def delete_slack_message(timestamp):
    try:
        response = slack_client.chat_delete(
            channel=SLACK_CHANNEL_ID,
            ts=timestamp
        )
        print(f"Deleted Slack message with timestamp: {timestamp}")
    except SlackApiError as e:
        print(f"Error deleting Slack message: {e}")

def main():
    print("Starting the bot...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.job_queue.run_repeating(check_unanswered_messages, interval=10)

    print("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
