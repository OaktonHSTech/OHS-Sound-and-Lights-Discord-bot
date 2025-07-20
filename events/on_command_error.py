import discord
import traceback
import sys
from discord.ext import commands
import aiosqlite

def setup_on_command_error_event(bot):
    @bot.event
    async def on_command_error(ctx, error):
        embed = discord.Embed(title="Error", color=discord.Color.red())
        if isinstance(error, commands.CommandNotFound):
            return  # Silently ignore unknown commands
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = f"Missing required argument: `{error.param.name}`."
        elif isinstance(error, commands.BadArgument):
            embed.description = f"Bad argument: {str(error)}"
        elif isinstance(error, commands.MissingPermissions):
            embed.description = f"You are missing required permissions to do that."
        elif isinstance(error, commands.BotMissingPermissions):
            embed.description = f"I am missing required permissions to do that."
        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"This command is on cooldown. Please wait {error.retry_after:.2f} seconds."
        elif isinstance(error, commands.MemberNotFound):
            embed.description = f"Member not found: {error.argument}"
        elif isinstance(error, commands.ChannelNotFound):
            embed.description = f"Channel not found: {error.argument}"
        elif isinstance(error, commands.CommandInvokeError):
            orig = error.original
            if isinstance(orig, aiosqlite.Error):
                embed.description = f"Database error: {str(orig)}"
            else:
                tb = ''.join(traceback.format_exception(type(orig), orig, orig.__traceback__))
                embed.description = f"Unknown error occurred.\n```py\n{tb[:1000]}\n```"
                print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
                traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        else:
            tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
            embed.description = f"Unknown error\n```py\n{tb[:1000]}\n```"
            print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        try:
            await ctx.send(embed=embed)
        except Exception:
            pass 