import discord
from discord.ext import commands
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

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                await channel.connect()
                await ctx.send(f"🔊 Joined **{channel.name}**")
        else:
            await ctx.send("❌ You are not in a voice channel!")

    @commands.command()
    async def play(self, ctx, *, search: str):
        if not os.path.exists(COOKIES_FILE):
            update_cookies()
        
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("❌ You are not in a voice channel!")
        
        if ctx.voice_client is None:
            vc = await voice_channel.connect()
        else:
            vc = ctx.voice_client
        
        async with ctx.typing():
            try:
                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{search}", download=False)
                    if 'entries' in info:
                        info = info['entries'][0]
                    url = info.get('url')
                    title = info.get('title', 'Unknown Track')
                    
                    self.queue.append((url, title))
                    await ctx.send(f"🎵 Added to queue: **{title}**")
            
            except Exception as e:
                return await ctx.send(f"❌ Error retrieving audio: `{str(e)}`")
        
        if not vc.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if self.queue and ctx.voice_client:
            url, title = self.queue.pop(0)
            try:
                source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(
                    source,
                    after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop)
                )
                await ctx.send(f"▶️ Now playing: **{title}**")
            
            except Exception as e:
                print(f"Playback error: {e}")
                await ctx.send(f"❌ Playback error: `{str(e)}`")
        
        elif ctx.voice_client:
            await ctx.send("📭 Queue is empty. Disconnecting..")
            await ctx.voice_client.disconnect()

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏩ Track Skipped.")
        else:
            await ctx.send("❌ Nothing is playing right now")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("⛔ Bot disconnected.")

async def setup(client):
    await client.add_cog(MusicBot(client))
