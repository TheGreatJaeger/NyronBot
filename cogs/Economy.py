import discord
from discord.ext import commands
from discord import app_commands
import json
import random

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} is ready!")
        
    async def cooldown_message(self, ctx):
        retry_after = ctx.command.get_cooldown_retry_after(ctx)
        await ctx.send(f"⏳ {ctx.author.mention}, you need to wait {int(retry_after)} seconds before using this command again!")
        
    @app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None):
        """Check user balance"""
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        member = member or interaction.user

        if str(member.id) not in user_eco:
            user_eco[str(member.id)] = {"Balance": 100, "Deposited": 0}

        embed = discord.Embed(
            title=f"{member.name}'s Current Balance",
            description="The current balance of this user.",
            color=discord.Color.green()
        )
        embed.add_field(name="Current Balance:", value=f"${user_eco[str(member.id)]['Balance']}.", inline=False)
        embed.add_field(name="Deposited Balance:", value=f"${user_eco[str(member.id)]['Deposited']}.", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="beg", description="Try your luck and beg for money")
    async def beg(self, interaction: discord.Interaction):
        """Beg for money"""
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        user_id = str(interaction.user.id)
        if user_id not in user_eco:
            user_eco[user_id] = {"Balance": 100}

        amount = random.randint(-10, 30)
        user_eco[user_id]["Balance"] += amount

        if amount > 0:
            message = f"💰 Some kind souls gave you **${amount}**!"
        elif amount < 0:
            message = f"💸 Oh no! You got robbed and lost **${abs(amount)}**!"
        else:
            message = "😞 You got nothing this time."

        embed = discord.Embed(title="Begging Result", description=message, color=discord.Color.random())

        with open("cogs/jsonfiles/eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Work and earn money")
    async def work(self, interaction: discord.Interaction):
        """Earn money by working"""
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        user_id = str(interaction.user.id)
        if user_id not in user_eco:
            user_eco[user_id] = {"Balance": 100, "Deposited": 0}

        amount = random.randint(100, 350)
        user_eco[user_id]["Balance"] += amount

        embed = discord.Embed(
            title="Work Result",
            description=f"🛠 You worked and earned **${amount}**!",
            color=discord.Color.green()
        )

        with open("cogs/jsonfiles/eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="steal", description="Try to steal money from another user")
    async def steal(self, interaction: discord.Interaction, member: discord.Member):
        """Steal money from another user"""
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        user_id = str(interaction.user.id)
        target_id = str(member.id)

        if user_id not in user_eco:
            user_eco[user_id] = {"Balance": 100}
        if target_id not in user_eco:
            user_eco[target_id] = {"Balance": 100}

        steal_success = random.choice([True, False])

        if steal_success:
            amount = random.randint(1, 100)
            user_eco[user_id]["Balance"] += amount
            user_eco[target_id]["Balance"] -= amount

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

        with open("cogs/jsonfiles/eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deposit", description="Deposit money into your bank")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        """Deposit money into the bank"""
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        user_id = str(interaction.user.id)
        if user_id not in user_eco:
            user_eco[user_id] = {"Balance": 100, "Deposited": 0}

        if amount > user_eco[user_id]["Balance"]:
            await interaction.response.send_message("❌ You don't have enough money to deposit.", ephemeral=True)
            return

        user_eco[user_id]["Balance"] -= amount
        user_eco[user_id]["Deposited"] += amount

        with open("cogs/jsonfiles/eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

        await interaction.response.send_message(f"🏦 You deposited **${amount}** into your bank.")

    @app_commands.command(name="withdraw", description="Withdraw money from your bank")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        """Withdraw money from the bank"""
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        user_id = str(interaction.user.id)
        if user_id not in user_eco:
            user_eco[user_id] = {"Balance": 100, "Deposited": 0}

        if amount > user_eco[user_id]["Deposited"]:
            await interaction.response.send_message("❌ You don't have enough money in your bank.", ephemeral=True)
            return

        user_eco[user_id]["Deposited"] -= amount
        user_eco[user_id]["Balance"] += amount

        with open("cogs/jsonfiles/eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

        await interaction.response.send_message(f"🏧 You withdrew **${amount}** from your bank.")
            
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """ Handles cooldown errors """
        if isinstance(error, commands.CommandOnCooldown):
            await self.cooldown_message(ctx)
        else:
            raise error

async def setup(client):
    await client.add_cog(Economy(client))
