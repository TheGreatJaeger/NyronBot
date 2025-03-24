import discord
from discord.ext import commands, tasks
from discord import app_commands
from itertools import cycle
import os
import asyncio
import json
import random
from dotenv import load_dotenv
load_dotenv(".env")
TOKEN: str = os.getenv("TOKEN")

def get_server_prefix(client, message):
    with open("cogs/jsonfiles/prefixes.json", "r") as f:
        prefix = json.load(f)
    
    return prefix.get(str(message.guild.id), '!')

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

client = commands.Bot(command_prefix=get_server_prefix, intents=intents)  # Creates prefix for bot

@client.event
async def on_guild_join(guild):
    with open("cogs/jsonfiles/prefixes.json", "r") as f:
        prefix = json.load(f)

    prefix[str(guild.id)] = "!"

    with open("cogs/jsonfiles/prefixes.json", "w") as f:
        json.dump(prefix, f, indent=4)

@client.event
async def on_guild_remove(guild):
    with open("cogs/jsonfiles/prefixes.json", "r") as f:
        prefix = json.load(f)

    prefix.pop(str(guild.id))

    with open("cogs/jsonfiles/prefixes.json", "w") as f:
        json.dump(prefix, f, indent=4)

@app_commands.command(name="setprefix", description="Set a custom prefix for this server.")
async def setprefix(interaction: discord.Interaction, newprefix: str):
    with open("cogs/jsonfiles/prefixes.json", "r") as f:
        prefix = json.load(f)

    prefix[str(interaction.guild.id)] = newprefix

    with open("cogs/jsonfiles/prefixes.json", "w") as f:
        json.dump(prefix, f, indent=4)
    
    await interaction.response.send_message(f"✅ Prefix changed to `{newprefix}`", ephemeral=True)

client.tree.add_command(setprefix)

#Context Menu
@client.tree.context_menu(name="Quick info")
async def quick_info(interaction: discord.Interaction, member: discord.Member):
    info_embed = discord.Embed(title=f"{member.name}'s Quick information", description="All quick information about this Discord user.", color=member.color)
    info_embed.add_field(name="Name:", value=member.name, inline=False)
    info_embed.add_field(name="ID:", value=member.id, inline=False)
    info_embed.add_field(name="Activity:", value=member.activity, inline=False)
    info_embed.add_field(name="Created At:", value=member.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
    info_embed.set_thumbnail(url=member.avatar)

    await interaction.response.send_message(embed=info_embed, ephemeral=True)

@client.tree.context_menu(name="Kick")
async def quick_info(interaction: discord.Interaction, member: discord.Member):
    # checking if user has administrator permission.
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permissions to use this command!", ephemeral=True)
        return

    # Kicking user from the server
    await interaction.guild.kick(member)
    await interaction.response.send_message(f"Successfully kicked {member.mention} from the server!", ephemeral=False)

# слэш команды / slash commands
@client.tree.command(name="ping", description="Shows the bot's latency in milliseconds")
async def ping(interaction: discord.Interaction):
    bot_latency = round(client.latency * 1000)
    await interaction.response.send_message(f"Bot's latency: {bot_latency} ms.")

# userinfo command
@client.command()
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    info_embed = discord.Embed(title=f"{member.name}'s User Information", description="All information about this user", color=member.color)
    info_embed.set_thumbnail(url=member.avatar)
    info_embed.add_field(name="Name:", value=member.name, inline=False)
    info_embed.add_field(name="Nick Name:", value=member.display_name, inline=False)
    info_embed.add_field(name="Discriminator:", value=member.discriminator, inline=False)
    info_embed.add_field(name="ID:", value=member.id, inline=False)
    info_embed.add_field(name="Top Role:", value=member.top_role, inline=False)
    info_embed.add_field(name="Status:", value=member.status, inline=False)
    info_embed.add_field(name="Bot User?:", value=member.bot, inline=False)
    info_embed.add_field(name="Creation Date:", value=member.created_at.__format__("%A, %d. %B %Y @ %H:%M:%S"), inline=False)

    await ctx.send(embed=info_embed)

@client.event
async def on_guild_join(guild):
    with open("cogs/jsonfiles/mutes.json", "r") as f:
        mute_role = json.load(f)

        mute_role[str(guild.id)] = None

    with open("cogs/jsonfiles/mutes.json", "w") as f:
        json.dump(mute_role, f, indent=4)

@client.event
async def on_guild_remove(guild):
    with open("cogs/jsonfiles/mutes.json", "r") as f:
        mute_role = json.load(f)

        mute_role.pop(str(guild.id))

    with open("cogs/jsonfiles/mutes.json", "w") as f:
        json.dump(mute_role, f, indent=4)

#on_ready function that will show if the bot is ready or not
@client.event
async def on_ready():
    await client.tree.sync()
    print("Success: Bot is Connected to Discord")
    
    activity = discord.Game(name="/help | discord.gg/CaCebqQxYs")
    await client.change_presence(status=discord.Status.online, activity=activity)
    
async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")

#welcome system

@client.event
async def on_guild_join(guild):
    with open("cogs/jsonfiles/welcome.json", "r") as f:
        data = json.load(f)

    data[str(guild.id)] = {}
    data[str(guild.id)]["Channel"] = None
    data[str(guild.id)]["Message"] = None
    data[str(guild.id)]["AutoRole"] = None
    data[str(guild.id)]["ImageUrl"] = None

    with open("cogs/jsonfiles/welcome.json", "w") as f:
        json.dump(data, f, indent=4)

@client.event
async def on_guild_remove(guild):
    with open("cogs/jsonfiles/welcome.json", "r") as f:
        data = json.load(f)

    data.pop(str(guild.id))

    with open("cogs/jsonfiles/welcome.json", "w") as f:
        json.dump(data, f, indent=4)

# command that runs the bot
async def main():
    async with client:
        await load()
        await client.start(TOKEN)

asyncio.run(main())



'''Selection Menu
class SelectMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Персистентный View

    @discord.ui.select(
        placeholder="Select Color",
        options=[
            discord.SelectOption(label="Red", value="1", description="Gives the color red to user."),
            discord.SelectOption(label="Blue", value="2", description="Gives the color blue to user."),
            discord.SelectOption(label="Yellow", value="3", description="Gives the color yellow to user.")
        ],
        custom_id="color_select"
    )
    async def menu_callback(self, interaction: discord.Interaction, select_interaction: discord.ui.Select):
        guild = interaction.guild
        member = interaction.user
        
        role_names = {"1": "Red", "2": "Blue", "3": "Yellow"}
        selected_role_name = role_names.get(select_interaction.values[0])

        if selected_role_name:
            role = discord.utils.get(guild.roles, name=selected_role_name)
            if role:
                color_roles = [discord.utils.get(guild.roles, name=r) for r in role_names.values()]
                await member.remove_roles(*[r for r in color_roles if r and r in member.roles])

                await member.add_roles(role)
                await interaction.response.send_message(content=f"Your color is now {selected_role_name}.", ephemeral=True)
            else:
                await interaction.response.send_message(content="Role not found. Please contact an administrator.", ephemeral=True)
        else:
            await interaction.response.send_message(content="Invalid selection.", ephemeral=True)

@client.tree.command(name="setcolor", description="Sets your color of choice.")
async def setcolor(interaction: discord.Interaction):
    await interaction.response.send_message(content="Select your role color", view=SelectMenu(), ephemeral=True)'''