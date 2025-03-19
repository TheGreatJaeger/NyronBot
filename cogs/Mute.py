import discord
from discord.ext import commands
from discord import app_commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

class Mute(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Mute.py is ready!")

    def load_mute_data(self):
        """Загружает JSON файл и обрабатывает ошибки"""
        if not os.path.exists("cogs/jsonfiles/mutes.json"):
            return {}
        try:
            with open("cogs/jsonfiles/mutes.json", "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save_mute_data(self, data):
        """Сохраняет данные в JSON"""
        with open("cogs/jsonfiles/mutes.json", "w") as f:
            json.dump(data, f, indent=4)

    @app_commands.command(name="setmuterole", description="Set the mute role for the server")
    @app_commands.checks.has_permissions(administrator=True)
    async def setmuterole(self, interaction: discord.Interaction, role: discord.Role):
        """Command to set the mute role"""
        mute_roles = self.load_mute_data()
        mute_roles[str(interaction.guild.id)] = role.id  # Save role ID instead of name
        self.save_mute_data(mute_roles)

        embed = discord.Embed(title="✅ Success!", color=discord.Color.green())
        embed.add_field(name="Mute Role Set", value=f"The mute role has been changed to {role.mention}.")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="mute", description="Mute a user")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member):
        """Mute a user"""
        role_data = self.load_mute_data()
        mute_role = discord.utils.get(interaction.guild.roles, id=role_data.get(str(interaction.guild.id)))

        if not mute_role:
            await interaction.response.send_message("❌ Error: Mute role is not set or does not exist!", ephemeral=True)
            return

        if interaction.guild.me.top_role <= mute_role:
            await interaction.response.send_message("❌ Error: I do not have permission to assign this role!", ephemeral=True)
            return

        await member.add_roles(mute_role)

        embed = discord.Embed(title="✅ Success!", color=discord.Color.green())
        embed.add_field(name="Muted", value=f"{member.mention} has been muted by {interaction.user.mention}.", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unmute", description="Unmute a user")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        """Unmute a user"""
        role_data = self.load_mute_data()
        mute_role = discord.utils.get(interaction.guild.roles, id=role_data.get(str(interaction.guild.id)))

        if not mute_role:
            await interaction.response.send_message("❌ Error: Mute role is not set or does not exist!", ephemeral=True)
            return

        if mute_role not in member.roles:
            await interaction.response.send_message(f"❌ {member.mention} is not muted.", ephemeral=True)
            return

        await member.remove_roles(mute_role)

        embed = discord.Embed(title="✅ Success!", color=discord.Color.green())
        embed.add_field(name="Unmuted", value=f"{member.mention} has been unmuted by {interaction.user.mention}.", inline=False)

        await interaction.response.send_message(embed=embed)

    # Error handlers
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Error: You must mention a user to mute!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Error: You do not have permission to use this command!")

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Error: You must mention a user to unmute!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Error: You do not have permission to use this command!")

async def setup(client):
    await client.add_cog(Mute(client))
