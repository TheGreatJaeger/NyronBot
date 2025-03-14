import discord
from discord import app_commands
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

class AppCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.tree.sync()
        print(f"{__name__} loaded successfully!")

    @app_commands.command(name="avatar", description="Sends user's avatar in a embed (sends own avatar if user is left none).")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user
        elif member is not None:
            member = member

        avatar_embed = discord.Embed(title=f"{member.name}'s Avatar", color=discord.Color.random())
        avatar_embed.set_image(url=member.avatar)
        avatar_embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)

        await interaction.response.send_message(embed=avatar_embed)

    @app_commands.command(name="about", description="Read everything about the bot!")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello, I'm NyronBot! I can do a lot of cool things. Type !help and you'll see something cool :)")

    @app_commands.command(name="8ball", description="Gives you random answers")
    @app_commands.describe(text_to_send="Ask anything!")
    async def eightball(self, interaction: discord.Interaction, text_to_send: str):
        try:
            with open("responses.txt", "r", encoding="utf-8") as f:
                random_responses = f.read().splitlines()
            response = random.choice(random_responses)

            await interaction.response.send_message(f"🎱 {text_to_send}\n**Answer:** {response}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

async def setup(client):
    await client.add_cog(AppCommands(client))
