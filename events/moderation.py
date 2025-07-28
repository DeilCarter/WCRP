import disnake
from disnake.ext import commands
from collections import defaultdict, deque
import time
import re
from config import *
from badwords import BAD_WORDS

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = defaultdict(lambda: deque(maxlen=FLOOD_LIMIT))
        self.user_repeats = defaultdict(lambda: {"last_msg": "", "count": 0})

    def normalize_text(self, text: str) -> str:
        text = text.lower()
        substitutions = {
            "0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t",
            "@": "a", "$": "s", "!": "i", "*": "", ".": "", "-": "",
            "_": "", " ": "",
        }
        for key, value in substitutions.items():
            text = text.replace(key, value)
        text = re.sub(r"[^a-zа-яё0-9]", "", text, flags=re.IGNORECASE)
        return text

    def contains_bad_word(self, message: str) -> bool:
        raw_text = message.lower()
        cleaned_text = self.normalize_text(raw_text)
        for word in BAD_WORDS:
            if re.search(rf"\b{re.escape(word)}\b", raw_text) or word in cleaned_text:
                return True
        return False

    async def warn_user(self, message: disnake.Message, reason: str):
        try:
            await message.channel.send(f"{message.author.mention}, ⚠️ {reason}", delete_after=5)
        except disnake.Forbidden:
            pass

        log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = disnake.Embed(title="Moderation Alert", color=disnake.Color.red())
            embed.add_field(name="User", value=message.author.mention, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Channel", value=message.channel.mention, inline=False)
            embed.add_field(name="Message", value=message.content[:1000], inline=False)
            embed.timestamp = message.created_at
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        # ✅ Skip moderation if user has BYPASS role
        if any(role.name == "BYPASS" for role in message.author.roles):
            return

        now = time.time()
        user_id = message.author.id
        content = message.content.strip()

        # Anti-Flood
        self.user_messages[user_id].append(now)
        if len(self.user_messages[user_id]) >= FLOOD_LIMIT:
            if now - self.user_messages[user_id][0] < FLOOD_INTERVAL:
                await message.delete()
                await self.warn_user(message, "Do not flood the chat!")
                return

        # Anti-Spam
        if self.user_repeats[user_id]["last_msg"] == content:
            self.user_repeats[user_id]["count"] += 1
        else:
            self.user_repeats[user_id]["last_msg"] = content
            self.user_repeats[user_id]["count"] = 1

        if self.user_repeats[user_id]["count"] >= SPAM_REPEAT_LIMIT:
            await message.delete()
            await self.warn_user(message, "Please do not spam the same message!")
            return

        # Anti-Mass Mention
        if message.mentions and len(message.mentions) >= MENTION_LIMIT:
            await message.delete()
            await self.warn_user(message, "Too many mentions!")
            return

        # Anti-Badword
        if self.contains_bad_word(content):
            await message.delete()
            await self.warn_user(message, "Watch your language!")
            return

        await self.bot.process_commands(message)

def setup(bot):
    bot.add_cog(Moderation(bot))
