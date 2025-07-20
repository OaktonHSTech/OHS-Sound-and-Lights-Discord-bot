async def setup_whatsit_command(bot):
    @bot.command(name="whatsit")
    async def whatsit_command(ctx):
        await ctx.reply(
            "**How to handle me correctly:**\n"
            "`!tag help` – Show tag commands help.(The helpfulness is debatable).\n"
            "`!bathtime` – Rinse off all that chat history for this channel. (Very cleansing).\n"
            "`!ping` – Play some ping pong with some stats.\n"
            "Ping me to ask questions <:pls:1396080923572961361>\n"
            "#- There *may* be an Easter egg"
        ) 