import discord
import json
import os
from discord.ext import commands
from discord import app_commands

WELCOME_FILE = "cogs/jsonfiles/welcome.json"

class Welcome(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Welcome.py is ready!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handles new member join and sends a welcome message."""
        if not os.path.exists(WELCOME_FILE):
            return  # Если файла нет, выходим

        with open(WELCOME_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("[ERROR] welcome.json is corrupted!")
                return

        guild_id = str(member.guild.id)
        if guild_id not in data:
            return

        # Создаём embed приветствия
        welcome_embed = discord.Embed(
            title=f"Welcome to {member.guild.name}!", 
            description=f"Welcome, {member.mention}! You are member #{member.guild.member_count}!",
            color=discord.Color.purple()
        )

        welcome_embed.add_field(name="Welcome Message", value=data[guild_id].get("Message", "Welcome!"), inline=False)
        welcome_embed.set_image(url=data[guild_id].get("ImageUrl", ""))
        welcome_embed.set_footer(text="Glad you've joined!", icon_url=member.display_avatar)

        # Авто-роль
        auto_role_name = data[guild_id].get("AutoRole")
        if auto_role_name:
            auto_role = discord.utils.get(member.guild.roles, name=auto_role_name)
            if auto_role:
                await member.add_roles(auto_role)

        # Отправка сообщения в канал или в ЛС
        channel_name = data[guild_id].get("Channel")
        if channel_name:
            welcome_channel = discord.utils.get(member.guild.channels, name=channel_name)
            if welcome_channel:
                await welcome_channel.send(f"{member.mention}", embed=welcome_embed)
                return
            else:
                print(f"[ERROR] Welcome channel '{channel_name}' not found in {member.guild.name}.")

        # Если канал не задан или не найден, отправляем в ЛС
        try:
            await member.send(embed=welcome_embed)
        except discord.Forbidden:
            print(f"[WARNING] Could not DM {member.name}, they have DMs disabled.")

    @app_commands.command(name="welcome", description="Setup the welcome system for your server")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome(self, interaction: discord.Interaction):
        """Displays information about the welcome system setup"""
        await interaction.response.defer()  # Даем боту больше времени на ответ

        embed = discord.Embed(
            title="Welcome System Setup",
            description="Configure the welcome system for your server!",
            color=discord.Color.teal()
        )
        embed.add_field(name="/welcome_autorole", value="Set an automatic role for new users.", inline=False)
        embed.add_field(name="/welcome_message", value="Set a custom welcome message.", inline=False)
        embed.add_field(name="/welcome_channel", value="Set the channel for the welcome message.", inline=False)
        embed.add_field(name="/welcome_img", value="Set an image or GIF URL for the welcome message.", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="welcome_autorole", description="Set an automatic role for new members")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_autorole(self, interaction: discord.Interaction, role: discord.Role):
        """Sets an automatic role for new members"""
        if not os.path.exists(WELCOME_FILE):
            data = {}
        else:
            with open(WELCOME_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        guild_id = str(interaction.guild.id)
        if guild_id not in data:
            data[guild_id] = {}

        data[guild_id]["AutoRole"] = role.name

        with open(WELCOME_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        await interaction.response.send_message(f"✅ Auto-role set to {role.mention}.", ephemeral=True)

    @app_commands.command(name="welcome_message", description="Set the welcome message")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_message(self, interaction: discord.Interaction, message: str):
        """Sets the welcome message"""
        if not os.path.exists(WELCOME_FILE):
            data = {}
        else:
            with open(WELCOME_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        guild_id = str(interaction.guild.id)
        if guild_id not in data:
            data[guild_id] = {}

        data[guild_id]["Message"] = message

        with open(WELCOME_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        await interaction.response.send_message(f"✅ Welcome message updated.", ephemeral=True)

    @app_commands.command(name="welcome_channel", description="Set the welcome message channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Sets the channel for the welcome message"""
        if not os.path.exists(WELCOME_FILE):
            data = {}
        else:
            with open(WELCOME_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        guild_id = str(interaction.guild.id)
        if guild_id not in data:
            data[guild_id] = {}

        data[guild_id]["Channel"] = channel.name

        with open(WELCOME_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        await interaction.response.send_message(f"✅ Welcome messages will be sent in {channel.mention}.", ephemeral=True)

    @app_commands.command(name="welcome_img", description="Set the welcome image URL")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_img(self, interaction: discord.Interaction, url: str):
        """Sets an image for the welcome message"""
        if not os.path.exists(WELCOME_FILE):
            data = {}
        else:
            with open(WELCOME_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

        guild_id = str(interaction.guild.id)
        if guild_id not in data:
            data[guild_id] = {}

        data[guild_id]["ImageUrl"] = url

        with open(WELCOME_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        await interaction.response.send_message("✅ Welcome image updated.", ephemeral=True)

async def setup(client):
    await client.add_cog(Welcome(client))
