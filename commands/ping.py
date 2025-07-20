import time
import platform
import discord
from discord.ext import commands

# Store the bot start time for uptime calculation
START_TIME = time.time()

async def setup_ping_command(bot):
    @bot.command(name="ping")
    async def ping_command(ctx):
        # Latency (websocket)
        latency_ms = round(bot.latency * 1000, 2)
        # Uptime
        uptime_seconds = int(time.time() - START_TIME)
        uptime_str = format_uptime(uptime_seconds)
        # System info
        python_version = platform.python_version()
        discord_version = discord.__version__
        # Guild and user stats
        guild_count = len(bot.guilds)
        user_count = sum(guild.member_count or 0 for guild in bot.guilds)

        msg = (
            f"🏓 **Pong!**\n"
            f"**Latency:** {latency_ms} ms\n"
            f"**Uptime:** {uptime_str}\n"
            f"**Servers:** {guild_count}\n"
            f"**Users:** {user_count}\n"
            f"**Python:** {python_version}\n"
            f"**discord.py:** {discord_version}"
        )
        await ctx.reply(msg)

def format_uptime(seconds):
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts) 