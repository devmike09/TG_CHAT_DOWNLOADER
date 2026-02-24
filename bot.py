import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# We will store messages in the server's memory temporarily.
# Note: If Render restarts the server, this memory clears. 
chat_logs = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to the /start command."""
    await update.message.reply_text(
        "Hello! I'm a Chat Logger Bot. 🤖\n\n"
        "Add me to a group, or message me directly. I will record new messages from now on. "
        "When you are ready, type /export to download the chat log as a text file."
    )

async def log_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Listens to all text messages and saves them."""
    # Ignore messages that don't have text (like photos or stickers)
    if not update.message or not update.message.text:
        return 

    chat_id = update.message.chat_id
    # Get the user's name or username
    user = update.message.from_user.username or update.message.from_user.first_name
    text = update.message.text

    # If this is a new chat, create a blank list for it
    if chat_id not in chat_logs:
        chat_logs[chat_id] = []

    # Add the message to the list
    chat_logs[chat_id].append(f"{user}: {text}\n")

async def export_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to /export by sending the text file."""
    chat_id = update.message.chat_id

    if chat_id not in chat_logs or len(chat_logs[chat_id]) == 0:
        await update.message.reply_text("I don't have any messages logged for this chat yet.")
        return

    # 1. Create a temporary text file
    filename = f"chat_log_{chat_id}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(chat_logs[chat_id])

    # 2. Send the file back to the Telegram chat
    with open(filename, "rb") as file:
        await update.message.reply_document(document=file, filename="chat_log.txt")

    # 3. Clean up: Delete the file from the server and clear memory
    os.remove(filename)
    chat_logs[chat_id] = []
    await update.message.reply_text("Log exported successfully! My memory for this chat has been cleared.")

def main():
    # Fetch environment variables provided by Render
    TOKEN = os.environ.get("BOT_TOKEN")
    # Render automatically provides this URL so your bot knows where it lives!
    APP_NAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME") 
    PORT = int(os.environ.get("PORT", "10000"))

    if not TOKEN:
        print("ERROR: Please set the BOT_TOKEN environment variable.")
        return

    # Build the bot application
    app = Application.builder().token(TOKEN).build()

    # Tell the bot what to do with specific commands/messages
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("export", export_chat))
    # Log all text messages that are NOT commands
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, log_message))

    # Deployment logic: Use Webhooks for Render, Polling for local testing
    if APP_NAME:
        webhook_url = f"https://{APP_NAME}/"
        print(f"Starting bot using Webhook on: {webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=webhook_url
        )
    else:
        print("Starting bot locally using Polling...")
        app.run_polling()

if __name__ == "__main__":
    main()
