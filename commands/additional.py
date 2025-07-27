import disnake
from disnake.ext import commands
from config import OWNER_ID, load_admins, save_admins

class ModerationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="admin", description="Управление администраторами")
    async def admin(self, inter: disnake.ApplicationCommandInteraction):
        # Если вызвано без подкоманды — покажем помощь
        await inter.response.send_message("Используйте подкоманды: add, remove", ephemeral=True)

    @admin.sub_command(name="add", description="Добавить администратора")
    async def admin_add(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        if inter.author.id != OWNER_ID:
            await inter.response.send_message("❌ У тебя нет доступа к этой команде.", ephemeral=True)
            return

        admins = load_admins()
        if user.id in admins:
            await inter.response.send_message(f"👮 {user.mention} уже является админом.")
        else:
            admins.append(user.id)
            save_admins(admins)
            await inter.response.send_message(f"✅ {user.mention} теперь администратор.")

    @admin.sub_command(name="remove", description="Удалить администратора")
    async def admin_remove(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        if inter.author.id != OWNER_ID:
            await inter.response.send_message("❌ У тебя нет доступа к этой команде.", ephemeral=True)
            return

        admins = load_admins()
        if user.id not in admins:
            await inter.response.send_message(f"⚠️ {user.mention} не является админом.")
        else:
            admins.remove(user.id)
            save_admins(admins)
            await inter.response.send_message(f"🗑️ {user.mention} больше не администратор.")


def setup(bot):
    bot.add_cog(ModerationCommands(bot))
