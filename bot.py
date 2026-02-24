import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat, User

# Configuration - Use Environment Variables for Security
API_ID = os.getenv("TG_API_ID")
API_HASH = os.getenv("TG_API_HASH")
# Ensure the session file is stored on Render's persistent disk path
SESSION_PATH = "/var/data/downloader_session"

client = TelegramClient(SESSION_PATH, API_ID, API_HASH)

async def download_chat_history(chat_entity, limit=None):
    """Downloads messages from a specific chat and saves to a text file."""
    chat_name = getattr(chat_entity, 'title', getattr(chat_entity, 'first_name', 'Unknown'))
    filename = f"/var/data/chats/{chat_name}_history.txt"
    
    os.makedirs("/var/data/chats", exist_ok=True)
    
    print(f"Starting download for: {chat_name}")
    with open(filename, "w", encoding="utf-8") as f:
        async for message in client.iter_messages(chat_entity, limit=limit):
            sender = await message.get_sender()
            name = getattr(sender, 'first_name', 'System')
            text = message.text or "[Media/No Text]"
            f.write(f"[{message.date}] {name}: {text}\n")
            
    print(f"Finished downloading {chat_name}")

@client.on(events.NewMessage(pattern='/download_all'))
async def handler(event):
    """Command to trigger a backup of all chats."""
    await event.respond("Starting full backup of all chats...")
    
    async for dialog in client.iter_dialogs():
        try:
            # Filters for Groups, Supergroups, and Private Chats
            await download_chat_history(dialog.entity, limit=500)
        except Exception as e:
            print(f"Could not download {dialog.name}: {e}")
            
    await event.respond("Backup complete! Files are stored on the server.")

async def main():
    await client.start()
    print("Bot is running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
