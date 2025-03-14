import discord
from discord.ext import commands
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

  @commands.command(aliases=["calc", "solve"])
  async def calculate(self, ctx, *, expression: str):
    try:
        answer = numexpr.evaluate(expression)

        await ctx.send(f"{ctx.author.mention}, {expression} = {answer}")
    except:
      await ctx.send(f"{ctx.author.mention}, Error: Invalid Expression.")


async def setup(client):
  await client.add_cog(Calc(client))

