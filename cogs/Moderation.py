import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.messages = True

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation.py is ready!")
    #команда clear которая очищает сообщения (доступно только участникам у которых есть права Управлять сообщениями)
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, count: int):
        await ctx.channel.purge(limit=count)
        await ctx.send(f"{count} message(s) have been deleted!")
    #комнада kick которая кикает участника с сервера (доступно только участникам у которых есть права выгонять участников)
    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member: discord.Member, *, reason):
        await ctx.guild.kick(member)

        conf_embed = discord.Embed(title = "Success!", color = discord.Color.green())
        conf_embed.add_field(name = "Kicked:", value = f"{member.mention} has been kicked from the server by {ctx.author.mention}.", inline = False)
        conf_embed.add_field(name = "Reason:", value = reason, inline = False)

        await ctx.send(embed = conf_embed)

    #комнада ban которая банит участника с сервера (доступно только участникам у которых есть права банить участников)
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member: discord.Member, *, reason):
        await ctx.guild.ban(member)

        conf_embed = discord.Embed(title = "Success!", color = discord.Color.red())
        conf_embed.add_field(name = "Banned:", value = f"{member.mention} was banned from this server by {ctx.author.mention}.", inline = False)
        conf_embed.add_field(name = "Reason:", value = reason, inline = False)

        await ctx.send(embed = conf_embed)
    #комнада unban которая разбанит участника с сервера (доступно только участникам у которых есть права банить участников)
    @commands.command(name="unban")
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx, userId):
        user = discord.Object(id = userId)
        await ctx.guild.unban(user)

        conf_embed = discord.Embed(title = "Success!", color = discord.Color.green())
        conf_embed.add_field(name = "Unbanned:", value = f"<@{userId}> was unbanned from this server by {ctx.author.mention}.", inline = False)

        await ctx.send(embed = conf_embed)

    #обработка ошибок
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Error: Missing Required Arguments. You must put in a value of number to run the clear command!")

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Error: You do not have permission to use this command!")

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Error: Missing Required Arguments. You must put in a user @mention and the reason to run the kick command!")

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Error: You do not have permission to use this command!")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Error: Missing Required Arguments. You must put in a user @mention and the reason to run the ban command!")

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Error: You do not have permission to use this command!")

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Error: Missing Required Arguments. You must put in a user ID to run the unban command!")

        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Error: You do not have permission to use this command!")

async def setup(client):
    await client.add_cog(Moderation(client))