import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation.py is ready!")
    #команда clear которая очищает сообщения (доступно только участникам у которых есть права Управлять сообщениями)
    # Команда clear (удаляет сообщения)
    @app_commands.command(name="clear", description="Clear a number of messages in the chat")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, count: int):
        await interaction.channel.purge(limit=count)
        await interaction.response.send_message(f"✅ Deleted {count} messages.", ephemeral=True)

    # Команда kick (кикает участника)
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await interaction.guild.kick(member)

        embed = discord.Embed(title="✅ Member Kicked", color=discord.Color.green())
        embed.add_field(name="User", value=f"{member.mention}", inline=False)
        embed.add_field(name="Kicked by", value=f"{interaction.user.mention}", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)

    # Команда ban (банит участника)
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        await interaction.guild.ban(member)

        embed = discord.Embed(title="⛔ Member Banned", color=discord.Color.red())
        embed.add_field(name="User", value=f"{member.mention}", inline=False)
        embed.add_field(name="Banned by", value=f"{interaction.user.mention}", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)

    # Команда unban (разбанивает участника)
    @app_commands.command(name="unban", description="Unban a user by their ID")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        user = discord.Object(id=int(user_id))
        await interaction.guild.unban(user)

        embed = discord.Embed(title="✅ User Unbanned", color=discord.Color.green())
        embed.add_field(name="User ID", value=f"<@{user_id}>", inline=False)
        embed.add_field(name="Unbanned by", value=f"{interaction.user.mention}", inline=False)

        await interaction.response.send_message(embed=embed)

    # Error handler
    async def error_handler(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠ An error occurred while executing the command.", ephemeral=True)

    @clear.error
    @kick.error
    @ban.error
    @unban.error
    async def command_error(self, interaction: discord.Interaction, error):
        await self.error_handler(interaction, error)

async def setup(client):
    await client.add_cog(Moderation(client))