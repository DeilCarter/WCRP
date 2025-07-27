import aiohttp
import json
import disnake
from disnake.ext import tasks
from config import HEADERS, BANNED_VEHICLES, INGAME_ALARM_CHANNEL_ID
import time

bot_instance = None
recent_vehicles = {}  # Глобальный кэш: {(vehicle_name, owner_name): timestamp}

ANTI_SPAM_TIMEOUT = 30 * 60  # 30 минут в секундах

def start_banned_vehicle_task(bot):
    global bot_instance
    bot_instance = bot
    check_banned_vehicles.start()

@tasks.loop(seconds=30)
async def check_banned_vehicles():
    now = time.time()  # текущее время в секундах

    # Очищаем устаревшие записи из кэша
    to_delete = [key for key, t in recent_vehicles.items() if now - t > ANTI_SPAM_TIMEOUT]
    for key in to_delete:
        del recent_vehicles[key]

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.policeroleplay.community/v1/server/vehicles", headers=HEADERS) as response:
                if response.status != 200:
                    print("Ошибка API:", response.status)
                    return

                vehicles = await response.json()
                channel = bot_instance.get_channel(INGAME_ALARM_CHANNEL_ID)
                if not channel:
                    print("Канал не найден")
                    return

                for vehicle in vehicles:
                    vehicle_name = vehicle.get("Name", "").strip()
                    owner_name = vehicle.get("Owner", "Неизвестно").strip()
                    key = (vehicle_name, owner_name)

                    if vehicle_name in BANNED_VEHICLES:
                        last_sent = recent_vehicles.get(key)
                        if last_sent and now - last_sent < ANTI_SPAM_TIMEOUT:
                            continue  # Пропускаем уже отправленное сообщение

                        # Загрузка шаблона
                        with open("json/bannedvehicle.json", "r", encoding="utf-8") as f:
                            template = f.read()

                        # Подстановка значений
                        filled_json_str = template.replace("{vehicle_name}", vehicle_name).replace("{owner_name}", owner_name)
                        embed_data = json.loads(filled_json_str)

                        # Отправка Embed'ов
                        for embed_dict in embed_data.get("embeds", []):
                            embed = disnake.Embed().from_dict(embed_dict)
                            await channel.send(embed=embed)

                        print(f"🚨 Отправлено: {vehicle_name} ({owner_name})")
                        recent_vehicles[key] = now  # Обновляем кэш

        except Exception as e:
            print("Error:", e)
