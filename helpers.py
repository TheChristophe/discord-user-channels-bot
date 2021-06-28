from discord.ext import commands as commands


def is_mod():
    async def predicate(ctx):
        return ctx.guild.get_role(510218732698599445) in ctx.author.roles
    return commands.check(predicate)
