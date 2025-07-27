import disnake
from disnake.ext import commands

class AdditionalCommands(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="ping", description="Check bot response")
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.send_message("Pong! 🏓")

def setup(bot):
    bot.add_cog(AdditionalCommands(bot))
