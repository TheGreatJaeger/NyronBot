import discord
from discord.ext import commands
from discord import app_commands

class HelpCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("helpcommand.py is ready!")

    @app_commands.command(name="help", description="Shows a list of available commands")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Избегаем "The application did not respond"

        category_icons = {
            "Welcome": "⚙️",
            "Moderation": "🛡️",
            "Economy": "💰",
            "Music": "🎵",
            "VirtualPet": "🎉",
            "Utility": "🔧",
            "ServerAutomation": "📌",
            "Ticket": "🎟️",
            "LevelSystem": "🔔",
            "Report": "❓",
            "Mute": "🤐",
            "HelpCommand": "📄",
            "GameGuru": "🖥️",
            "MemeGenerator": "😂",
            
        }

        embed = discord.Embed(
            title="📜 NyronBot Command List",
            description="Here is a list of all available commands.",
            color=discord.Color.dark_blue()
        )
        embed.set_thumbnail(url=interaction.client.user.avatar.url)  # Устанавливаем аватар бота

        for cog_name, cog in self.client.cogs.items():
            commands_list = [
                f"🔹 **`/{command.name}`** — {command.description or '*No description*'}"
                for command in cog.__cog_app_commands__
            ]
            if commands_list:
                icon = category_icons.get(cog_name, "📂")  # Получаем иконку, если нет - стандартная папка
                embed.add_field(
                    name=f"{icon} **{cog_name}**",
                    value="\n".join(commands_list),
                    inline=False
                )

        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar.url)

        await interaction.followup.send(embed=embed)

async def setup(client):
    await client.add_cog(HelpCommand(client))
