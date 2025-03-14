import discord
from discord.ext import commands
import json

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

class welcome(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("welcome.py is ready!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open("cogs/jsonfiles/welcome.json", "r") as f:
            data = json.load(f)

        welcome_embed = discord.Embed(
            title=f"Welcome to {member.guild.name}!", 
            description=f"Welcome to the server, {member.mention}! You are member number {member.guild.member_count}!", 
            color=discord.Color.purple()
        )

        welcome_embed.add_field(name="Welcome to the server!", value=data[str(member.guild.id)]["Message"], inline=False)
        welcome_embed.set_image(url=data[str(member.guild.id)]["ImageUrl"])
        welcome_embed.set_footer(text="Glad you've joined!", icon_url=member.avatar)

        auto_role = discord.utils.get(member.guild.roles, name=data[str(member.guild.id)]["AutoRole"])

        await member.add_roles(auto_role)

        if data[str(member.guild.id)]["Channel"] is None:
            await member.send(embed=welcome_embed)
        else:
            welcome_channel = discord.utils.get(member.guild.channels, name=data[str(member.guild.id)]["Channel"])
            await welcome_channel.send(f"{member.mention}", embed=welcome_embed)

    @commands.group(name="welcome", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        info_embed = discord.Embed(
            title="welcome System Setup", 
            description="Create a custom welcome system for your discord server!", 
            color=discord.Color.teal()
        )
        info_embed.add_field(name="autorole", value="Set and automatic role so when a users join they will receive it.", inline=False)
        info_embed.add_field(name="message", value="Set a message to be included in your welcome card.", inline=False)
        info_embed.add_field(name="channel", value="Set a channel for your welcome card to be sent in. (if you didn't set a channel then it's going to send a message in dm)", inline=False)
        info_embed.add_field(name="img", value="Set a image or gif url to be sent with the welcome card.", inline=False)

        await ctx.send(embed=info_embed)
    
    @welcome.command()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, role: discord.Role):
        with open("cogs/jsonfiles/welcome.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)]["AutoRole"] = str(role.name)

        with open("cogs/jsonfiles/welcome.json", "w") as f:
            json.dump(data, f, indent=4)
            
    @welcome.command()
    @commands.has_permissions(administrator=True)
    async def message(self, ctx, *, msg):
        with open("cogs/jsonfiles/welcome.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)]["Message"] = str(msg)

        with open("cogs/jsonfiles/welcome.json", "w") as f:
            json.dump(data, f, indent=4)

    @welcome.command()
    @commands.has_permissions(administrator=True)
    async def channel(self, ctx, channel: discord.TextChannel):
        with open("cogs/jsonfiles/welcome.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)]["Channel"] = str(channel.name)

        with open("cogs/jsonfiles/welcome.json", "w") as f:
            json.dump(data, f, indent=4)

    @welcome.command()
    @commands.has_permissions(administrator=True)
    async def img(self, ctx, *, url):
        with open("cogs/jsonfiles/welcome.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)]["ImageUrl"] = str(url)

        with open("cogs/jsonfiles/welcome.json", "w") as f:
            json.dump(data, f, indent=4)

async def setup(client):
    await client.add_cog(welcome(client))
