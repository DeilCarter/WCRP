import disnake
from disnake.ext import commands
import time
import json
import asyncio
from config import STARTUP_CHANNEL_ID, SHUTDOWN_CHANNEL_ID, STARTUP_REACTION_COUNT, SHR_ROLE_ID

startup_message_id = None
current_embed_message_id = None
session_start_time = None

def load_embeds_from_json(filename, replacements=None):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []

    embeds = []
    for entry in data.get("embeds", []):
        desc = entry.get("description", "")
        if replacements:
            for key, value in replacements.items():
                desc = desc.replace(key, value)

        embed = disnake.Embed(description=desc, color=entry.get("color", 0))
        if "title" in entry:
            embed.title = entry["title"]
        if "image" in entry:
            embed.set_image(url=entry["image"]["url"])
        embeds.append(embed)
    return embeds

def load_views_from_json(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []

    views = []
    for row in data.get("components", []):
        view = disnake.ui.View()
        for comp in row.get("components", []):
            if comp["type"] == 2:
                button = disnake.ui.Button(
                    label=comp.get("label", "Button"),
                    style=comp.get("style", disnake.ButtonStyle.primary),
                    url=comp.get("url"),
                    custom_id=comp.get("custom_id") if "url" not in comp else None
                )
                view.add_item(button)
        views.append(view)
    return views

class SessionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Session startup")
    async def session_startup(self, inter: disnake.ApplicationCommandInteraction):
        member = inter.author
        member_role_ids = {role.id for role in member.roles}
        if SHR_ROLE_ID not in member_role_ids:
            await inter.response.send_message("❌ У вас нет прав для запуска сессии.", ephemeral=True)
            return

        try:
            await inter.response.defer(ephemeral=True)
            print("[DEBUG] Defer успешно вызван")
        except Exception as e:
            print(f"[ERROR] Ошибка при defer: {type(e).__name__} - {e}")
            return

        global startup_message_id, session_start_time, current_embed_message_id
        session_start_time = int(time.time())

        embeds = load_embeds_from_json("json/startup.json")
        views = load_views_from_json("json/startup.json")

        if not embeds:
            await inter.followup.send("❌ Не удалось загрузить embed.", ephemeral=True)
            return

        channel = self.bot.get_channel(STARTUP_CHANNEL_ID)
        if not channel:
            await inter.followup.send("❌ Не найден канал запуска.", ephemeral=True)
            return

        message = await channel.send(embed=embeds[0], view=views[0] if views else None)
        startup_message_id = message.id
        await message.add_reaction("✅")

        for embed in embeds[1:]:
            await channel.send(embed=embed)

        await inter.followup.send("✅ Сессия начата. Ожидаем реакции.", ephemeral=True)

        async def wait_for_reactions():
            global startup_message_id, current_embed_message_id

            while startup_message_id:
                try:
                    msg = await channel.fetch_message(startup_message_id)
                except disnake.NotFound:
                    return

                for reaction in msg.reactions:
                    if str(reaction.emoji) == "✅":
                        users = [user async for user in reaction.users() if not user.bot]
                        if len(users) >= STARTUP_REACTION_COUNT:
                            await msg.delete()
                            startup_message_id = None

                            # Здесь время достижения нужного количества галочек
                            reached_time = int(time.time())
                            timestamp_str = f"<t:{reached_time}:R>"

                            current_embeds = load_embeds_from_json("json/current.json", {
                                "{SERVERE_STARTUP_TIME}": timestamp_str
                            })

                            if current_embeds:
                                sent = await channel.send(embed=current_embeds[0])
                                current_embed_message_id = sent.id
                            return

                await asyncio.sleep(1)

        self.bot.loop.create_task(wait_for_reactions())

    @commands.slash_command(description="Session Shutdown")
    async def session_shutdown(self, inter: disnake.ApplicationCommandInteraction):
        global current_embed_message_id

        await inter.response.defer(ephemeral=True)

        try:
            msg = await inter.channel.fetch_message(current_embed_message_id)
            await msg.delete()
        except:
            pass

        shutdown_embeds = load_embeds_from_json("json/shutdown.json")
        if not shutdown_embeds:
            await inter.followup.send("❌ Не удалось загрузить shutdown embed.", ephemeral=True)
            return

        startup_channel = self.bot.get_channel(STARTUP_CHANNEL_ID)
        if startup_channel:
            for embed in shutdown_embeds:
                await startup_channel.send(embed=embed)

        current_embed_message_id = None
        await inter.followup.send("🟥 Сессия завершена.", ephemeral=True)

def setup(bot):
    bot.add_cog(SessionCommands(bot))
