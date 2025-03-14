import discord
import json
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

# File to store report channel IDs
REPORT_CHANNELS_FILE = "cogs/jsonfiles/report_channels.json"

# Load report channel IDs if file exists
if os.path.exists(REPORT_CHANNELS_FILE):
    with open(REPORT_CHANNELS_FILE, "r") as f:
        report_channels = json.load(f)
else:
    report_channels = {}

class ReportModal(discord.ui.Modal, title="Report User"):
    def __init__(self):
        super().__init__()

        self.user_name = discord.ui.TextInput(
            label="User's Discord Name",
            placeholder="e.g. JohnDoe#0000",
            required=True,
            max_length=100,
            style=discord.TextStyle.short
        )

        self.user_id = discord.ui.TextInput(
            label="User's Discord ID",
            placeholder="To grab a user's ID, enable Developer Mode.",
            required=True,
            max_length=100,
            style=discord.TextStyle.short
        )

        self.description = discord.ui.TextInput(
            label="What did they do?",
            placeholder="e.g. Broke rule #7",
            required=True,
            min_length=20,
            max_length=2000,
            style=discord.TextStyle.paragraph
        )

        self.add_item(self.user_name)
        self.add_item(self.user_id)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)

        # Check if a report channel is set
        if guild_id not in report_channels:
            await interaction.response.send_message(
                "❌ Report channel is not set! Use `/setreportchannel`.", ephemeral=True
            )
            return

        report_channel = interaction.client.get_channel(report_channels[guild_id])
        if not report_channel:
            await interaction.response.send_message(
                "❌ Report channel not found! An admin needs to set it again.", ephemeral=True
            )
            return

        # Mention admins or @here
        guild = interaction.guild
        admin_role = discord.utils.get(guild.roles, permissions=discord.Permissions(administrator=True))
        
        # Default to @here if no admin role is found or if admin role is the bot itself
        mention_text = "@here"  

        # If admin role exists and is not the bot's role, use its mention
        if admin_role and admin_role.id != interaction.client.user.id:
            mention_text = admin_role.mention

        embed = discord.Embed(title="🔴 New Report", color=discord.Color.red())
        embed.add_field(name="👤 User Name", value=self.user_name.value, inline=False)
        embed.add_field(name="🆔 User ID", value=self.user_id.value, inline=False)
        embed.add_field(name="📜 Description", value=self.description.value, inline=False)
        embed.set_footer(text=f"Reported by: {interaction.user}")

        await report_channel.send(f"{mention_text} A new report has been submitted!", embed=embed)
        await interaction.response.send_message("✅ Report submitted!", ephemeral=True)


class ReportCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is ready!")

    @app_commands.command(name="report", description="Report a user")
    async def report(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ReportModal())

    @app_commands.command(name="setreportchannel", description="Set the report channel")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_report_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Command to set the report channel (admins only)"""
        guild_id = str(interaction.guild.id)
        report_channels[guild_id] = channel.id

        # Save to JSON
        with open(REPORT_CHANNELS_FILE, "w") as f:
            json.dump(report_channels, f, indent=4)

        await interaction.response.send_message(f"✅ Report channel set to: {channel.mention}", ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(ReportCog(client))
