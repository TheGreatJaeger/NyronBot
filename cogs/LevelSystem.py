import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import math
import random
import time

class LevelSystem(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.user_timers = {}  # Dictionary for storing the time of the last experience gained

        self.client.loop.create_task(self.save())

        try:
            with open("cogs/jsonfiles/users.json", "r") as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}  # If file not found, than create a new one

    def level_up(self, author_id):
        """Проверяет, можно ли повысить уровень пользователя"""
        current_experience = self.users[author_id]["Experience"]
        current_level = self.users[author_id]["Level"]

        if current_experience >= math.ceil((6 * (current_level ** 4)) / 2.5):
            self.users[author_id]["Level"] += 1
            return True
        return False

    async def save(self):
        """Периодически сохраняет данные в JSON"""
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            with open("cogs/jsonfiles/users.json", "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=4)

            await asyncio.sleep(10)  # Saving once in 10 seconds

    @commands.Cog.listener()
    async def on_ready(self):
        print("LevelSystem.py is ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Выдаёт опыт раз в 60 секунд"""
        if message.author.bot:  # Игнорируем ботов
            return
        
        author_id = str(message.author.id)
        current_time = time.time()

        # Check if 60 seconds have passed since the last experience gained
        if author_id in self.user_timers and current_time - self.user_timers[author_id] < 60:
            return  # If not, we don’t give out experience.

        # Update the time of the last experience gained
        self.user_timers[author_id] = current_time

        # If user doesn't exist in database, than add him
        if author_id not in self.users:
            self.users[author_id] = {"Level": 1, "Experience": 0}

        # Adding random exp from 5 to 15
        random_exp = random.randint(5, 15)
        self.users[author_id]["Experience"] += random_exp

        # Checking if user has leveled up
        if self.level_up(author_id):
            level_up_embed = discord.Embed(title="🎉 Level Up!", color=discord.Color.green())
            level_up_embed.add_field(
                name="Congratulations!",
                value=f"{message.author.mention} leveled up to level **{self.users[author_id]['Level']}**!"
            )
            await message.channel.send(embed=level_up_embed)

    @app_commands.command(name="level", description="Check your level and experience")
    async def level(self, interaction: discord.Interaction, user: discord.User = None):
        """Shows the level of user"""
        user = user or interaction.user
        author_id = str(user.id)

        if author_id not in self.users:
            self.users[author_id] = {"Level": 1, "Experience": 0}

        level_card = discord.Embed(
            title=f"{user.name}'s Level & Experience",
            color=discord.Color.random()
        )
        level_card.add_field(name="Level:", value=self.users[author_id]["Level"])
        level_card.add_field(name="Experience:", value=self.users[author_id]["Experience"])
        level_card.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)

        await interaction.response.send_message(embed=level_card)

async def setup(client):
    await client.add_cog(LevelSystem(client))
