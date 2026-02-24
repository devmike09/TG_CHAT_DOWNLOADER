import os
from telethon import TelegramClient, events
from aiohttp import web

# Pull credentials from Render's hidden environment variables
API_ID = os.environ.get('API_ID')
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Initialize the bot
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Listen for someone typing "/download" in a chat the bot is in
@client.on(events.NewMessage(pattern='/download'))
async def handler(event):
    chat = await event.get_chat()
    await event.reply("Fetching recent messages... give me a moment.")
    
    # Download the last 50 messages from this specific chat
    # (Educational example: we are just printing them to the server console here)
    async for message in client.iter_messages(chat, limit=50):
        if message.text:
            print(f"Sender {message.sender_id} said: {message.text}")
            
    await event.reply("Downloaded 50 messages to the server console!")

# --- DUMMY WEB SERVER FOR RENDER ---
# Render requires a web server to bind to a port, otherwise the free tier fails.
async def handle(request):
    return web.Response(text="Bot is awake and running!")

app = web.Application()
app.router.add_get('/', handle)

async def main():
    # Start the web server
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")
    
    # Keep the bot running
    await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
