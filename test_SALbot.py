import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import sqlite3
import json

# === Bot logic functions to test ===
# We'll recreate minimal parts here to keep tests self-contained.
# In real life, import these from your bot module.

DB_FILE = ":memory:"
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:1b"
MAX_CONTEXT_MESSAGES = 69

class BotDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()
        self.c.execute("CREATE TABLE IF NOT EXISTS tags (name TEXT PRIMARY KEY, content TEXT)")
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,
                user_id TEXT,
                message TEXT,
                is_bot BOOLEAN,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    # Tag DB methods
    def get_tag(self, name):
        self.c.execute("SELECT content FROM tags WHERE name = ?", (name,))
        row = self.c.fetchone()
        return row[0] if row else None

    def add_tag(self, name, content):
        self.c.execute("INSERT INTO tags (name, content) VALUES (?, ?)", (name, content))
        self.conn.commit()

    def edit_tag(self, name, content):
        self.c.execute("UPDATE tags SET content = ? WHERE name = ?", (content, name))
        self.conn.commit()

    def delete_tag(self, name):
        self.c.execute("DELETE FROM tags WHERE name = ?", (name,))
        self.conn.commit()

    def list_tags(self):
        self.c.execute("SELECT name FROM tags")
        return [row[0] for row in self.c.fetchall()]

    # Conversation DB methods
    def save_message(self, channel_id, user_id, message, is_bot):
        self.c.execute(
            "INSERT INTO conversations (channel_id, user_id, message, is_bot) VALUES (?, ?, ?, ?)",
            (str(channel_id), str(user_id), message, is_bot)
        )
        self.conn.commit()

        self.c.execute("SELECT COUNT(*) FROM conversations WHERE channel_id = ?", (str(channel_id),))
        count = self.c.fetchone()[0]
        if count > MAX_CONTEXT_MESSAGES:
            to_delete = count - MAX_CONTEXT_MESSAGES
            self.c.execute(
                "DELETE FROM conversations WHERE id IN (SELECT id FROM conversations WHERE channel_id = ? ORDER BY created_at ASC LIMIT ?)",
                (str(channel_id), to_delete)
            )
            self.conn.commit()

    def get_recent_context(self, channel_id, limit=MAX_CONTEXT_MESSAGES):
        self.c.execute(
            "SELECT user_id, message, is_bot FROM conversations WHERE channel_id = ? ORDER BY created_at DESC LIMIT ?",
            (str(channel_id), limit)
        )
        rows = self.c.fetchall()
        rows.reverse()
        context = ""
        for user_id, msg, is_bot in rows:
            speaker = "Bot" if is_bot else "User"
            context += f"{speaker}: {msg}\n"
        return context.strip()

    def clear_context(self, channel_id):
        self.c.execute("DELETE FROM conversations WHERE channel_id = ?", (str(channel_id),))
        self.conn.commit()

# A simplified mocked Bot class to simulate commands and on_message handling
class MockBot:
    def __init__(self):
        self.db = BotDB()
        self.user = MagicMock()
        self.user.id = 123456789
        self.commands = {}
        self.process_commands = AsyncMock()

    def command(self, name=None):
        def decorator(func):
            self.commands[name or func.__name__] = func
            return func
        return decorator

    async def invoke_command(self, name, ctx, *args, **kwargs):
        if name in self.commands:
            return await self.commands[name](ctx, *args, **kwargs)
        else:
            raise ValueError(f"Command {name} not found")

# Mock Context and Message for Discord
class MockContext:
    def __init__(self):
        self.replies = []
    async def reply(self, content):
        self.replies.append(content)

class MockMessage:
    def __init__(self, content, author_bot=False, mentions=None, reference=None, channel=None):
        self.content = content
        self.author = MagicMock()
        self.author.bot = author_bot
        self.mentions = mentions or []
        self.reference = reference
        self.channel = channel or self
        self.id = 42
        self.replies = []

    async def reply(self, content):
        self.replies.append(content)

    async def channel_send(self, content):
        self.replies.append(content)
        return self

    # Simulate fetching a message for reply reference
    async def fetch_message(self, message_id):
        return MockMessage("Previous message content")

class TestDiscordBot(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.bot = MockBot()
        self.db = self.bot.db

        # Setup commands as per the real bot commands
        @self.bot.command(name="tag")
        async def tag_cmd(ctx, subcommand=None, name=None, *, content=None):
            # ... simplified command handler using self.db ...
            if subcommand is None or subcommand.lower() == "help":
                await ctx.reply("Help message")
                return
            sub = subcommand.lower()
            if sub == "add":
                if not name or not content:
                    await ctx.reply("❌ Usage: !tag add <name> <content>")
                    return
                if self.db.get_tag(name):
                    await ctx.reply(f"⚠️ Tag `{name}` already exists.")
                    return
                self.db.add_tag(name, content)
                await ctx.reply(f"✅ Tag `{name}` added.")
            elif sub == "edit":
                if not name or not content:
                    await ctx.reply("❌ Usage: !tag edit <name> <new content>")
                    return
                if not self.db.get_tag(name):
                    await ctx.reply(f"❌ Tag `{name}` not found.")
                    return
                self.db.edit_tag(name, content)
                await ctx.reply(f"✏️ Tag `{name}` updated.")
            elif sub == "remove":
                if not name:
                    await ctx.reply("❌ Usage: !tag remove <name>")
                    return
                if not self.db.get_tag(name):
                    await ctx.reply(f"❌ Tag `{name}` not found.")
                    return
                self.db.delete_tag(name)
                await ctx.reply(f"??️ Tag `{name}` removed.")
            elif sub == "list":
                tags = self.db.list_tags()
                if not tags:
                    await ctx.reply("No tags available.")
                else:
                    await ctx.reply(f"Tags: {', '.join(tags)}")
            else:
                # treat as tag name
                content = self.db.get_tag(subcommand)
                if content:
                    await ctx.reply(content)
                else:
                    await ctx.reply(f"❌ Tag `{subcommand}` not found.")

        # Setup !bathtime and !help commands for testing
        @self.bot.command(name="bathtime")
        async def bathtime_cmd(ctx):
            # Clear chat history (simulate)
            self.db.clear_context("testchannel")
            await ctx.reply("?? Bathtime! Context cleared.")

        @self.bot.command(name="help")
        async def help_cmd(ctx):
            await ctx.reply("Help: !tag, !bathtime, !help")

    async def test_tag_add_and_get(self):
        ctx = MockContext()
        await self.bot.invoke_command("tag", ctx, "add", "foo", content="bar")
        self.assertIn("✅ Tag `foo` added.", ctx.replies)
        self.assertEqual(self.db.get_tag("foo"), "bar")

    async def test_tag_edit(self):
        self.db.add_tag("foo", "bar")
        ctx = MockContext()
        await self.bot.invoke_command("tag", ctx, "edit", "foo", content="baz")
        self.assertIn("✏️ Tag `foo` updated.", ctx.replies)
        self.assertEqual(self.db.get_tag("foo"), "baz")

    async def test_tag_remove(self):
        self.db.add_tag("foo", "bar")
        ctx = MockContext()
        await self.bot.invoke_command("tag", ctx, "remove", "foo")
        self.assertIn("??️ Tag `foo` removed.", ctx.replies)
        self.assertIsNone(self.db.get_tag("foo"))

    async def test_tag_list_and_fetch(self):
        self.db.add_tag("foo", "bar")
        self.db.add_tag("baz", "qux")
        ctx = MockContext()
        await self.bot.invoke_command("tag", ctx, "list")
        self.assertTrue(any("foo" in reply and "baz" in reply for reply in ctx.replies))
        ctx2 = MockContext()
        await self.bot.invoke_command("tag", ctx2, "foo")
        self.assertIn("bar", ctx2.replies)

    async def test_tag_help(self):
        ctx = MockContext()
        await self.bot.invoke_command("tag", ctx, "help")
        self.assertTrue(any("Help" in reply for reply in ctx.replies))

    async def test_bathtime_clears_context(self):
        # Add some conversation history first
        self.db.save_message("testchannel", "user1", "Hello", False)
        self.db.save_message("testchannel", "bot", "Hi!", True)
        ctx = MockContext()
        await self.bot.invoke_command("bathtime", ctx)
        self.assertIn("?? Bathtime! Context cleared.", ctx.replies)
        # Context should be empty after
        context = self.db.get_recent_context("testchannel")
        self.assertEqual(context, "")

    async def test_help_lists_commands(self):
        ctx = MockContext()
        await self.bot.invoke_command("help", ctx)
        self.assertIn("!tag", ctx.replies[0])
        self.assertIn("!bathtime", ctx.replies[0])
        self.assertIn("!help", ctx.replies[0])

    @patch("requests.post")
    async def test_ollama_mention_response(self, mock_post):
        # Simulate a Discord message mentioning bot
        mock_message = MockMessage(f"<@!{self.bot.user.id}> Hello bot!", author_bot=False, mentions=[self.bot.user])
        mock_message.channel.send = AsyncMock(return_value=mock_message)  # For thinking message

        # Mock the HTTP post to Ollama API to return streaming JSON lines
        def generate_stream():
            # Simulate streaming JSON response line by line
            yield json.dumps({"response": "Hi there!"}).encode("utf-8")
            yield b""
        mock_post.return_value.iter_lines = generate_stream

        # Patch bot.process_commands to just pass
        self.bot.process_commands = AsyncMock()

        # Define the event handler roughly like your bot's on_message
        async def on_message(message):
            if message.author.bot:
                return
            if self.bot.user in message.mentions:
                prompt = message.content.replace(f"<@!{self.bot.user.id}>", "").strip()
                thinking_msg = await message.channel.send("?? Thinking...")

                try:
                    response = mock_post(f"{OLLAMA_URL}/api/generate", json={"model": MODEL, "prompt": prompt}, stream=True)
                    reply_parts = []
                    for line in response.iter_lines():
                        if not line:
                            continue
                        data = json.loads(line.decode("utf-8"))
                        if "response" in data:
                            reply_parts.append(data["response"])
                    reply = "".join(reply_parts).strip()
                    await thinking_msg.reply(reply)
                except Exception as e:
                    await thinking_msg.reply(f"⚠️ Error talking to LLM: {e}")

            await self.bot.process_commands(message)

        await on_message(mock_message)

        # The bot should reply with the mocked response
        self.assertIn("Hi there!", mock_message.replies)

    async def test_context_pruning(self):
        channel = "chan-prune"
        # Add 80 messages, should prune to 69
        for i in range(80):
            self.db.save_message(channel, f"user{i}", f"Msg {i}", False)
        count = self.db.c.execute("SELECT COUNT(*) FROM conversations WHERE channel_id = ?", (channel,)).fetchone()[0]
        self.assertEqual(count, MAX_CONTEXT_MESSAGES)

if __name__ == "__main__":
    unittest.main()
