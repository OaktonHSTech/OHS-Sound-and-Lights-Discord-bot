def setup_on_ready_event(bot):
    @bot.event
    async def on_ready():
        if bot.user is not None:
            print(f"Logged in as {bot.user} (ID: {bot.user.id})")
        else:
            print("Bot user is None in on_ready()") 