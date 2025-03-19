import discord
from discord.ext import commands
from discord import app_commands
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

    @app_commands.command(name="gamehelp", description="Provides gaming tips based on user questions")
    @app_commands.describe(game="Game title", question="Your question")
    async def gamehelp(self, interaction: discord.Interaction, game: str, question: str):
        """Provides gaming tips based on user questions"""
        
        if not game or not question:
            await interaction.response.send_message(
                "❌ **You must provide a game title and a question!**\nExample: `/gamehelp Elden Ring Best mage build?`",
                ephemeral=True
            )
            return

        await interaction.response.send_message(f"🔍 Searching for the best answer for **{game}**...", ephemeral=True)

        search_query = f"{game} {question}"

        params = {
            "q": search_query,
            "engine": "google",
            "api_key": SERPAPI_KEY,
            "num": 5
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        if "organic_results" in results:
            links = [res["link"] for res in results["organic_results"]]

            if links:
                random_link = random.choice(links)
                await interaction.followup.send(f"✅ **Found a guide for {game}!**\n{random_link}")
            else:
                await interaction.followup.send("❌ Couldn't find a useful guide 😔 Try a different query.")
        else:
            await interaction.followup.send("⚠ No results found. Please try again later.")

async def setup(bot):
    await bot.add_cog(GameGuru(bot))
