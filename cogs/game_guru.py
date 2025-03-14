import discord
from discord.ext import commands
from serpapi import GoogleSearch
import random
import os
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

class GameGuru(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("game_guru.py is ready!")

    @commands.command()
    async def gamehelp(self, ctx, game: str = None, *, question: str = None):
        """Provides gaming tips based on user questions"""

        if game is None or question is None:
            await ctx.send("❌ **You must put a game title and a question!**\nExample: `!gamehelp Elden Ring Best mage build?`")
            return

        await ctx.send(f"🔍 Searching for the best answer for **{game}**...")

        search_query = f"{game} {question}"

        params = {
            "q": search_query,
            "engine": "google",
            "api_key": SERPAPI_KEY,
            "num": 5  # Number of links in response
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        if "organic_results" in results:
            links = [res["link"] for res in results["organic_results"]]

            if links:
                random_link = random.choice(links)  # Choosing a random link
                await ctx.send(f"✅ **Found a guide for {game}!**\n{random_link}")
            else:
                await ctx.send("❌ Couldn't find a useful guide 😔 Try a different query.")
        else:
            await ctx.send("⚠ No results found. Please try again later.")

async def setup(bot):
    await bot.add_cog(GameGuru(bot))
