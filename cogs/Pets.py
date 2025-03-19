import discord
import asyncio
import random
import json
import os
from discord.ext import commands
from discord import app_commands
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

    @app_commands.command(name="pet_create", description="Create a new virtual pet")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    async def pet_create(self, interaction: discord.Interaction, name: str):
        """ Creates a new pet """
        user_id = str(interaction.user.id)
        if user_id in self.pets:
            await interaction.response.send_message("You already have a pet!", ephemeral=True)
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
        await interaction.response.send_message(f"🎉 {interaction.user.mention}, you have created a pet named {name}!")

    @app_commands.command(name="pet_stats", description="Show your pet's statistics")
    async def pet_stats(self, interaction: discord.Interaction):
        """ Shows pet statistics """
        pet = self.get_pet(interaction.user.id)
        if not pet:
            await interaction.response.send_message("You don't have a pet yet! Use `/pet_create <name>`.", ephemeral=True)
            return
        
        embed = discord.Embed(title=f"📊 {pet['name']}'s Stats", color=discord.Color.green())
        embed.add_field(name="🍗 Hunger", value=pet["hunger"])
        embed.add_field(name="😊 Happiness", value=pet["happiness"])
        embed.add_field(name="❤️ Health", value=pet["health"])
        embed.add_field(name="⚔️ Attack", value=pet["attack"])
        embed.add_field(name="⭐ Level", value=pet["level"])
        embed.add_field(name="🎖 Experience", value=pet["experience"])
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pet_battle", description="Battle your pet against another player's pet")
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.user.id))
    async def pet_battle(self, interaction: discord.Interaction, opponent: discord.Member):
        """ Starts a battle between two pets if both users agree """
        user_id = str(interaction.user.id)
        opponent_id = str(opponent.id)

        if user_id not in self.pets or opponent_id not in self.pets:
            await interaction.response.send_message("❌ Both players must have a pet to battle!", ephemeral=True)
            return

        user_pet = self.pets[user_id]
        opponent_pet = self.pets[opponent_id]

        class BattleConfirmation(View):
            def __init__(self, cog, interaction, opponent):
                super().__init__(timeout=30)
                self.cog = cog
                self.interaction = interaction
                self.opponent = opponent
                self.user_accepted = False
                self.opponent_accepted = False

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                return interaction.user.id in [self.interaction.user.id, self.opponent.id]

            @discord.ui.button(label="Accept Battle", style=discord.ButtonStyle.green)
            async def accept(self, interaction: discord.Interaction, button: Button):
                if interaction.user.id == self.interaction.user.id:
                    self.user_accepted = True
                elif interaction.user.id == self.opponent.id:
                    self.opponent_accepted = True
                await interaction.response.send_message(f"{interaction.user.mention} accepted the battle!", ephemeral=True)
                if self.user_accepted and self.opponent_accepted:
                    self.stop()

            @discord.ui.button(label="Decline Battle", style=discord.ButtonStyle.red)
            async def decline(self, interaction: discord.Interaction, button: Button):
                await interaction.response.send_message(f"{interaction.user.mention} declined the battle.", ephemeral=True)
                await self.interaction.followup.send("Battle request was declined.")
                self.stop()

        view = BattleConfirmation(self, interaction, opponent)
        await interaction.response.send_message(
            f"⚔️ {interaction.user.mention} has challenged {opponent.mention} to a pet battle! {opponent.mention}, do you accept?",
            view=view
        )
        await view.wait()

        if not (view.user_accepted and view.opponent_accepted):
            await interaction.followup.send("Battle canceled.")
            return

        battle_message = await interaction.followup.send(f"⚔️ **{user_pet['name']} vs {opponent_pet['name']}!** ⚔️\n\n🔄 Battle starting...", wait=True)

        user_hp = user_pet["health"]
        opponent_hp = opponent_pet["health"]

        while user_hp > 0 and opponent_hp > 0:
            user_damage = random.randint(5, user_pet["attack"])
            opponent_damage = random.randint(5, opponent_pet["attack"])

            opponent_hp -= user_damage
            user_hp -= opponent_damage

            battle_text = (
                f"⚔️ **{user_pet['name']} vs {opponent_pet['name']}** ⚔️\n"
                f"🔥 {user_pet['name']} deals **{user_damage}** damage! {opponent_pet['name']} HP: **{max(opponent_hp, 0)}**\n"
                f"💥 {opponent_pet['name']} deals **{opponent_damage}** damage! {user_pet['name']} HP: **{max(user_hp, 0)}**"
            )

            await battle_message.edit(content=battle_text)
            await asyncio.sleep(2)

        if user_hp > 0:
            result_text = f"🏆 {user_pet['name']} **wins the battle!** 🎉"
            self.pets[user_id]["experience"] += 30
        else:
            result_text = f"🏆 {opponent_pet['name']} **wins the battle!** 🎉"
            self.pets[opponent_id]["experience"] += 30

        self.save_pets()
        await battle_message.edit(content=f"{battle_text}\n\n{result_text}")

    async def cooldown_message(self, interaction: discord.Interaction):
        """Handles cooldown messages"""
        retry_after = interaction.command.get_cooldown_retry_after(interaction)
        await interaction.response.send_message(
            f"⏳ {interaction.user.mention}, you need to wait {int(retry_after)} seconds before using this command again!", 
            ephemeral=True
        )

    @app_commands.command(name="pet_feed", description="Feed your pet")
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.user.id))
    async def pet_feed(self, interaction: discord.Interaction):
        """ Feeds the pet """
        pet = self.get_pet(interaction.user.id)
        if not pet:
            await interaction.response.send_message("You don't have a pet yet! Use `/pet_create <name>`.", ephemeral=True)
            return
        
        pet['hunger'] = min(pet['hunger'] + 20, 100)
        self.save_pets()
        await interaction.response.send_message(f"🍗 {interaction.user.mention} fed {pet['name']}! Hunger: {pet['hunger']}.")

    @app_commands.command(name="pet_train", description="Train your pet")
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.user.id))
    async def pet_train(self, interaction: discord.Interaction):
        """ Trains the pet """
        pet = self.get_pet(interaction.user.id)
        if not pet:
            await interaction.response.send_message("You don't have a pet yet! Use `/pet_create <name>`.", ephemeral=True)
            return
        
        pet['attack'] += 5
        pet['health'] += 10
        self.save_pets()
        await interaction.response.send_message(f"💪 {interaction.user.mention} trained {pet['name']}! Attack: {pet['attack']}, Health: {pet['health']}.")

    @app_commands.command(name="pet_cuddle", description="Increase your pet's happiness")
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.user.id))
    async def pet_cuddle(self, interaction: discord.Interaction):
        """ Increases pet happiness """
        pet = self.get_pet(interaction.user.id)
        if not pet:
            await interaction.response.send_message("You don't have a pet yet! Use `/pet_create <name>`.", ephemeral=True)
            return
        
        pet['happiness'] = min(pet['happiness'] + 15, 100)
        self.save_pets()
        await interaction.response.send_message(f"💖 {interaction.user.mention} cuddled {pet['name']}! Happiness: {pet['happiness']}.")

    @app_commands.command(name="pet_delete", description="Delete your pet")
    async def pet_delete(self, interaction: discord.Interaction):
        """ Deletes a pet """
        user_id = str(interaction.user.id)
        if user_id not in self.pets:
            await interaction.response.send_message("You don't have a pet to delete!", ephemeral=True)
            return
        
        del self.pets[user_id]
        self.save_pets()
        await interaction.response.send_message(f"❌ {interaction.user.mention}, your pet has been deleted!")

    async def cooldown_message(self, interaction: discord.Interaction):
        """Handles cooldown messages"""
        retry_after = interaction.command.get_cooldown_retry_after(interaction)
        await interaction.response.send_message(
            f"⏳ {interaction.user.mention}, you need to wait {int(retry_after)} seconds before using this command again!", 
            ephemeral=True
        )

    async def on_app_command_error(self, interaction: discord.Interaction, error):
        """Global error handler for cooldowns"""
        if isinstance(error, app_commands.CommandOnCooldown):
            await self.cooldown_message(interaction)
        else:
            raise error

async def setup(bot):
    await bot.add_cog(VirtualPet(bot))
