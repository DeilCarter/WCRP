import aiohttp
import json
import disnake
from disnake.ext import tasks
from config import HEADERS, BANNED_VEHICLES, INGAME_ALARM_CHANNEL_ID

bot_instance = None  # глобальная переменная для хранения экземпляра бота

def start_banned_vehicle_task(bot):
    global bot_instance
    bot_instance = bot
    check_banned_vehicles.start()

@tasks.loop(seconds=30)
async def check_banned_vehicles():
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
                    vehicle_name = vehicle.get("Name", "")
                    owner_name = vehicle.get("Owner", "Неизвестно")

                    if vehicle_name in BANNED_VEHICLES:
                        with open("json/bannedvehicle.json", "r", encoding="utf-8") as f:
                            template = f.read()

                        # Заменяем плейсхолдеры
                        filled_json_str = template.replace("{vehicle_name}", vehicle_name).replace("{owner_name}", owner_name)

                        # Парсим строку в dict
                        embed_data = json.loads(filled_json_str)

                        # Отправляем каждый Embed из списка
                        for embed_dict in embed_data.get("embeds", []):
                            embed = disnake.Embed().from_dict(embed_dict)
                            await channel.send(embed=embed)

        except Exception as e:
            print("Ошибка при проверке запрещённых машин:", e)
