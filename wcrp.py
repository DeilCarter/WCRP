import disnake
from disnake.ext import commands, tasks
import aiohttp
import asyncio
import threading
import os
import socket
import time

from config import TOKEN, API_URL, HEADERS

# --- Функция fake_web_server для "фейкового" сервера ---
def fake_web_server():
    port = int(os.environ.get("PORT", 10000))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", port))
    sock.listen(1)
    while True:
        time.sleep(100)

# Запуск fake_web_server в отдельном потоке
threading.Thread(target=fake_web_server, daemon=True).start()

# --- Создаем бота ---
intents = disnake.Intents.all()
bot = commands.InteractionBot(intents=intents)  # Используем InteractionBot (для slash-команд)

# --- Задача для проверки статуса сервера ---
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

extensions = [
    "commands.session",
    "commands.additional",
    "commands.gameintegration", 
]

for ext in extensions:
    try:
        bot.load_extension(ext)
        print(f"Loaded cog: {ext.split('.')[-1]}")
    except Exception as e:
        print(f"Failed to load cog {ext.split('.')[-1]}: {e}")

from events.banned_vehicle_monitor import start_banned_vehicle_task

@bot.event
async def on_ready():
    print(f"✅ Bot started as {bot.user}")
    await check_server_status()
    check_server_status.start()
    start_banned_vehicle_task(bot)

# --- Запуск бота ---
bot.run(TOKEN)
