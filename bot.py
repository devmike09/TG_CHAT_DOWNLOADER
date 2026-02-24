import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat, User

# Configuration - Use Environment Variables for Security
API_ID = os.getenv("TG_API_ID")
API_HASH = os.getenv("TG_API_HASH")

# Check if we are on Render (which uses /var/data) or local
if os.path.exists("/var/data"):
    SESSION_PATH = "/var/data/downloader_session"
    CHATS_DIR = "/var/data/chats"
else:
    SESSION_PATH = "downloader_session"
    CHATS_DIR = "chats"

client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

async def download_chat_history(chat_entity, limit=None):
    """Downloads messages from a specific chat and saves to a text file."""
    chat_name = getattr(chat_entity, 'title', getattr(chat_entity, 'first_name', 'Unknown'))
    
    # Ensure the directory exists
    os.makedirs(CHATS_DIR, exist_ok=True)
    filename = os.path.join(CHATS_DIR, f"{chat_name}_history.txt")
    
    print(f"Starting download for: {chat_name}")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            async for message in client.iter_messages(chat_entity, limit=limit):
                sender = await message.get_sender()
                name = getattr(sender, 'first_name', 'System')
                text = message.text or "[Media/No Text]"
                f.write(f"[{message.date}] {name}: {text}\n")
        print(f"Finished downloading {chat_name}")
    except Exception as e:
        print(f"Error saving {chat_name}: {e}")

@client.on(events.NewMessage(pattern='/download_all'))
async def handler(event):
    """Command to trigger a backup of all chats."""
    await event.respond("Starting full backup of all chats...")
    
    async for dialog in client.iter_dialogs():
        try:
            # Limits to 500 messages per chat to avoid being banned
            await download_chat_history(dialog.entity, limit=500)
            await asyncio.sleep(1) # Small delay to be safe
        except Exception as e:
            print(f"Could not download {dialog.name}: {e}")
            
    await event.respond("Backup complete! Files are stored on the server.")

async def main():
    await client.start()
    print("Bot is running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Ensure the loop runs correctly in all environments
    try:
        asyncio.run(main())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
