from discord.ext import commands
from typing import Optional
from utils import reply_long_message

async def setup_tag_command(bot, db):
    @bot.command(name="tag")
    async def tag(ctx, subcommand: Optional[str] = None, name: Optional[str] = None, *, content: Optional[str] = None):
        if subcommand is None or subcommand.lower() == "help":
            return await ctx.reply(
                "**Tag Help**\n"
                "`!tag add <name> <content>` – Add a new tag\n"
                "`!tag edit <name> <new content>` – Edit a tag. (Ship of Theseus).\n"
                "`!tag remove <name>` – Delete a tag\n"
                "`!tag rename <deadname> <new name>` – Change the tags name, something more... *representative*.\n"
                "`!tag list` – List all tags I bother to look for.\n"
                "`!tag <name>` – Prints a tag on a good day.\n"
                "`!tag help` – Show this message <:metagaming:1396089073994694658>"
            )

        subcommand = subcommand.lower()

        if subcommand == "add":
            if not name or not content:
                return await ctx.reply("Usage: `!tag add <name> <content>`. *ring ring ring* Oh the IRS is calling to congratulate you. You survived another day of life. <:LazGhost:1385160995605053491>")
            if await db.get_tag(name):
                return await ctx.reply(f"Tag `{name}` already exists. Unlike the developer's sleep schedule... <:metagaming:1396089073994694658>")
            await db.add_tag(name, content)
            await ctx.reply(f"Tag `{name}` added. Eventually this list will be as big as your mother (not really).")
        elif subcommand == "edit":
            if not name or not content:
                return await ctx.reply("Usage: `!tag edit <name> <new content>`. *Now with 56% less baking powder!*")
            if not await db.get_tag(name):
                return await ctx.reply(f"Tag `{name}` not found. Don't look at me, you are the people who add them. <:metagaming:1396089073994694658>")
            await db.edit_tag(name, content)
            await ctx.reply(f"***So, it has come to this***: tag `{name}` has been... ||changed!||")

        elif subcommand == "remove":
            if not name:
                return await ctx.reply("Usage: `!tag remove <name>`\nYou forgot the name bit. <:notlikethis:1396086703281672212>")
            if not await db.get_tag(name):
                return await ctx.reply(f"Tag `{name}` not found. How about you find it smart guy. <:metagaming:1396089073994694658>")
            await db.delete_tag(name)
            await ctx.reply(f"Tag `{name}` just got *owned*... actually more like unowned. <:notlikethis:1396086703281672212>")

        elif subcommand == "rename":
            if not name and not content:
                original_nick = ctx.author.display_name
                new_nick = f"Margie({original_nick})"
                if len(new_nick) > 32:
                    new_nick = "Margie"
                await ctx.author.edit(nick=new_nick)
                return await ctx.reply("Usage: `!tag rename <oldname> <newname>`.\nUnless, do you want me to call you Margie? Congratulations on your new name!")

            if not name:
                return await ctx.reply("Missing the original name! Did you know I got vaccinated for SQL injection at birth?")

            if not content:
                return await ctx.reply("Missing the new name! Are you ok, do you want to talk?? <:concern:1396099894363816058>")

            success, msg = await db.rename_tag(name, content)
            await ctx.reply(msg)
            
        elif subcommand == "list":
            tags = await db.list_tags()
            if not tags:
                return await ctx.reply("No tags available smh. <:notlikethis:1396086703281672212>")
            tag_list = f"These are some of the ones I found: {', '.join(tags)}\n#- I even checked under the couch cushions for you"
            await reply_long_message(ctx, tag_list)

        else:
            tag_content = await db.get_tag(subcommand)
            if tag_content:
                await reply_long_message(ctx, tag_content)
            else:
                await ctx.reply(f"I don't remember if tag `{subcommand}` is a thing, probably not.") 