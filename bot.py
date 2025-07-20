import discord
from discord.ext import commands
import asyncio
import os
from config import DB_FILE, DISCORD_TOKEN
from db import Database
from commands.tag import setup_tag_command
from commands.bathtime import setup_bathtime_command
from commands.whatsit import setup_whatsit_command
from events.on_ready import setup_on_ready_event
from events.on_command_error import setup_on_command_error_event
from events.on_message import setup_on_message_event

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

db = Database(DB_FILE)

async def main():
    # Print configuration for debugging
    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
    model = os.getenv("MODEL", "phi3:mini")
    print(f"Bot configuration:")
    print(f"  Ollama URL: {ollama_url}")
    print(f"  Model: {model}")
    
    await db.connect()
    await setup_tag_command(bot, db)
    await setup_bathtime_command(bot, db)
    await setup_whatsit_command(bot)
    setup_on_ready_event(bot)
    setup_on_command_error_event(bot)
    setup_on_message_event(bot, db)
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main()) 