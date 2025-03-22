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
        self.user_timers = {}  # XP cooldown per user
        self.levelup_notify_timers = {}  # Level-up cooldown
        self.enabled_guilds = set()  # Guilds with level system enabled

        self.client.loop.create_task(self.save())

        try:
            with open("cogs/jsonfiles/users.json", "r") as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}

        try:
            with open("cogs/jsonfiles/level_enabled.json", "r") as f:
                self.enabled_guilds = set(json.load(f))
        except:
            self.enabled_guilds = set()

    def level_up(self, author_id):
        current_experience = self.users[author_id]["Experience"]
        current_level = self.users[author_id]["Level"]
        required_exp = math.ceil((6 * (current_level ** 4)) / 2.5)
        if current_experience >= required_exp:
            self.users[author_id]["Level"] += 1
            return True
        return False

    async def save(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            with open("cogs/jsonfiles/users.json", "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=4)

            with open("cogs/jsonfiles/level_enabled.json", "w", encoding="utf-8") as f:
                json.dump(list(self.enabled_guilds), f, indent=4)

            await asyncio.sleep(10)

    @commands.Cog.listener()
    async def on_ready(self):
        print("LevelSystem.py is ready")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        if guild_id not in self.enabled_guilds:
            return  # система выключена

        author_id = str(message.author.id)
        now = time.time()

        if author_id in self.user_timers and now - self.user_timers[author_id] < 60:
            return
        self.user_timers[author_id] = now

        if author_id not in self.users:
            self.users[author_id] = {"Level": 1, "Experience": 0}

        self.users[author_id]["Experience"] += random.randint(5, 15)

        if self.level_up(author_id):
            if author_id in self.levelup_notify_timers and now - self.levelup_notify_timers[author_id] < 180:
                return
            self.levelup_notify_timers[author_id] = now

            level = self.users[author_id]["Level"]
            embed = discord.Embed(title="🎉 Level Up!", color=discord.Color.green())
            embed.add_field(
                name="Congratulations!",
                value=f"{message.author.mention} leveled up to level **{level}**!"
            )
            await message.channel.send(embed=embed)

    @app_commands.command(name="level", description="Check your level and experience")
    async def level(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        author_id = str(user.id)

        if author_id not in self.users:
            self.users[author_id] = {"Level": 1, "Experience": 0}

        embed = discord.Embed(
            title=f"{user.name}'s Level & Experience",
            color=discord.Color.random()
        )
        embed.add_field(name="Level:", value=self.users[author_id]["Level"])
        embed.add_field(name="Experience:", value=self.users[author_id]["Experience"])
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar)

        await interaction.response.send_message(embed=embed)

    # ✅ Включить систему уровней
    @app_commands.command(name="enable_levels", description="Enable level system for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def enable_levels(self, interaction: discord.Interaction):
        self.enabled_guilds.add(interaction.guild.id)
        await interaction.response.send_message("✅ Level system has been **enabled** on this server.", ephemeral=True)

    # ✅ Отключить систему уровней
    @app_commands.command(name="disable_levels", description="Disable level system for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def disable_levels(self, interaction: discord.Interaction):
        self.enabled_guilds.discard(interaction.guild.id)
        await interaction.response.send_message("🛑 Level system has been **disabled** on this server.", ephemeral=True)

    @enable_levels.error
    @disable_levels.error
    async def permission_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ You need to be an **administrator** to use this command.", ephemeral=True)
        else:
            raise error

async def setup(client):
    await client.add_cog(LevelSystem(client))
