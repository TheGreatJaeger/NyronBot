import discord
from discord.ext import commands
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
        
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(aliases=["bal", "money"])
    async def balance(self, ctx, member: discord.Member = None):
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        if member is None:
            member = ctx.author

        if str(member.id) not in user_eco:
            user_eco[str(member.id)] = {
                "Balance": 100,
                "Deposited": 0
            }
            with open("cogs/jsonfiles/eco.json", "w") as f:
                json.dump(user_eco, f, indent=4)

        if "Deposited" not in user_eco[str(member.id)]:
            user_eco[str(member.id)]["Deposited"] = 0

        eco_embed = discord.Embed(
            title=f"{member.name}'s Current Balance",
            description="The current balance of this user.",
            color=discord.Color.green()
        )
        eco_embed.add_field(name="Current Balance:", value=f"${user_eco[str(member.id)]['Balance']}.", inline=False)
        eco_embed.add_field(name="Deposited Balance:", value=f"${user_eco[str(member.id)]['Deposited']}.", inline=False)
        eco_embed.set_footer(
            text="Want to increase balance? Try running some economy-based commands!",
            icon_url=None
        )

        await ctx.send(embed=eco_embed)

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command()
    async def beg(self, ctx):
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        if str(ctx.author.id) not in user_eco:
            user_eco[str(ctx.author.id)] = {"Balance": 100}

        cur_bal = user_eco[str(ctx.author.id)]["Balance"]
        amount = random.randint(-10, 30)
        new_bal = cur_bal + amount

        if cur_bal > new_bal:
            eco_embed = discord.Embed(
                title="Oh No! - You've been robbed!",
                description="A group of robbers saw opportunity in taking advantage of you.",
                color=discord.Color.red()
            )
            eco_embed.add_field(name="New Balance:", value=f"${new_bal}", inline=False)
            eco_embed.set_footer(text="Should probably beg in a nicer part of town ...", icon_url=None)

        elif cur_bal < new_bal:
            eco_embed = discord.Embed(
                title="Oh Sweet Green!",
                description="Some kind souls out there have given you what they could.",
                color=discord.Color.green()
            )
            eco_embed.add_field(name="New Balance:", value=f"${new_bal}", inline=False)
            eco_embed.set_footer(text="Want more? Wait 1 hour to run this command again, or try some others!", icon_url=None)

        else:
            eco_embed = discord.Embed(
                title="Awh That Sucks!",
                description="Looks like begging didn't get you anywhere today.",
                color=discord.Color.green()
            )
            eco_embed.set_footer(text="Want more? Wait 1 hour to run this command again, or try some others!", icon_url=None)

        await ctx.send(embed=eco_embed)

        user_eco[str(ctx.author.id)]["Balance"] += amount
        with open("cogs/jsonfiles/eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)
            
    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command()
    async def work(self, ctx):
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        if str(ctx.author.id) not in user_eco:
            user_eco[str(ctx.author.id)] = {"Balance": 100, "Deposited": 0}

        amount = random.randint(100, 350)
        user_eco[str(ctx.author.id)]["Balance"] += amount

        with open("cogs/jsonfiles/eco.json", "w") as f:
            json.dump(user_eco, f, indent=4)

        eco_embed = discord.Embed(
            title="Phew!",
            description="After a tiring shift, here's what you earned!",
            color=discord.Color.green()
        )
        eco_embed.add_field(name="Earnings:", value=f"${amount}", inline=False)
        eco_embed.add_field(name="New Balance:", value=f"${user_eco[str(ctx.author.id)]['Balance']}.", inline=False)
        eco_embed.set_footer(
            text="Want more? Wait 1 hour to run this command again, or try some others!",
            icon_url=None
        )

        await ctx.send(embed=eco_embed)

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command()
    async def steal(self, ctx, member: discord.Member):
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        steal_probability = random.randint(0, 1)

        if steal_probability == 1:
            amount = random.randint(1, 100)

            if str(ctx.author.id) not in user_eco:
                user_eco[str(ctx.author.id)] = {"Balance": 100}

            if str(member.id) not in user_eco:
                user_eco[str(member.id)] = {"Balance": 100}

            user_eco[str(ctx.author.id)]["Balance"] += amount
            user_eco[str(member.id)]["Balance"] -= amount

            with open("cogs/jsonfiles/eco.json", "w") as f:
                json.dump(user_eco, f, indent=4)

            await ctx.send(f"{ctx.author.mention}, You have stolen ${amount} from {member.mention}! Be sure to keep it safe as they may be looking for revenge...")

        else:
            await ctx.send("Uh oh.. You did not get to steal from this user, better luck next time..")

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command(aliases=["dep", "bank"])
    async def deposit(self, ctx, amount: int):
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        if str(ctx.author.id) not in user_eco:
            user_eco[str(ctx.author.id)] = {"Balance": 100, "Deposited": 0}

        if amount > user_eco[str(ctx.author.id)]["Balance"]:
            await ctx.send("Cannot deposit this amount because your balance does not have the sufficient funds.")
        else:
            user_eco[str(ctx.author.id)]["Deposited"] += amount
            user_eco[str(ctx.author.id)]["Balance"] -= amount

            with open("cogs/jsonfiles/eco.json", "w") as f:
                json.dump(user_eco, f, indent=4)

            await ctx.send(f"You have deposited ${amount} into your bank. This money is now safe and only you can touch it.")

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command(aliases=["wd"])
    async def withdraw(self, ctx, amount: int):
        with open("cogs/jsonfiles/eco.json", "r") as f:
            user_eco = json.load(f)

        if str(ctx.author.id) not in user_eco:
            user_eco[str(ctx.author.id)] = {"Balance": 100, "Deposited": 0}

        if amount > user_eco[str(ctx.author.id)]["Deposited"]:
            await ctx.send("Cannot withdraw this amount because your bank does not have it.")
        else:
            user_eco[str(ctx.author.id)]["Deposited"] -= amount
            user_eco[str(ctx.author.id)]["Balance"] += amount

            with open("cogs/jsonfiles/eco.json", "w") as f:
                json.dump(user_eco, f, indent=4)

            await ctx.send(f"You have withdrawn ${amount} from your bank.")
            
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """ Handles cooldown errors """
        if isinstance(error, commands.CommandOnCooldown):
            await self.cooldown_message(ctx)
        else:
            raise error

async def setup(client):
    await client.add_cog(Economy(client))
