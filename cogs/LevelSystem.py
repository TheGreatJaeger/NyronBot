import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import math
import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont
import random
import time
import os

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
            return  # system disabled

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
        await interaction.response.defer()

        user = user or interaction.user
        author_id = str(user.id)

        if author_id not in self.users:
            self.users[author_id] = {"Level": 1, "Experience": 0}

        level = self.users[author_id]["Level"]
        xp = self.users[author_id]["Experience"]
        required = math.ceil((6 * (level ** 4)) / 2.5)
        percent = xp / required if required != 0 else 0

        # 1. background
        bg_folder = "cogs/levelcards"
        card_files = [f for f in os.listdir(bg_folder) if f.endswith((".png", ".jpg", ".jpeg"))]
        if not card_files:
            return await interaction.followup.send("❌ No background images found.", ephemeral=True)
        bg_path = os.path.join(bg_folder, random.choice(card_files))
        bg = Image.open(bg_path).convert("RGBA").resize((800, 250))

        # 2. making background darker
        overlay = Image.new("RGBA", bg.size, (0, 0, 0, 130))
        bg = Image.alpha_composite(bg, overlay)

        draw = ImageDraw.Draw(bg)

        # 3. avatar
        async with aiohttp.ClientSession() as session:
            async with session.get(user.display_avatar.replace(format='png', size=128).url) as resp:
                avatar_bytes = await resp.read()
        pfp = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((100, 100))
        mask = Image.new("L", pfp.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 100, 100), fill=255)
        pfp.putalpha(mask)
        bg.paste(pfp, (30, 75), pfp)

        # 4. fonts
        try:
            font_big = ImageFont.truetype("SouthPark.otf", 28)
            font_small = ImageFont.truetype("SouthPark.otf", 20)
        except:
            return await interaction.followup.send("❌ Font not found.", ephemeral=True)

        # 5. Name and level
        draw.text((150, 70), f"{user.name}", font=font_big, fill=(255, 165, 0))
        draw.text((150, 110), f"Level: {level}   XP: {xp}/{required}", font=font_small, fill=(255, 165, 0))

        # 6. Progress bar
        bar_x = 150
        bar_y = 150
        bar_width = 600
        bar_height = 25
        outline_color = (255, 255, 255, 180)
        fill_color = (255, 165, 0, 255)
        
        draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_width, bar_y + bar_height), radius=12, fill=(255,255,255,50))
        draw.rounded_rectangle((bar_x, bar_y, bar_x + int(bar_width * percent), bar_y + bar_height), radius=12, fill=fill_color)

        # 7. send
        buffer = io.BytesIO()
        bg.save(buffer, format="PNG")
        buffer.seek(0)

        file = discord.File(buffer, filename="levelcard.png")
        await interaction.followup.send(file=file)
        
    # ✅ Enable level system
    @app_commands.command(name="enable_levels", description="Enable level system for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def enable_levels(self, interaction: discord.Interaction):
        self.enabled_guilds.add(interaction.guild.id)
        await interaction.response.send_message("✅ Level system has been **enabled** on this server.", ephemeral=True)

    # ✅ Disable level system
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
