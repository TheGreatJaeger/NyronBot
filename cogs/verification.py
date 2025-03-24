import discord
from discord.ext import commands
from discord import app_commands
import json
import os

VERIFY_FILE = "cogs/jsonfiles/verify_config.json"

class Verification(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.verify_data = self.load_data()

    def load_data(self):
        if not os.path.exists(VERIFY_FILE):
            return {}
        with open(VERIFY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_data(self):
        with open(VERIFY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.verify_data, f, indent=4)

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Verification system is ready!")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data.get("custom_id") == "verify_button":
            guild_id = str(interaction.guild.id)
            if guild_id in self.verify_data:
                config = self.verify_data[guild_id]
                if not config.get("enabled", True):
                    return await interaction.response.send_message("❌ Verification system is currently disabled.", ephemeral=True)
                role = interaction.guild.get_role(config.get("role_id"))
                if role:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message("✅ You have been verified!", ephemeral=True)

    @app_commands.command(name="verify_setup", description="Setup the verification system")
    @app_commands.checks.has_permissions(administrator=True)
    async def verify_setup(self, interaction: discord.Interaction, 
                           channel: discord.TextChannel, 
                           role: discord.Role, 
                           message: str, 
                           button_text: str = "Verify", 
                           embed_title: str = "Verification Required",
                           image_url: str = None,
                           button_style: str = "blurple"):

        guild_id = str(interaction.guild.id)

        style_map = {
            "blurple": discord.ButtonStyle.blurple,
            "grey": discord.ButtonStyle.grey,
            "gray": discord.ButtonStyle.grey,
            "green": discord.ButtonStyle.green,
            "red": discord.ButtonStyle.red,
            "primary": discord.ButtonStyle.primary,
            "secondary": discord.ButtonStyle.secondary,
            "danger": discord.ButtonStyle.danger,
            "success": discord.ButtonStyle.success
        }

        style = style_map.get(button_style.lower(), discord.ButtonStyle.blurple)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=button_text, style=style, custom_id="verify_button"))

        embed = discord.Embed(title=embed_title, description=message, color=discord.Color.green())
        if image_url:
            embed.set_image(url=image_url)

        await channel.send(embed=embed, view=view)

        self.verify_data[guild_id] = {
            "channel_id": channel.id,
            "role_id": role.id,
            "message": message,
            "button_text": button_text,
            "embed_title": embed_title,
            "image_url": image_url,
            "style": button_style.lower(),
            "enabled": True
        }
        self.save_data()

        await interaction.response.send_message("✅ Verification system configured!", ephemeral=True)

    @app_commands.command(name="verify_enable", description="Enable the verification system")
    @app_commands.checks.has_permissions(administrator=True)
    async def verify_enable(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id not in self.verify_data:
            return await interaction.response.send_message("❌ Verification system not set up.", ephemeral=True)
        self.verify_data[guild_id]["enabled"] = True
        self.save_data()
        await interaction.response.send_message("✅ Verification system enabled.", ephemeral=True)

    @app_commands.command(name="verify_disable", description="Disable the verification system")
    @app_commands.checks.has_permissions(administrator=True)
    async def verify_disable(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        if guild_id not in self.verify_data:
            return await interaction.response.send_message("❌ Verification system not set up.", ephemeral=True)
        self.verify_data[guild_id]["enabled"] = False
        self.save_data()
        await interaction.response.send_message("🛑 Verification system disabled.", ephemeral=True)

async def setup(client):
    await client.add_cog(Verification(client))
