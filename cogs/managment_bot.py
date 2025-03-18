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
    
    # 2. Logging System
    @app_commands.command(name="set_logs_channel", description="Set a channel for logging server events.")
    async def set_logs_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.logs_channel = channel.id
        await interaction.response.send_message(f"✅ Logging channel set to {channel.mention}", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if self.logs_channel:
            channel = self.client.get_channel(self.logs_channel)
            if channel:
                embed = discord.Embed(title="🗑 Deleted Message", description=f"{message.content}", color=discord.Color.red())
                embed.set_footer(text=f"Deleted by {message.author}")
                await channel.send(embed=embed)
    
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
    
    # 5. Mute System
    @app_commands.command(name="mute", description="Mute a user for a specific duration.")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int):
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await interaction.guild.create_role(name="Muted")
            for channel in interaction.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
        await member.add_roles(mute_role)
        await interaction.response.send_message(f"🔇 {member.mention} has been muted for {duration} minutes.")
        await asyncio.sleep(duration * 60)
        await member.remove_roles(mute_role)
        await interaction.channel.send(f"✅ {member.mention} is now unmuted.")
    
    # 6. Kick User
    @app_commands.command(name="kick", description="Kick a user from the server.")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 {member.mention} has been kicked. Reason: {reason}")
    
    # 7. Ban User
    @app_commands.command(name="ban", description="Ban a user from the server.")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"⛔ {member.mention} has been banned. Reason: {reason}")
    
    # 8. Unban User
    @app_commands.command(name="unban", description="Unban a previously banned user.")
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        banned_users = await interaction.guild.bans()
        for ban_entry in banned_users:
            if ban_entry.user.id == user.id:
                await interaction.guild.unban(user)
                await interaction.response.send_message(f"✅ {user.mention} has been unbanned.")
                return
        await interaction.response.send_message("❌ User not found in ban list.")
    # 9. Reminders
    @app_commands.command(name="set_reminder", description="Set a reminder.")
    async def set_reminder(self, interaction: discord.Interaction, time_in_minutes: int, message: str):
        await interaction.response.send_message(f"⏰ Reminder set for {time_in_minutes} minutes!", ephemeral=True)
        await asyncio.sleep(time_in_minutes * 60)
        await interaction.user.send(f"⏰ Reminder: {message}")
    
    async def setup(self, client: commands.Bot):
        client.tree.add_command(self.set_auto_role)
        client.tree.add_command(self.set_logs_channel)
        client.tree.add_command(self.clear_chat)
        client.tree.add_command(self.add_auto_response)
        client.tree.add_command(self.mute)
        client.tree.add_command(self.kick)
        client.tree.add_command(self.ban)
        client.tree.add_command(self.unban)
        client.tree.add_command(self.set_reminder)

async def setup(client: commands.Bot):
    await client.add_cog(ServerAutomation(client))