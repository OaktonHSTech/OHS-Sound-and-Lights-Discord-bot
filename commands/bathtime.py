async def setup_bathtime_command(bot, db):
    @bot.command(name="bathtime")
    async def bathtime(ctx):
        await db.clear_context(ctx.channel.id)
        await ctx.reply("<a:bathtime:1396085064122634300> I am feeling a bout of amnesia coming on.") 