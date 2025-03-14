import discord
from discord.ext import commands
from deep_translator import GoogleTranslator  # New import

class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_history = {}  # Message history

    @commands.Cog.listener()
    async def on_ready(self):
        print("Translator.py is ready!")

    # Function to translate text
    def translate_text(self, text, target_lang="en"):
        try:
            translated = GoogleTranslator(source="auto", target=target_lang).translate(text)
            return translated
        except Exception as e:
            return f"Translation error: {e}"

    # Auto-translate messages (ignores commands)
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith("!translate"):  # Ignore command
            return

        channel_id = message.channel.id
        if channel_id not in self.message_history:
            self.message_history[channel_id] = []
        
        self.message_history[channel_id].append(message.content)
        if len(self.message_history[channel_id]) > 5:
            self.message_history[channel_id].pop(0)

    # Command to translate specific text
    @commands.command()
    async def translate(self, ctx, lang: str, *, text: str):
        """Translates text into the specified language"""
        translated_text = self.translate_text(text, lang)
        await ctx.send(f"**Translation to {lang}:** {translated_text}")

# Load the Cog
async def setup(bot):
    await bot.add_cog(Translator(bot))