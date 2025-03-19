import discord
from discord.ext import commands
from discord import app_commands
from numpy import *
import numexpr

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

class Calc(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_ready(self):
    print(f"{__name__} is online.")

  @app_commands.command(name="calculate", description="Evaluate a mathematical expression")
  async def calculate(self, interaction: discord.Interaction, expression: str):
        """Evaluates a mathematical expression"""
        try:
            answer = numexpr.evaluate(expression)
            await interaction.response.send_message(f"🧮 `{expression} = {answer}`", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Error: Invalid Expression.", ephemeral=True)


async def setup(client):
  await client.add_cog(Calc(client))

