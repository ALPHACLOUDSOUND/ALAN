import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from YukkiMusic import app
from config import API_ID, API_HASH, BOT_TOKEN, DEFAULT_ASSISTANT_SESSION_STRING

# Images for the bot responses
IMG = [
    "https://telegra.ph/file/cefd3211a5acdcd332415.jpg",
    "https://telegra.ph/file/30d743cea510c563af6e3.jpg",
    "https://telegra.ph/file/f7ae22a1491f530c05279.jpg",
    "https://telegra.ph/file/2f1c9c98452ae9a958f7d.jpg"
]

# Welcome message
WELCOME_MESSAGE = (
    "🤖 Welcome to the Music Bot Cloner!\n\n"
    "I can host your music bot on my server within seconds.\n\n"
    "Use /clone <your-bot-token> [optional-assistant-session-string] to get started.\n"
    "If you don't provide an assistant session string, the default assistant will be used."
)

# Initialize the cloner bot
cloner_bot = Client(
    "MusicBotCloner",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@cloner_bot.on_message(filters.private & filters.command("start"))
async def start(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("Updates Channel", url="https://t.me/YourUpdatesChannel")],
        [InlineKeyboardButton("Support Group", url="https://t.me/YourSupportGroup")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_photo(
        photo=choice(IMG),
        caption=WELCOME_MESSAGE,
        reply_markup=reply_markup
    )

@cloner_bot.on_message(filters.private & filters.command("clone"))
async def clone(client: Client, message: Message):
    if len(message.command) < 2 or len(message.command) > 3:
        await message.reply("Usage: /clone <bot-token> [optional-assistant-session-string]")
        return

    bot_token = message.command[1]
    assistant_session_string = message.command[2] if len(message.command) == 3 else DEFAULT_ASSISTANT_SESSION_STRING
    text = await message.reply("Starting the cloning process...")

    try:
        # Validate bot token format (basic check)
        if not re.match(r'^\d{8,10}:[a-zA-Z0-9_-]{35}$', bot_token):
            raise ValueError("Invalid bot token format!")

        # Initialize the cloned bot client
        new_bot = Client(
            session_name=":memory:",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=bot_token,
            plugins={"root": "YukkiMusic"}
        )

        # Initialize the assistant client
        assistant_bot = Client(
            session_name="assistant",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=assistant_session_string
        )

        await new_bot.start()
        await assistant_bot.start()

        user = await new_bot.get_me()

        await text.edit(f"Your bot @{user.username} has been successfully cloned and started! ✅\n\n"
                        f"Now add your bot and the assistant to your chat.\n\nThanks for cloning!")

        # Optionally send a start command to the cloned bot
        await new_bot.send_message(user.id, "/start")

        # Stop the cloned bot and assistant to avoid session conflicts
        await new_bot.stop()
        await assistant_bot.stop()

    except Exception as e:
        await text.edit(f"**ERROR:** `{str(e)}`\nPlease try again with a valid token or session string, or press /start to begin anew.")

if __name__ == "__main__":
    cloner_bot.run()
