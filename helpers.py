from typing import Any

import discord
from discord.ext import commands as commands


def is_mod():
    async def predicate(ctx):
        return ctx.guild.get_role(510218732698599445) in ctx.author.roles

    return commands.check(predicate)


def is_response():
    async def predicate(ctx):
        response = ctx.message.reference
        if response is None:
            await ctx.message.channel.send("You must use this command by replying to a message")
            return False
        message = await ctx.fetch_message(response.message_id)
        if message is None:
            await ctx.message.channel.send("Could not load message being replied to.")
            return False
        return True

    return commands.check(predicate)


def fetch_responded(ctx: Any) -> discord.Message:
    return await ctx.fetch_message(ctx.message.reference.message_id)


def make_button_list(buttons: list) -> list[list]:
    """
    If the list has more than 5 elements, split it into multiple lists of up to 5 elements.
    Args:
        buttons (list): List of button components
    Returns:
        list of lists of button components, each up to 5 elements
    """
    return [buttons[i:i + 5] for i in range(0, len(buttons), 5)]
