import discord
import asyncio
import json
import os
from discord import app_commands, utils
from discord.ext import commands

CONFIG_FILE = "cogs/jsonfiles/ticket_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

class TicketView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎟 Create Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = load_config()
        guild_id = str(interaction.guild.id)

        ticket = utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.id}")
        if ticket:
            await interaction.response.send_message(f"❗ You already have a ticket: {ticket.mention}", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        ticket_channel = await interaction.guild.create_text_channel(
            name=f"ticket-{interaction.user.id}",
            overwrites=overwrites,
            reason=f"Ticket for {interaction.user}"
        )

        await ticket_channel.send(
            f"{interaction.user.mention}, your ticket has been created! Use the buttons below.",
            view=ManageTicketView(self.bot, interaction.user, config.get(guild_id, {}).get("log_channel"))
        )
        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

class ManageTicketView(discord.ui.View):
    def __init__(self, bot: commands.Bot, user: discord.User, log_channel_name: str = None):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user
        self.log_channel_name = log_channel_name

    @discord.ui.button(label="📄 Save Ticket", style=discord.ButtonStyle.green, custom_id="save_ticket")
    async def save_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)
        try:
            channel = interaction.channel
            messages = [m async for m in channel.history(limit=1000)]
            messages.reverse()

            log = "\n".join([f"[{m.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {m.author}: {m.clean_content}" for m in messages])
            filename = f"ticket-{self.user.name}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(log)
            with open(filename, "rb") as f:
                await interaction.followup.send(file=discord.File(f, filename), ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    @discord.ui.button(label="❌ Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket closed. What would you like to do?", view=CloseOptionsView(self.bot, interaction.channel, self.user, self.log_channel_name), ephemeral=True)

class CloseOptionsView(discord.ui.View):
    def __init__(self, bot: commands.Bot, channel: discord.TextChannel, user: discord.User, log_channel_name: str = None):
        super().__init__(timeout=60)
        self.bot = bot
        self.channel = channel
        self.user = user
        self.log_channel_name = log_channel_name

    @discord.ui.button(label="♻ Reopen", style=discord.ButtonStyle.green)
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        perms = self.channel.overwrites_for(self.user)
        perms.view_channel = True
        perms.send_messages = True
        await self.channel.set_permissions(self.user, overwrite=perms)
        await interaction.response.send_message("✅ Ticket reopened.", ephemeral=True)

    @discord.ui.button(label="🗑 Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏳ Deleting in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)
        if self.log_channel_name:
            log_channel = utils.get(interaction.guild.text_channels, name=self.log_channel_name)
            if log_channel:
                await log_channel.send(f"🗑 Ticket `{self.channel.name}` closed and deleted by {interaction.user}.")
        await self.channel.delete()

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("🟢 Ticket Cog is loaded!")

    @app_commands.command(name="ticket", description="Send the ticket panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket(self, interaction: discord.Interaction):
        config = load_config()
        guild_id = str(interaction.guild.id)
        title = config.get(guild_id, {}).get("title", "🎫 Support Ticket")
        desc = config.get(guild_id, {}).get("description", "Click the button to create a ticket.")
        color = discord.Color.green()
        image_url = config.get(guild_id, {}).get("image")

        embed = discord.Embed(title=title, description=desc, color=color)
        if image_url:
            embed.set_image(url=image_url)

        await interaction.channel.send(embed=embed, view=TicketView(self.bot))
        await interaction.response.send_message("✅ Ticket panel sent.", ephemeral=True)

    @app_commands.command(name="ticket_setup", description="Set log channel and customize panel")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_setup(self, interaction: discord.Interaction, log_channel: discord.TextChannel, title: str, description: str, image: str = None):
        config = load_config()
        guild_id = str(interaction.guild.id)
        config[guild_id] = {
            "log_channel": log_channel.name,
            "title": title,
            "description": description,
            "image": image
        }
        save_config(config)
        await interaction.response.send_message("✅ Ticket system configured!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Ticket(bot))
