import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import datetime

class ServerAutomation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.logs_channel = None
        self.auto_roles = {}
        self.auto_responses = {}
        self.reminders = {}
        self.anti_spam = {}
        self.moderation_logs = {}
    
    # 1. Auto Role Assignment
    @app_commands.command(name="set_auto_role", description="Set an automatic role for new members.")
    async def set_auto_role(self, interaction: discord.Interaction, role: discord.Role):
        self.auto_roles[interaction.guild.id] = role.id
        await interaction.response.send_message(f"✅ Auto role set to {role.name}", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id in self.auto_roles:
            role = member.guild.get_role(self.auto_roles[member.guild.id])
            if role:
                await member.add_roles(role)
                log_channel = discord.utils.get(member.guild.text_channels, name="logs")
                if log_channel:
                    await log_channel.send(f"🎉 {member.mention} joined and received role {role.name}!")
                    
    # 3. Auto Chat Cleanup
    @app_commands.command(name="clear_chat", description="Clear messages in a channel.")
    async def clear_chat(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Deleted {amount} messages", ephemeral=True)
    
    # 4. Auto Responses
    @app_commands.command(name="add_auto_response", description="Set up an auto-response for a phrase.")
    async def add_auto_response(self, interaction: discord.Interaction, trigger: str, response: str):
        self.auto_responses[trigger.lower()] = response
        await interaction.response.send_message(f"✅ Added auto-response: `{trigger}` → `{response}`", ephemeral=True)
    
    # 9. Reminders
    @app_commands.command(name="set_reminder", description="Set a reminder.")
    async def set_reminder(self, interaction: discord.Interaction, time_in_minutes: int, message: str):
        await interaction.response.send_message(f"⏰ Reminder set for {time_in_minutes} minutes!", ephemeral=True)
        await asyncio.sleep(time_in_minutes * 60)
        await interaction.user.send(f"⏰ Reminder: {message}")
    
    async def setup(self, client: commands.Bot):
        client.tree.add_command(self.set_auto_role)
        client.tree.add_command(self.clear_chat)
        client.tree.add_command(self.add_auto_response)
        client.tree.add_command(self.set_reminder)

async def setup(client: commands.Bot):
    await client.add_cog(ServerAutomation(client))