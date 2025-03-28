import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator

class Translator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_history = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Translator.py is ready!")

    def translate_text(self, text, target_lang="en"):
        try:
            translated = GoogleTranslator(source="auto", target=target_lang).translate(text)
            return translated
        except Exception as e:
            return f"❌ Translation error: {e}"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith("!translate"):
            return

        channel_id = message.channel.id
        if channel_id not in self.message_history:
            self.message_history[channel_id] = []

        self.message_history[channel_id].append(message.content)
        if len(self.message_history[channel_id]) > 5:
            self.message_history[channel_id].pop(0)

    @app_commands.command(name="translate", description="Translates text into the specified language")
    async def translate(self, interaction: discord.Interaction, lang: str, text: str):
        translated = self.translate_text(text, target_lang=lang)
        await interaction.response.send_message(f"🌐 **Translated to `{lang}`:** {translated}", ephemeral=True)

# Load the Cog
async def setup(bot):
    await bot.add_cog(Translator(bot))