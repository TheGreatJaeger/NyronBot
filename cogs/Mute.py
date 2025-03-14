import discord
from discord.ext import commands
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

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setmuterole(self, ctx, role: discord.Role):
        mute_role = self.load_mute_data()
        mute_role[str(ctx.guild.id)] = role.id  # Сохраняем ID вместо имени
        self.save_mute_data(mute_role)

        conf_embed = discord.Embed(title="Success!", color=discord.Color.green())
        conf_embed.add_field(name="Mute role has been set!", 
                             value=f"The mute role has been changed to {role.mention} for this guild.")
        await ctx.send(embed=conf_embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member):
        role_data = self.load_mute_data()
        mute_role = discord.utils.get(ctx.guild.roles, id=role_data.get(str(ctx.guild.id)))

        if not mute_role:
            await ctx.send("Error: Mute role is not set or does not exist!")
            return

        if ctx.guild.me.top_role <= mute_role:
            await ctx.send("Error: I do not have permission to assign this role!")
            return

        await member.add_roles(mute_role)

        conf_embed = discord.Embed(title="Success!", color=discord.Color.green())
        conf_embed.add_field(name="Muted", value=f"{member.mention} has been muted by {ctx.author.mention}.", inline=False)
        await ctx.send(embed=conf_embed)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        role_data = self.load_mute_data()
        mute_role = discord.utils.get(ctx.guild.roles, id=role_data.get(str(ctx.guild.id)))

        if not mute_role:
            await ctx.send("Error: Mute role is not set or does not exist!")
            return

        if mute_role not in member.roles:
            await ctx.send(f"{member.mention} is not muted.")
            return

        await member.remove_roles(mute_role)

        conf_embed = discord.Embed(title="Success!", color=discord.Color.green())
        conf_embed.add_field(name="Unmuted", value=f"{member.mention} has been unmuted by {ctx.author.mention}.", inline=False)
        await ctx.send(embed=conf_embed)

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
