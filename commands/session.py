import disnake
from disnake.ext import commands
import time
import json
from config import STARTUP_CHANNEL_ID, SHUTDOWN_CHANNEL_ID, STARTUP_REACTION_COUNT

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
        global startup_message_id, session_start_time, current_embed_message_id

        session_start_time = int(time.time())
        await inter.response.defer(ephemeral=True)

        embeds = load_embeds_from_json("sessionsjson/startup.json")
        views = load_views_from_json("sessionsjson/startup.json")

        if not embeds:
            await inter.followup.send("\u200b", ephemeral=True)
            return

        channel = self.bot.get_channel(STARTUP_CHANNEL_ID)
        if not channel:
            await inter.followup.send("\u200b", ephemeral=True)
            return

        message = await channel.send(embed=embeds[0], view=views[0] if views else None)
        startup_message_id = message.id
        await message.add_reaction("✅")

        for embed in embeds[1:]:
            await channel.send(embed=embed)

        await inter.followup.send("Session started!", ephemeral=True)

        # Ждём реакции ✅
        async def wait_for_reactions():
            global startup_message_id
            while True:
                msg = await channel.fetch_message(startup_message_id)
                for reaction in msg.reactions:
                    if str(reaction.emoji) == "✅":
                        users = [user async for user in reaction.users() if not user.bot]
                        if len(users) >= STARTUP_REACTION_COUNT:
                            await msg.delete()
                            startup_message_id = None

                            timestamp_str = f"<t:{session_start_time}:R>"
                            current_embeds = load_embeds_from_json("sessionsjson/current.json", {
                                "{SERVERE_STARTUP_TIME}": timestamp_str
                            })

                            if current_embeds:
                                sent = await channel.send(embed=current_embeds[0])
                                current_embed_message_id = sent.id
                            return
                await disnake.utils.sleep_until(time.time() + 1)

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
            await inter.channel.send("")
            return

        startup_channel = self.bot.get_channel(STARTUP_CHANNEL_ID)
        if startup_channel:
            for embed in shutdown_embeds:
                await startup_channel.send(embed=embed)
        else:
            await inter.channel.send("")

        current_embed_message_id = None
        await inter.followup.send("Session is ended.", ephemeral=True)
