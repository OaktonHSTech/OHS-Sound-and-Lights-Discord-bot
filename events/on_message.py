import random
import re
from ai import build_base_instruction, ollama_generate, detect_search_directive, build_interpretation_prompt, web_search
from utils import split_message


def convert_simple_emojis(text):
    """Convert simple emoji references to full Discord emoji format"""
    emoji_mappings = {
        ":pls:": "<:pls:1396080923572961361>",
        ":metagaming:": "<:metagaming:1396089073994694658>",
        ":notlikethis:": "<:notlikethis:1396086703281672212>",
        ":concern:": "<:concern:1396099894363816058>",
        ":bigbrain:": "<:bigbrain:1396078525655683213>"
    }
    
    for simple, full in emoji_mappings.items():
        text = text.replace(simple, full)
    
    return text





def setup_on_message_event(bot, db):
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        await db.save_message(message.channel.id, message.author.id, message.content, message.author.bot)

        if message.content.lower().strip() == "uwu":
            await message.channel.send("Ditto. <a:RainbowPls:1396091046148050945>")
            return

        # Check if message mentions the bot OR is a reply to the bot OR random chance (1 in 420)
        should_respond = False
        prompt = message.content.strip()
        
        if bot.user and bot.user in message.mentions:
            should_respond = True
            prompt = message.content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()
        elif message.reference:
            try:
                replied = await message.channel.fetch_message(message.reference.message_id)
                if replied.author.id == bot.user.id:
                    should_respond = True
                    # Keep the original prompt since it's a reply to the bot
            except Exception as e:
                print(f"Warning: Failed to fetch replied message - {e}")
        elif random.random() < 1/420:  # 1 in 420 chance
            should_respond = True
            print(f"Random response triggered! (1/420 chance)")
        
        if should_respond:
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
                # First, generate initial response to detect if search is needed
                initial_reply = ollama_generate(full_prompt)
                
                if detect_search_directive(initial_reply):
                    search_query = detect_search_directive(initial_reply)
                    # Update thinking message to show searching
                    await thinking_msg.edit(content="searching... <a:cattyping:1396352060428910734>")
                    
                    # Perform the search
                    search_result = await web_search(search_query)
                    
                    # Generate final response with search results
                    interpretation_prompt = build_interpretation_prompt(
                        base_instruction, search_query, search_result, message.author.display_name, prompt
                    )
                    try:
                        reply = ollama_generate(interpretation_prompt)
                    except Exception as e:
                        reply = f"Something went wrong while interpreting the search result: {e}"
                else:
                    # No search needed, use the initial reply
                    reply = initial_reply
                
                # Clean up the reply (remove any remaining search directives)
                reply = reply.replace("[SEARCH:", "").replace("]", "")
                
                # Convert simple emoji references to full Discord emoji format
                reply = convert_simple_emojis(reply)
                
                # Split long messages into multiple messages
                messages = split_message(reply)
                
                # Send the first message by editing the thinking message
                first_message = messages[0]
                if random.random() < 0.069:
                    first_message += " <:meowsquee:1396125533061910528>"
                await thinking_msg.edit(content=first_message)
                
                # Send additional messages if there are more
                for i, msg in enumerate(messages[1:], 1):
                    if i == len(messages) - 1 and random.random() < 0.069:
                        msg += " <:meowsquee:1396125533061910528>"
                    await message.channel.send(msg)
            except Exception as e:
                await thinking_msg.edit(content=f"Error: {e}")

        await bot.process_commands(message) 