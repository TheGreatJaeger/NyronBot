import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
import os
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
load_dotenv(".env")


COOKIES_FILE = "cookies.txt"
LOGIN_URL = "https://accounts.google.com/signin"
YOUTUBE_URL = "https://www.youtube.com"
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


def update_cookies():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(LOGIN_URL)
        time.sleep(2)
        
        email_input = driver.find_element(By.ID, "identifierId")
        email_input.send_keys(EMAIL)
        email_input.send_keys(Keys.RETURN)
        time.sleep(3)
        
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)
        
        driver.get(YOUTUBE_URL)
        time.sleep(3)
        
        cookies = driver.get_cookies()
        with open(COOKIES_FILE, "w") as file:
            file.write(json.dumps(cookies))
        print("✅ Cookies обновлены!")
    
    finally:
        driver.quit()


if not os.path.exists(COOKIES_FILE):
    update_cookies()

# Настройки yt-dlp
FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch',
    'quiet': False,
    'geo_bypass': True,
    'nocheckcertificate': True,
    'source_address': '0.0.0.0',
    'cookiefile': COOKIES_FILE,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.youtube.com/',
    }
}

class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"✅ {self.__class__.__name__} is ready!")

    @app_commands.command(name="join", description="Bot joins the voice channel")
    async def join(self, interaction: discord.Interaction):
        """Bot joins the user's voice channel"""
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            if interaction.guild.voice_client is None:
                await channel.connect()
                await interaction.response.send_message(f"🔊 Joined **{channel.name}**")
            else:
                await interaction.response.send_message("❌ I'm already connected to a voice channel.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You are not in a voice channel!", ephemeral=True)

    @app_commands.command(name="play", description="Plays a song from YouTube")
    async def play(self, interaction: discord.Interaction, search: str):
        """Play music from YouTube"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You are not in a voice channel!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            vc = await voice_channel.connect()
        else:
            vc = interaction.guild.voice_client

        await interaction.response.defer()  # Уведомляем Discord, что бот обрабатывает команду

        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                url = info.get('url')
                title = info.get('title', 'Unknown Track')

                self.queue.append((url, title))
                await interaction.followup.send(f"🎵 Added to queue: **{title}**")
        
        except Exception as e:
            return await interaction.followup.send(f"❌ Error retrieving audio: `{str(e)}`")

        if not vc.is_playing():
            await self.play_next(interaction)

    async def play_next(self, interaction):
        """Plays the next song in the queue"""
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

    @app_commands.command(name="skip", description="Skips the current song")
    async def skip(self, interaction: discord.Interaction):
        """Skip the currently playing song"""
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏩ Track Skipped.")
        else:
            await interaction.response.send_message("❌ Nothing is playing right now", ephemeral=True)

    @app_commands.command(name="stop", description="Stops the music and leaves the channel")
    async def stop(self, interaction: discord.Interaction):
        """Stop playing and leave the voice channel"""
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("⛔ Bot disconnected.")
        else:
            await interaction.response.send_message("❌ I'm not in a voice channel!", ephemeral=True)

async def setup(client):
    await client.add_cog(MusicBot(client))
