import random
from ai import build_base_instruction, ollama_generate, detect_search_directive, build_interpretation_prompt, web_search


def setup_on_message_event(bot, db):
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        await db.save_message(message.channel.id, message.author.id, message.content, message.author.bot)

        if message.content.lower().strip() == "uwu":
            await message.channel.send("Ditto. <a:RainbowPls:1396091046148050945>")
            return

        if bot.user and bot.user in message.mentions:
            prompt = message.content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()
            base_instruction = build_base_instruction()

            if message.reference:
                try:
                    replied = await message.channel.fetch_message(message.reference.message_id)
                    replied_content = replied.content.strip()
                    if replied_content:
                        prompt = f"[Context: {replied_content}]\n{prompt}"
                except Exception as e:
                    print(f"Warning: Failed to fetch replied message - {e}")

            rows = await db.get_recent_context_rows(message.channel.id)
            rows = list(rows)
            rows.reverse()

            context = ""
            for user_id, msg, is_bot in rows:
                if is_bot:
                    speaker = "Bot"
                else:
                    try:
                        member = message.guild.get_member(int(user_id))
                        if not member:
                            member = await message.guild.fetch_member(int(user_id))
                        speaker = member.display_name or member.name
                    except:
                        speaker = f"User-{user_id[-4:]}"
                context += f"{speaker}: {msg}\n"

            full_prompt = f"{base_instruction}\n{context}\n{message.author.display_name}: {prompt}\nBot:"
            thinking_msg = await message.channel.send("?? Thinking... <:bigbrain:1396078525655683213>")

            try:
                reply = ollama_generate(full_prompt)
                if detect_search_directive(reply):
                    search_query = detect_search_directive(reply)
                    search_result = await web_search(search_query)
                    interpretation_prompt = build_interpretation_prompt(
                        base_instruction, search_query, search_result, message.author.display_name, prompt
                    )
                    try:
                        reply = ollama_generate(interpretation_prompt)
                    except Exception as e:
                        reply = f"Something went wrong while interpreting the search result: {e}"
                if len(reply) > 2000:
                    reply = reply[:1997] + "..."
                if random.random() < 0.069:
                    reply += " <:meowsquee:1396125533061910528>"
                await thinking_msg.edit(content=reply)
            except Exception as e:
                await thinking_msg.edit(content=f"Error: {e}")

        await bot.process_commands(message) 