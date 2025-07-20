import aiosqlite

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.db = None

    async def connect(self):
        self.db = await aiosqlite.connect(self.db_file)
        await self.db.execute("CREATE TABLE IF NOT EXISTS tags (name TEXT PRIMARY KEY, content TEXT)")
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT,
            user_id TEXT,
            message TEXT,
            is_bot BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        await self.db.commit()

    async def get_tag(self, name):
        async with self.db.execute("SELECT content FROM tags WHERE name = ?", (name,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

    async def add_tag(self, name, content):
        await self.db.execute("INSERT INTO tags (name, content) VALUES (?, ?)", (name, content))
        await self.db.commit()

    async def edit_tag(self, name, content):
        await self.db.execute("UPDATE tags SET content = ? WHERE name = ?", (content, name))
        await self.db.commit()

    async def delete_tag(self, name):
        await self.db.execute("DELETE FROM tags WHERE name = ?", (name,))
        await self.db.commit()

    async def list_tags(self):
        async with self.db.execute("SELECT name FROM tags") as cursor:
            return [row[0] async for row in cursor]

    async def rename_tag(self, old_name, new_name):
        if not await self.get_tag(old_name):
            return False, f"Tag `{old_name}` does not exist... unless you believe in yourself."
        if await self.get_tag(new_name):
            return False, f"Tag `{new_name}` already exists. And one is *definitely* enough."
        content = await self.get_tag(old_name)
        await self.add_tag(new_name, content)
        await self.delete_tag(old_name)
        return True, f"Tag `{old_name}` is now tag `{new_name}`. Have fun watching me make fun of the people who deadname `{new_name}`!"

    async def save_message(self, channel_id, user_id, message, is_bot, max_context_messages=420):
        await self.db.execute(
            "INSERT INTO conversations (channel_id, user_id, message, is_bot) VALUES (?, ?, ?, ?)",
            (str(channel_id), str(user_id), message, is_bot)
        )
        await self.db.commit()
        async with self.db.execute("SELECT COUNT(*) FROM conversations WHERE channel_id = ?", (str(channel_id),)) as cursor:
            count = (await cursor.fetchone())[0]
        if count > max_context_messages:
            to_delete = count - max_context_messages
            await self.db.execute(
                "DELETE FROM conversations WHERE id IN (SELECT id FROM conversations WHERE channel_id = ? ORDER BY created_at ASC LIMIT ?)",
                (str(channel_id), to_delete)
            )
            await self.db.commit()

    async def get_recent_context_rows(self, channel_id, limit=69):
        async with self.db.execute(
            "SELECT user_id, message, is_bot FROM conversations WHERE channel_id = ? ORDER BY created_at DESC LIMIT ?",
            (str(channel_id), limit)
        ) as cursor:
            return await cursor.fetchall()

    async def clear_context(self, channel_id):
        await self.db.execute("DELETE FROM conversations WHERE channel_id = ?", (str(channel_id),))
        await self.db.commit() 