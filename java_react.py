from typing import Any, Optional, Union

import discord
from discord import Client
import discord.ext.commands as commands

from random import randint

from config import config


async def _add_react(message: discord.Message, emoji="🤮"):
    try:
        await message.add_reaction(emoji)
    except discord.Forbidden:
        return
    except discord.HTTPException:
        # retry once
        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            pass
        finally:
            return


class JavaReact(commands.Cog):
    """Appropriate java reaction."""

    def __init__(self, client):
        self._client: Client = client

        self._channel_ids = config["java_channels"]

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        """Parse messages for the cursed word."""
        if message.channel.id in self._channel_ids or isinstance(message.channel, discord.DMChannel) or \
                (message.channel.category is not None and message.channel.category.id in self._channel_ids):
            if 'java' in message.content.lower() and randint(1, 10) == 10:
                await _add_react(message)
        if 'os' in message.content.lower():
            if 'pavel' in message.content.lower():
                await _add_react(message, "😡")
                await _add_react(message, "🤬")


def setup(bot):
    """Load the anarchy extension.

    Args:
        bot (discord.Client) - The discord bot to attach to.
    """
    java_react: JavaReact = JavaReact(bot)
    bot.add_cog(java_react)
