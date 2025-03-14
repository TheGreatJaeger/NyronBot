import discord
import asyncio
from discord import app_commands, utils
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

class TicketView(discord.ui.View):  # Класс кнопки создания тикета
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎟 Create Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        ticket = utils.get(interaction.guild.text_channels, name=f"ticket-{interaction.user.id}")
        
        if ticket:
            await interaction.response.send_message(f"❗ You already have an open ticket: {ticket.mention}", ephemeral=True)
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
            view=ManageTicketView(self.bot, interaction.user)
        )
        
        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

class ManageTicketView(discord.ui.View):  # Класс кнопок управления тикетом
    def __init__(self, bot: commands.Bot, user: discord.User):
        super().__init__(timeout=None)
        self.bot = bot
        self.user = user

    @discord.ui.button(label="📄 Save Conversation", style=discord.ButtonStyle.green, custom_id="save_ticket")
    async def save_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True)  # Уведомляем, что бот "думает"

        try:
            channel = interaction.channel
            messages = [message async for message in channel.history(limit=1000)]  # Теперь все работает!
            messages.reverse()  # Разворачиваем, чтобы читать в порядке отправки

            log_content = "\n".join([f"[{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {msg.author}: {msg.content}" for msg in messages])
            file_name = f"ticket-{self.user.name}.txt"

            with open(file_name, "w", encoding="utf-8") as file:
                file.write(log_content)

            with open(file_name, "rb") as file:
                await interaction.followup.send("📄 Ticket conversation saved:", file=discord.File(file, file_name), ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Error saving conversation: {e}", ephemeral=True)


    @discord.ui.button(label="❌ Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        await interaction.response.send_message("⏳ Closing ticket in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)
        await channel.delete(reason=f"Ticket closed by {interaction.user}")

class TicketCog(commands.Cog):  # Основной класс КОГа
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"🟢 {__name__} loaded!")

    @app_commands.command(name="ticket", description="Display a button to create a ticket")
    async def ticket_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎫 Support Ticket",
            description="Click the button below to create a ticket.",
            color=discord.Color.green()
        )
        await interaction.channel.send(embed=embed, view=TicketView(self.bot))
        await interaction.response.send_message("✅ Ticket button sent!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
