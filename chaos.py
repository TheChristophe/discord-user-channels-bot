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
        self._log_channel_id = config["anarchy_logging_id"]

        self._server: Optional[discord.Guild] = None
        self._channel: Optional[discord.TextChannel] = None
        self._category: Optional[discord.CategoryChannel] = None
        self._logging: Optional[discord.TextChannel] = None

    class MoreThanOne(Exception):
        pass

    def _get_channel(self, channel_ref: Union[discord.TextChannel, int, str]) -> Optional[Union[discord.TextChannel, discord.VoiceChannel]]:
        """Helper to fetch channels.

        Args:
            channel_ref (Union[discord.TextChannel, int, str]) - A reference to the channel; may be a channel
            id/snowflake, channel name or a direct channel reference.
        Returns:
            Optional[Union[discord.TextChannel, discord.VoiceChannel]] - The channel, if any was found.
        """
        # if snowflake/ID
        if isinstance(channel_ref, int):
            channel = self._client.get_channel(channel_ref)
        # by name
        elif isinstance(channel_ref, str):
            channel = discord.utils.get(self._category.channels, name=channel_ref)
        elif isinstance(channel_ref, discord.TextChannel):
            return channel_ref
        else:
            raise ValueError("unknown channel reference type")
        # not found
        if channel is None:
            return None
        if isinstance(channel_ref, str) and \
                len([channel for channel in self._category.channels if channel.name == channel_ref]) > 1:
            raise Anarchy.MoreThanOne()
        return channel

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        """Set up internal references."""
        print('We have logged in as {0.user}'.format(self._client))

        self._server = self._client.get_guild(self._server_id)
        self._channel = self._server.get_channel(self._commands_channel)
        self._category = self._server.get_channel(self._category_id)
        if self._log_channel_id is not None:
            self._logging = self._server.get_channel(self._log_channel_id)

    async def _log(self, whence, who: str, what: str, how: str):
        if self._logging is None:
            return
        where = "DMs" if isinstance(whence, discord.DMChannel) else '#' + whence.name
        embed = discord.Embed(title="Anarchy")
        embed.set_footer(text="Through " + where)
        embed.add_field(name=what, value=how)
        embed.add_field(name="Responsible", value=who)
        await self._logging.send(embed=embed)

    @commands.command()
    async def add_text_channel(self, ctx: Any, name: str):
        """Create a text channel.

        Args:
            ctx (Any) - (internal) The command context.
            name (str) - The channel's name.
        """
        position = 0
        for channel in self._category.channels:
            if name < channel.name:
                position = channel.position - 1
                break

        try:
            channel = await self._server.create_text_channel(name, category=self._category, position=position)

            if channel is not None:
                await ctx.message.add_reaction("✅")
                await self._log(ctx.message.channel, ctx.message.author, "Channel created: {}", channel.name)
        except discord.Forbidden:
            await ctx.message.send("Insufficient permissions")
            return
        except (discord.HTTPException, discord.InvalidArgument):
            await ctx.message.add_reaction("❌")
            return

    @commands.command()
    async def add_voice_channel(self, ctx: Any, name: str):
        """Create a voice channel.

        Args:
            ctx (Any) - (internal) The command context.
            name (str) - The channel's name.
        """
        await self._server.create_voice_channel(name, category=self._category)
        await ctx.message.add_reaction("✅")

        await self._log(ctx.message.channel, ctx.message.author, "Channel created", name)

    @commands.command()
    async def remove_channel(self, ctx: Any, channel_ref: Union[discord.TextChannel, int, str]):
        """Remove a channel.

        Args:
            ctx (Any) - (internal) The command context.
            channel_ref (Union[discord.TextChannel, int, str]) - The channel to remove.
        """
        try:
            channel = self._get_channel(channel_ref)
            if channel is None:
                await ctx.send("channel not found")
                return
        except Anarchy.MoreThanOne:
            await ctx.send("multiple channels with that name found, please specify id")
            return

        if channel.category_id != self._category.id:
            # sanity check
            await ctx.send("this channel is not deletable")
            return

        channel_name: str = channel.name

        await channel.delete()
        await ctx.message.add_reaction("✅")

        await self._log(ctx.message.channel, ctx.message.author, "Channel removed", channel_name)

    @commands.command()
    async def set_channel_name(self, ctx: Any, channel_ref: Union[discord.TextChannel, int, str], name: str):
        """Set a new channel name.

        Args:
            ctx (Any) - (internal) The command context.
            channel_ref (Union[discord.TextChannel, int, str]) - The channel to set the description of.
            name (str) - The new channel name.
        """
        try:
            channel = self._get_channel(channel_ref)
            if channel is None:
                await ctx.send("channel not found")
                return
        except Anarchy.MoreThanOne:
            await ctx.send("multiple channels with that name found, please specify id")
            return

        old_name: str = channel.name

        await channel.edit(name=name)
        await ctx.message.add_reaction("✅")

        await self._log(ctx.message.channel, ctx.message.author, "Channel renamed", old_name + " => " + name)

    @commands.command()
    async def set_channel_description(self, ctx: Any, channel_ref: Union[discord.TextChannel, int, str], description: str):
        """Give a channel a new description.

        Args:
            ctx (Any) - (internal) The command context.
            channel_ref (Union[discord.TextChannel, int, str]) - The channel to set the description of.
            description (str) - The new channel description.
        """
        try:
            channel = self._get_channel(channel_ref)
            if channel is None:
                await ctx.send("channel not found")
                return
        except Anarchy.MoreThanOne:
            await ctx.send("multiple channels with that name found, please specify id")
            return

        if not isinstance(channel, discord.TextChannel):
            await ctx.send("cannot set description on this type of channel")
            return

        old_description: str = channel.topic if channel.topic is not None else "[nothing]"

        await channel.edit(topic=description)
        await ctx.message.add_reaction("✅")

        await self._log(ctx.message.channel, ctx.message.author, "Channel description changed",
                        old_description + " => " + description)

    @commands.command()
    async def toggle_nsfw(self, ctx: Any, channel_ref: Union[discord.TextChannel, int, str]):
        """Toggle NSFW mode on a channel.

        Args:
            ctx (Any) - (internal) The command context.
            channel_ref (Union[discord.TextChannel, int, str]) - The channel to toggle NSFW mode on.
        """
        try:
            channel = self._get_channel(channel_ref)
            if channel is None:
                await ctx.send("channel not found")
                return
        except Anarchy.MoreThanOne:
            await ctx.send("multiple channels with that name found, please specify id")
            return

        await channel.edit(nsfw=not channel.nsfw)
        await ctx.message.add_reaction("✅")

        await self._log(ctx.message.channel, ctx.message.author, "NSFW toggled",
                        channel.nsfw)


def setup(bot):
    """Load the anarchy extension.

    Args:
        bot (discord.Client) - The discord bot to attach to.
    """
    anarchy: Anarchy = Anarchy(bot, bot._custom_config)
    bot.add_cog(anarchy)
