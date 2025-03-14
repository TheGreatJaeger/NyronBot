import discord
import asyncio
import random
import json
import os
from discord.ext import commands
from discord.ui import View, Button

PET_FILE = "pets.json"

class VirtualPet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_pets()
    @commands.Cog.listener()
    async def on_ready(self):
        print("Pets.py is ready!")

    def load_pets(self):
        """ Loads the pet database """
        if os.path.exists(PET_FILE):
            with open(PET_FILE, "r", encoding="utf-8") as f:
                self.pets = json.load(f)
        else:
            self.pets = {}

    def save_pets(self):
        """ Saves the pet database """
        with open(PET_FILE, "w", encoding="utf-8") as f:
            json.dump(self.pets, f, indent=4, ensure_ascii=False)

    def get_pet(self, user_id):
        """ Retrieves a user's pet data """
        return self.pets.get(str(user_id), None)

    async def cooldown_message(self, ctx):
        retry_after = ctx.command.get_cooldown_retry_after(ctx)
        await ctx.send(f"⏳ {ctx.author.mention}, you need to wait {int(retry_after)} seconds before using this command again!")
        
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def pet_create(self, ctx, name: str):
        """ Creates a new pet """
        user_id = str(ctx.author.id)
        if user_id in self.pets:
            await ctx.send("You already have a pet!")
            return
        
        self.pets[user_id] = {
            "name": name,
            "hunger": 50,
            "happiness": 50,
            "level": 1,
            "experience": 0,
            "health": 100,
            "attack": 10
        }
        self.save_pets()
        await ctx.send(f"🎉 {ctx.author.mention}, you have created a pet named {name}!")
        
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def pet_stats(self, ctx):
        """ Shows pet statistics """
        pet = self.get_pet(ctx.author.id)
        if not pet:
            await ctx.send("You don't have a pet yet! Use `!pet_create <name>`.")
            return
        
        stats = (f"📊 **{pet['name']}'s Stats**\n"
                 f"🍗 Hunger: {pet['hunger']}\n"
                 f"😊 Happiness: {pet['happiness']}\n"
                 f"❤️ Health: {pet['health']}\n"
                 f"⚔️ Attack: {pet['attack']}\n"
                 f"⭐ Level: {pet['level']}\n"
                 f"🎖 Experience: {pet['experience']}")
        await ctx.send(stats)
    
    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command()
    async def pet_feed(self, ctx):
        """ Feeds the pet """
        pet = self.get_pet(ctx.author.id)
        if not pet:
            await ctx.send("You don't have a pet yet! Use `!pet_create <name>`.")
            return
        
        pet['hunger'] = min(pet['hunger'] + 20, 100)
        self.save_pets()
        await ctx.send(f"🍗 {ctx.author.mention} fed {pet['name']}! Hunger: {pet['hunger']}.")
        
    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command()
    async def pet_train(self, ctx):
        """ Trains the pet """
        pet = self.get_pet(ctx.author.id)
        if not pet:
            await ctx.send("You don't have a pet yet! Use `!pet_create <name>`.")
            return
        
        pet['attack'] += 5
        pet['health'] += 10
        self.save_pets()
        await ctx.send(f"💪 {ctx.author.mention} trained {pet['name']}! Attack: {pet['attack']}, Health: {pet['health']}.")
    
    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command()
    async def pet_cuddle(self, ctx):
        """ Increases pet happiness """
        pet = self.get_pet(ctx.author.id)
        if not pet:
            await ctx.send("You don't have a pet yet! Use `!pet_create <name>`.")
            return
        
        pet['happiness'] = min(pet['happiness'] + 15, 100)
        self.save_pets()
        await ctx.send(f"💖 {ctx.author.mention} cuddled {pet['name']}! Happiness: {pet['happiness']}.")
        
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def pet_delete(self, ctx):
        """ Deletes a pet """
        user_id = str(ctx.author.id)
        if user_id not in self.pets:
            await ctx.send("You don't have a pet to delete!")
            return
        
        del self.pets[user_id]
        self.save_pets()
        await ctx.send(f"❌ {ctx.author.mention}, your pet has been deleted!")
    
    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command()
    async def pet_battle(self, ctx, opponent: discord.Member):
        """ Starts a battle between two pets if both users agree """
        user_id = str(ctx.author.id)
        opponent_id = str(opponent.id)

        if user_id not in self.pets or opponent_id not in self.pets:
            await ctx.send("Both players must have a pet to battle!")
            return

        user_pet = self.pets[user_id]
        opponent_pet = self.pets[opponent_id]

        class BattleConfirmation(View):
            def __init__(self, cog, ctx, opponent):
                super().__init__(timeout=30)
                self.cog = cog
                self.ctx = ctx
                self.opponent = opponent
                self.user_accepted = False
                self.opponent_accepted = False

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                return interaction.user.id in [self.ctx.author.id, self.opponent.id]

            @discord.ui.button(label="Accept Battle", style=discord.ButtonStyle.green)
            async def accept(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id == self.ctx.author.id:
                    self.user_accepted = True
                elif interaction.user.id == self.opponent.id:
                    self.opponent_accepted = True
                await interaction.response.send_message(f"{interaction.user.mention} accepted the battle!", ephemeral=True)
                if self.user_accepted and self.opponent_accepted:
                    self.stop()

            @discord.ui.button(label="Decline Battle", style=discord.ButtonStyle.red)
            async def decline(self, interaction: discord.Interaction, button: Button):
                await interaction.response.send_message(f"{interaction.user.mention} declined the battle.", ephemeral=True)
                await self.ctx.send("Battle request was declined.")
                self.stop()

        view = BattleConfirmation(self, ctx, opponent)
        await ctx.send(f"⚔️ {ctx.author.mention} has challenged {opponent.mention} to a pet battle! {opponent.mention}, do you accept?", view=view)
        await view.wait()

        if not (view.user_accepted and view.opponent_accepted):
            await ctx.send("Battle canceled.")
            return

        await ctx.send(f"⚔️ **{user_pet['name']} vs {opponent_pet['name']}!** ⚔️")
        user_hp = user_pet["health"]
        opponent_hp = opponent_pet["health"]

        while user_hp > 0 and opponent_hp > 0:
            user_damage = random.randint(5, user_pet["attack"])
            opponent_damage = random.randint(5, opponent_pet["attack"])

            opponent_hp -= user_damage
            user_hp -= opponent_damage

            await ctx.send(f"🔥 {user_pet['name']} deals {user_damage} damage! {opponent_pet['name']} HP: {max(opponent_hp, 0)}")
            await ctx.send(f"💥 {opponent_pet['name']} deals {opponent_damage} damage! {user_pet['name']} HP: {max(user_hp, 0)}")

            await asyncio.sleep(2)

        if user_hp > 0:
            await ctx.send(f"🏆 {user_pet['name']} wins the battle!")
            self.pets[user_id]["experience"] += 30
        else:
            await ctx.send(f"🏆 {opponent_pet['name']} wins the battle!")
            self.pets[opponent_id]["experience"] += 30

        self.save_pets()
    
    @pet_create.error
    @pet_stats.error
    @pet_feed.error
    @pet_train.error
    @pet_cuddle.error
    @pet_battle.error
    @pet_delete.error
    async def command_cooldown_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await self.cooldown_message(ctx)

async def setup(bot):
    await bot.add_cog(VirtualPet(bot))
