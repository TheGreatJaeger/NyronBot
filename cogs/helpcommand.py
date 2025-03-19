import discord
from discord.ext import commands
from discord import app_commands

class HelpCommand(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("helpcommand.py is ready!")
  
    @app_commands.command(name="help", description="Shows list of commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Commands list", color=discord.Color.green())

        for cog_name, cog in self.client.cogs.items():  # Заменил self.bot на self.client
            commands_list = [
                f"`/{command.name}` - {command.description or 'No description'}"
                for command in cog.__cog_app_commands__
            ]
            if commands_list:
                embed.add_field(name=f"📂 {cog_name}", value="\n".join(commands_list), inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(client):
    await client.add_cog(HelpCommand(client))
