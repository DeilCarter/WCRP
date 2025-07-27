import disnake
from disnake.ext import commands, tasks
import aiohttp
import asyncio
from config import TOKEN, API_KEY, API_URL, HEADERS

intents = disnake.Intents.all()
bot = commands.InteractionBot(intents=intents)

@tasks.loop(minutes=1)
async def check_server_status():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_URL, headers=HEADERS) as response:
                data = await response.json()

                current_players = data.get("CurrentPlayers", 0)

                if current_players >= 1:
                    await bot.change_presence(status=disnake.Status.online,
                                              activity=disnake.Game("Server Online"))
                else:
                    await bot.change_presence(status=disnake.Status.do_not_disturb,
                                              activity=disnake.Game("Server Offline"))
        except Exception as e:
            print(f"Can't fetch server API: {e}")
            await bot.change_presence(status=disnake.Status.do_not_disturb,
                                      activity=disnake.Game("Server Offline"))

from commands.session import SessionCommands
from commands.additional import AdditionalCommands
from commands.moderation import ModerationCommands

from events.banned_vehicle_monitor import start_banned_vehicle_task

bot.add_cog(ModerationCommands(bot))
bot.add_cog(SessionCommands(bot))
bot.add_cog(AdditionalCommands(bot))

@bot.event
async def on_ready():
    print(f"✅ Bot started as {bot.user}")
    await check_server_status()
    check_server_status.start()
    start_banned_vehicle_task(bot)

bot.run(TOKEN)
