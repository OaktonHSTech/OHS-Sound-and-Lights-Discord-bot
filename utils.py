def split_message(text, max_length=1900):
    """Split a long message into multiple messages that fit Discord's 2000 character limit"""
    if len(text) <= max_length:
        return [text]
    
    messages = []
    current_message = ""
    
    # Split by lines first to avoid breaking in the middle of lines
    lines = text.split('\n')
    
    for line in lines:
        # If adding this line would exceed the limit, start a new message
        if len(current_message) + len(line) + 1 > max_length:
            if current_message:
                messages.append(current_message.strip())
                current_message = ""
            
            # If a single line is too long, split it by words
            if len(line) > max_length:
                words = line.split(' ')
                for word in words:
                    if len(current_message) + len(word) + 1 > max_length:
                        if current_message:
                            messages.append(current_message.strip())
                            current_message = ""
                    current_message += word + " "
            else:
                current_message = line + "\n"
        else:
            current_message += line + "\n"
    
    # Add the last message if there's content
    if current_message.strip():
        messages.append(current_message.strip())
    
    # If we still have a message that's too long, split it by characters
    if messages and len(messages[-1]) > max_length:
        last_message = messages.pop()
        while len(last_message) > max_length:
            messages.append(last_message[:max_length])
            last_message = last_message[max_length:]
        if last_message:
            messages.append(last_message)
    
    return messages


async def send_long_message(channel, text, max_length=1900):
    """Send a potentially long message by splitting it into multiple messages if needed"""
    messages = split_message(text, max_length)
    
    if not messages:
        return
    
    # Send the first message
    first_msg = await channel.send(messages[0])
    
    # Send additional messages if there are more
    for msg in messages[1:]:
        await channel.send(msg)
    
    return first_msg


async def reply_long_message(ctx, text, max_length=1900):
    """Reply to a context with a potentially long message by splitting it into multiple messages if needed"""
    messages = split_message(text, max_length)
    
    if not messages:
        return
    
    # Send the first message as a reply
    first_msg = await ctx.reply(messages[0])
    
    # Send additional messages if there are more
    for msg in messages[1:]:
        await ctx.channel.send(msg)
    
    return first_msg 