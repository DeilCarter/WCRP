import disnake
from disnake.ext import commands
import json
import os 

class ModerationCommands(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="ban", description="Ban a user from the server")
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        reason: str = "No reason provided"
    ):
        # Попытка отправить ЛС с уведомлением о бане
        try:
            file_path = os.path.join("json", "bannotification.json")
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                message = data.get("message", "You have been banned from the server.")
            await member.send(message)
        except Exception as e:
            print(f"Failed to send DM to {member}: {e}")

        # Баним пользователя
        try:
            await member.ban(reason=reason)
            await inter.response.send_message(f"User {member} has been banned for: {reason}")
        except Exception as e:
            await inter.response.send_message(f"Failed to ban user: {e}", ephemeral=True)

def setup(bot):
    bot.add_cog(ModerationCommands(bot))
