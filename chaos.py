from typing import Any, Optional, Union

import discord
from discord import Client
import discord.ext.commands as commands


class Anarchy(commands.Cog):
    """Anarchy channel category where anyone may create, delete or edit channels."""

    def __init__(self, client, config):
        self._client: Client = client

        self._server_id = config["server_id"]
        self._commands_channel = config["server_id"]
        self._category_id = config["anarchy_category_id"]

        self._server: Optional[discord.Guild] = None
        self._channel: Optional[discord.TextChannel] = None
        self._category: Optional[discord.CategoryChannel] = None

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        """Set up internal references."""
        print('We have logged in as {0.user}'.format(self._client))

        self._server = self._client.get_guild(self._server_id)
        self._channel = self._server.get_channel(self._commands_channel)
        self._category = self._server.get_channel(self._category_id)

    @commands.command()
    async def add_text_channel(self, ctx: Any, name: str):
        """Create a text channel.

        Args:
            ctx (Any) - (internal) The command context.
            name (str) - The channel's name.
        """
        await self._server.create_text_channel(name, category=self._category)

    @commands.command()
    async def add_voice_channel(self, ctx: Any, name: str):
        """Create a voice channel.

        Args:
            ctx (Any) - (internal) The command context.
            name (str) - The channel's name.
        """
        await self._server.create_voice_channel(name, category=self._category)

    @commands.command()
    async def remove_channel(self, ctx: Any, name: str):
        """Remove a channel.

        Args:
            ctx (Any) - (internal) The command context.
            name (str) - The channel's name.
        """
        channel = discord.utils.get(self._server.channels, name=name)
        if channel is None:
            await ctx.send("channel not found")
            return
        if len([channel for channel in self._server.channels if channel.name == name]) > 1:
            await ctx.send("multiple channels found, please specify id")
            return

        await channel.delete()

    @commands.command()
    async def remove_channel_by_id(self, ctx: Any, snowflake: int):
        """Remove a channel by id.

        Args:
            ctx (Any) - (internal) The command context.
            snowflake (int) - The channel's id.
        """
        if discord.utils.get(self._category.channels, id=snowflake) is None:
            await ctx.send("channel not found")
            return
        channel = self._server.get_channel(snowflake)
        await channel.delete()


def setup(bot):
    """Load the anarchy extension.

    Args:
        bot (discord.Client) - The discord bot to attach to.
    """
    anarchy: Anarchy = Anarchy(bot, bot._custom_config)
    bot.add_cog(anarchy)
