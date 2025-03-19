import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import os
import time

ECONOMY_FILE = "cogs/jsonfiles/eco.json"

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.load_data()
        self.cooldowns = {}  # Новый метод кулдауна

    def load_data(self):
        """Загружает или создаёт JSON-файл"""
        if not os.path.exists(ECONOMY_FILE):
            self.user_eco = {}
            self.save_data()
        else:
            try:
                with open(ECONOMY_FILE, "r", encoding="utf-8") as f:
                    self.user_eco = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.user_eco = {}
                self.save_data()

    def save_data(self):
        """Сохраняет данные экономики"""
        with open(ECONOMY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.user_eco, f, indent=4)

    def check_cooldown(self, user_id, command, cooldown_time):
        """Проверяет кулдаун команды"""
        now = time.time()
        if user_id in self.cooldowns and command in self.cooldowns[user_id]:
            elapsed = now - self.cooldowns[user_id][command]
            if elapsed < cooldown_time:
                return int(cooldown_time - elapsed)
        self.cooldowns.setdefault(user_id, {})[command] = now
        return None  # Кулдауна нет, можно выполнять команду

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is ready!")

    async def ensure_response(self, interaction: discord.Interaction):
        """Гарантирует, что бот отвечает, чтобы избежать зависания"""
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=True, ephemeral=False)

    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        """Check user balance"""
        await self.ensure_response(interaction)

        user_id = str(interaction.user.id)
        cooldown = self.check_cooldown(user_id, "balance", 10)
        if cooldown:
            await interaction.followup.send(f"⏳ Wait **{cooldown} seconds** before checking balance again!", ephemeral=True)
            return

        member = member or interaction.user
        if user_id not in self.user_eco:
            self.user_eco[user_id] = {"Balance": 100, "Deposited": 0}

        embed = discord.Embed(
            title=f"{member.name}'s Balance",
            color=discord.Color.green()
        )
        embed.add_field(name="Wallet:", value=f"${self.user_eco[user_id]['Balance']}", inline=False)
        embed.add_field(name="Bank:", value=f"${self.user_eco[user_id]['Deposited']}", inline=False)

        self.save_data()
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="work", description="Earn money by working")
    async def work(self, interaction: discord.Interaction):
        """Earn money by working"""
        await self.ensure_response(interaction)

        user_id = str(interaction.user.id)
        cooldown = self.check_cooldown(user_id, "work", 300)
        if cooldown:
            await interaction.followup.send(f"⏳ Wait **{cooldown} seconds** before using `/work` again!", ephemeral=True)
            return

        if user_id not in self.user_eco:
            self.user_eco[user_id] = {"Balance": 100, "Deposited": 0}

        amount = random.randint(100, 350)
        self.user_eco[user_id]["Balance"] += amount

        embed = discord.Embed(
            title="Work Completed",
            description=f"🛠 You earned **${amount}**!",
            color=discord.Color.green()
        )

        self.save_data()
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="steal", description="Try to steal money from another user")
    async def steal(self, interaction: discord.Interaction, member: discord.Member):
        """Steal money from another user"""
        await self.ensure_response(interaction)

        user_id = str(interaction.user.id)
        cooldown = self.check_cooldown(user_id, "steal", 300)
        if cooldown:
            await interaction.followup.send(f"⏳ Wait **{cooldown} seconds** before stealing again!", ephemeral=True)
            return

        target_id = str(member.id)

        if user_id not in self.user_eco:
            self.user_eco[user_id] = {"Balance": 100}
        if target_id not in self.user_eco:
            self.user_eco[target_id] = {"Balance": 100}

        steal_success = random.choice([True, False])

        if steal_success:
            amount = min(random.randint(1, 100), self.user_eco[target_id]["Balance"])
            self.user_eco[user_id]["Balance"] += amount
            self.user_eco[target_id]["Balance"] -= amount

            embed = discord.Embed(
                title="Stealing Success!",
                description=f"🕵️‍♂️ You stole **${amount}** from {member.mention}!",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="Stealing Failed!",
                description="🚔 You got caught and failed to steal!",
                color=discord.Color.red()
            )

        self.save_data()
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="deposit", description="Deposit money into your bank")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        """Deposit money into the bank"""
        await self.ensure_response(interaction)

        user_id = str(interaction.user.id)
        cooldown = self.check_cooldown(user_id, "deposit", 300)
        if cooldown:
            await interaction.followup.send(f"⏳ Wait **{cooldown} seconds** before depositing again!", ephemeral=True)
            return

        if user_id not in self.user_eco:
            self.user_eco[user_id] = {"Balance": 100, "Deposited": 0}

        if amount > self.user_eco[user_id]["Balance"]:
            await interaction.followup.send("❌ Not enough money!")
            return

        self.user_eco[user_id]["Balance"] -= amount
        self.user_eco[user_id]["Deposited"] += amount

        self.save_data()
        await interaction.followup.send(f"🏦 Deposited **${amount}** into your bank.")

    @app_commands.command(name="withdraw", description="Withdraw money from your bank")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        """Withdraw money from the bank"""
        await self.ensure_response(interaction)

        user_id = str(interaction.user.id)
        cooldown = self.check_cooldown(user_id, "withdraw", 300)
        if cooldown:
            await interaction.followup.send(f"⏳ Wait **{cooldown} seconds** before withdrawing again!", ephemeral=True)
            return

        if user_id not in self.user_eco:
            self.user_eco[user_id] = {"Balance": 100, "Deposited": 0}

        if amount > self.user_eco[user_id]["Deposited"]:
            await interaction.followup.send("❌ Not enough money in bank!")
            return

        self.user_eco[user_id]["Deposited"] -= amount
        self.user_eco[user_id]["Balance"] += amount

        self.save_data()
        await interaction.followup.send(f"🏧 Withdrawn **${amount}** from bank.")
        
    @app_commands.command(name="beg", description="Try your luck and beg for money")
    async def beg(self, interaction: discord.Interaction):
        """Beg for money"""
        await self.ensure_response(interaction)

        user_id = str(interaction.user.id)
        cooldown = self.check_cooldown(user_id, "beg", 300)
        if cooldown:
            await interaction.followup.send(f"⏳ Wait **{cooldown} seconds** before begging again!", ephemeral=True)
            return

        if user_id not in self.user_eco:
            self.user_eco[user_id] = {"Balance": 100}

        amount = random.randint(-10, 30)
        self.user_eco[user_id]["Balance"] += amount

        if amount > 0:
            message = f"💰 Someone gave you **${amount}**!"
        elif amount < 0:
            message = f"💸 You got robbed and lost **${abs(amount)}**!"
        else:
            message = "😞 Nothing today..."

        embed = discord.Embed(title="Begging Result", description=message, color=discord.Color.random())

        self.save_data()
        await interaction.followup.send(embed=embed)

async def setup(client):
    await client.add_cog(Economy(client))
