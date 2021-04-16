from typing import Any, Optional, Union

import discord
from discord import Client
import discord.ext.commands as commands

from random import randint


async def _add_puke(message: discord.Message):
    try:
        await message.add_reaction("🤮")
    except discord.Forbidden:
        return
    except discord.HTTPException:
        # retry once
        try:
            await message.add_reaction("🤮")
        except discord.HTTPException:
            pass
        finally:
            return


class JavaReact(commands.Cog):
    """Appropriate java reaction."""

    def __init__(self, client, config):
        self._client: Client = client

        self._channel_ids = config["java_channels"]

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        """Parse messages for the cursed word."""
        if message.channel.id in self._channel_ids or\
                (message.channel.category is not None and message.channel.category.id in self._channel_ids):
            if 'java' in message.content.lower() and randint(1, 10) == 10:
                await _add_puke(message)


def setup(bot):
    """Load the anarchy extension.

    Args:
        bot (discord.Client) - The discord bot to attach to.
    """
    java_react: JavaReact = JavaReact(bot, bot._custom_config)
    bot.add_cog(java_react)
