import discord
import json
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

# Функция для загрузки и сохранения лог-каналов
def load_log_channels():
    try:
        with open("cogs/jsonfiles/config.json", "r") as f:
            return json.load(f)["log_channels"]
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_log_channels(log_channels):
    with open("cogs/jsonfiles/config.json", "w") as f:
        json.dump({"log_channels": log_channels}, f, indent=4)

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.log_channels = load_log_channels()  # Загружаем данные из JSON

    @commands.Cog.listener()
    async def on_ready(self):
        print("Events.py is online.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        log_channel_id = self.log_channels.get(guild_id)

        if log_channel_id:
            log_channel = self.client.get_channel(log_channel_id)
        else:
            log_channel = None

        if not log_channel:
            return  # Если лог-канал не найден, выходим

        event_embed = discord.Embed(
            title="Message Logged",
            description="Message's contents and origin.",
            color=discord.Color.green()
        )
        event_embed.add_field(name="Message Author:", value=message.author.mention, inline=False)
        event_embed.add_field(name="Channel Origin:", value=message.channel.mention, inline=False)
        event_embed.add_field(name="Message Content:", value=message.content or "No content", inline=False)

        await log_channel.send(embed=event_embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setlog(self, ctx, channel: discord.TextChannel):
        """Command to set a log channel"""
        guild_id = str(ctx.guild.id)
        self.log_channels[guild_id] = channel.id
        save_log_channels(self.log_channels)

        await ctx.send(f"✅ Log channel has been set: {channel.mention}")

async def setup(client):
    await client.add_cog(Events(client))
