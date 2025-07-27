import disnake
from disnake.ext import commands
import requests
import json
from config import API_KEY, OWNER_COMMANDS, ADMINISTRATOR_COMMANDS, MODERATOR_COMMANDS, MODERATOR_ROLE_ID, ADMIN_ROLE_ID, SHR_ROLE_ID

class SendCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def user_allowed_commands(self, member: disnake.Member) -> set:
        member_role_ids = {role.id for role in member.roles}

        if SHR_ROLE_ID in member_role_ids:
            return OWNER_COMMANDS
        elif any(role_id in member_role_ids for role_id in ADMIN_ROLE_ID):
            return ADMINISTRATOR_COMMANDS
        elif any(role_id in member_role_ids for role_id in MODERATOR_ROLE_ID):
            return MODERATOR_COMMANDS
        else:
            return set()

    @commands.slash_command(name="sendcommand", description="Send a custom command to server API")
    async def send_command(
        self,
        inter: disnake.ApplicationCommandInteraction,
        message: str = commands.Param(description="Message to send, e.g. ':h Hey everyone!'")
    ):
        await inter.response.defer()

        allowed = self.user_allowed_commands(inter.author)
        command_token = message.strip().split()[0].lower()

        if command_token not in allowed:
            await inter.followup.send("You don't have permission to use this command.")
            return

        try:
            payload = {"command": message}
            response = requests.post(
                "https://api.policeroleplay.community/v1/server/command",
                headers={
                    "server-key": API_KEY,
                    "Accept": "*/*"
                },
                json=payload
            )
            data = response.json()
            
        except Exception as e:
            await inter.followup.send(f"{e}")


def setup(bot):
    bot.add_cog(SendCommandCog(bot))
