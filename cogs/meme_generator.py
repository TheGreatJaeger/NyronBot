import discord
from discord.ext import commands
import praw
import random
import os
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные из .env

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Настраиваем API Reddit
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

class MemeGenerator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def meme(self, ctx):
        """Sends a random meme from Reddit r/memes"""
        await ctx.send("🔍 **Searching for a meme...**")

        subreddit = reddit.subreddit("memes")
        posts = [post for post in subreddit.hot(limit=50) if not post.stickied]

        if not posts:
            await ctx.send("❌ **Could not find memes, try again later.**")
            return

        random_post = random.choice(posts)

        embed = discord.Embed(title=random_post.title, color=discord.Color.blue())
        embed.set_image(url=random_post.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MemeGenerator(bot))
