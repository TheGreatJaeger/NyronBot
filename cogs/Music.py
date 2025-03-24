import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

FFMPEG_OPTIONS = {'options': '-vn'}

class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ {self.__class__.__name__} is ready!")

    @app_commands.command(name="join", description="Bot joins the voice channel")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client is None:
                await channel.connect()
                await interaction.response.send_message(f"🔊 Joined **{channel.name}**")
            else:
                await interaction.response.send_message("❌ I'm already connected to a voice channel.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You are not in a voice channel!", ephemeral=True)

    @app_commands.command(name="play", description="Plays a song from Spotify or SoundCloud")
    @app_commands.describe(
        search="Search query or link",
        source="Choose a platform"
    )
    @app_commands.choices(source=[
        app_commands.Choice(name="SoundCloud", value="scsearch"),
        app_commands.Choice(name="Spotify", value="ytsearch")  # Spotify через YouTube
    ])
    async def play(self, interaction: discord.Interaction, search: str, source: app_commands.Choice[str]):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You are not in a voice channel!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            vc = await voice_channel.connect()
        else:
            vc = interaction.guild.voice_client

        await interaction.response.defer()

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': source.value,
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"{search}", download=False)
                if 'entries' in info:
                    info = info['entries'][0]

                # Найдем подходящий аудиоформат
                audio_url = None
                for fmt in info.get("formats", []):
                    if fmt.get("vcodec") == "none":
                        audio_url = fmt.get("url")
                        break

                if not audio_url:
                    raise Exception("No playable audio format found.")

                title = info.get('title', 'Unknown Track')
                self.queue.append((audio_url, title))
                await interaction.followup.send(f"🎵 Added to queue: **{title}**")

        except Exception as e:
            return await interaction.followup.send(f"❌ Error retrieving audio: `{str(e)}`")

        if not vc.is_playing():
            await self.play_next(interaction)

    async def play_next(self, interaction):
        vc = interaction.guild.voice_client
        if self.queue and vc:
            url, title = self.queue.pop(0)
            try:
                source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
                vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.client.loop))
                await interaction.followup.send(f"▶️ Now playing: **{title}**")
            except Exception as e:
                print(f"Playback error: {e}")
                await interaction.followup.send(f"❌ Playback error: `{str(e)}`")
        elif vc:
            await interaction.followup.send("📭 Queue is empty. Disconnecting..")
            await vc.disconnect()

    @app_commands.command(name="stop", description="Stops the music and leaves the channel")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("⛔ Bot disconnected.")
        else:
            await interaction.response.send_message("❌ I'm not in a voice channel!", ephemeral=True)

async def setup(client):
    await client.add_cog(MusicBot(client))