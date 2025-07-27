import disnake
from disnake.ext import commands, tasks
import aiohttp
import asyncio
import threading
import os
import socket
import time
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

def fake_web_server():
    port = int(os.environ.get("PORT", 10000))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", port))
    sock.listen(1)
    while True:
        time.sleep(100)

# Запуск фейкового сервера в фоне
threading.Thread(target=fake_web_server, daemon=True).start()

# --- Настройка Discord-бота ---
intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)


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
bot.run(os.getenv(TOKEN))

