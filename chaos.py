from typing import Any, Optional, Union

import discord
from discord import Client
import discord.ext.commands as commands


async def _add_checkmark(ctx: Any):
    try:
        await ctx.message.add_reaction("✅")
    except discord.Forbidden:
        await ctx.send("Success (but I could not add a ✅ reaction)")
        return
    except discord.HTTPException:
        # retry once
        try:
            await ctx.message.add_reaction("✅")
        except discord.HTTPException:
            await ctx.send("Success (but I could not add a ✅ reaction)")
        finally:
            return


class Anarchy(commands.Cog):
    """Anarchy channel category where anyone may create, delete or edit channels."""

    def __init__(self, client, config):
        self._client: Client = client

        self._server_id = config["server_id"]
        self._category_id = config["anarchy_category_id"]
        self._full_log_id = config["anarchy_full_log_id"]
        self._anon_log_id = config["anarchy_anon_log_id"]

        self._server: Optional[discord.Guild] = None
        self._category: Optional[discord.CategoryChannel] = None
        self._full_log: Optional[discord.TextChannel] = None
        self._anon_log: Optional[discord.TextChannel] = None

    class MoreThanOne(Exception):
        pass

    def _get_channel(self, channel_ref: Union[discord.TextChannel, int, str]) -> \
            Optional[Union[discord.TextChannel, discord.VoiceChannel]]:
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
        self._category = self._server.get_channel(self._category_id)
        print("Server:", self._server.name, "Category:", self._category.name)
        if self._full_log_id is not None:
            self._full_log = self._server.get_channel(self._full_log_id)
            print("Full log:", self._full_log.name)

        if self._anon_log_id is not None:
            self._anon_log = self._server.get_channel(self._anon_log_id)
            print("Anonymous log:", self._anon_log.name)

    async def _log(self, whence, who: str, what: str, how: str):
        print(who, "did \"", what, how, "\" from", whence)
        where = "DMs" if isinstance(whence, discord.DMChannel) else '#' + whence.name
        embed = discord.Embed(title="Anarchy")
        embed.add_field(name=what, value=how)
        if self._anon_log is not None:
            await self._anon_log.send(embed=embed)
        embed.set_footer(text="Through " + where)
        embed.add_field(name="Responsible", value=who)
        if self._full_log is not None:
            await self._full_log.send(embed=embed)

    async def _add_channel(self, ctx: Any, name: str, channel_type: type):
        position = None
        if channel_type == discord.TextChannel:
            position = 0
            for channel in self._category.channels:
                if name < channel.name:
                    position = channel.position - 1
                    break

        try:
            channel = None
            if channel_type == discord.TextChannel:
                channel = await self._server.create_text_channel(name, category=self._category, position=position)
            elif channel_type == discord.VoiceChannel:
                channel = await self._server.create_voice_channel(name, category=self._category, position=position)
            else:
                await ctx.send("Internal error")
                return

            if channel is not None:
                await _add_checkmark(ctx)
                await self._log(ctx.message.channel, ctx.message.author, "Channel created:", channel.name)
            else:
                await ctx.message.add_reaction("❌")
                await self._log(ctx.message.channel, ctx.message.author, "Failed to create channel:", name)
        except discord.Forbidden:
            await ctx.message.send("I lack the permissions to create channels")
            return
        except (discord.HTTPException, discord.InvalidArgument):
            await ctx.message.add_reaction("❌")
            return

    @commands.command()
    async def add_text_channel(self, ctx: Any, name: str):
        """Create a text channel.

        Args:
            ctx (Any) - (internal) The command context.
            name (str) - The channel's name.
        """
        await self._add_channel(ctx, name, discord.TextChannel)

    @commands.command()
    async def add_voice_channel(self, ctx: Any, name: str):
        """Create a voice channel.

        Args:
            ctx (Any) - (internal) The command context.
            name (str) - The channel's name.
        """
        await self._add_channel(ctx, name, discord.VoiceChannel)

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

        try:
            await channel.delete()
        except discord.Forbidden:
            await ctx.send("I lack the permissions to delete channels")
            return
        except discord.HTTPException:
            try:
                await channel.delete()
            except discord.HTTPException:
                await ctx.send("❌")
        else:
            await _add_checkmark(ctx)
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

        try:
            await channel.edit(name=name)
        except (discord.HTTPException, discord.Forbidden, discord.InvalidArgument):
            await ctx.message.add_reaction("❌")
            return
        else:
            await self._log(ctx.message.channel, ctx.message.author, "Channel renamed", old_name + " => " + name)
            await _add_checkmark(ctx)

    @commands.command()
    async def set_channel_description(self, ctx: Any, channel_ref: Union[discord.TextChannel, int, str],
                                      description: str):
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

        try:
            await channel.edit(topic=description)
        except (discord.HTTPException, discord.Forbidden, discord.InvalidArgument):
            await ctx.message.add_reaction("❌")
            return
        else:
            await self._log(ctx.message.channel, ctx.message.author, "Channel description changed",
                            old_description + " => " + description)
            await _add_checkmark(ctx)

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

        try:
            await channel.edit(nsfw=not channel.nsfw)
        except (discord.HTTPException, discord.Forbidden, discord.InvalidArgument):
            await ctx.message.add_reaction("❌")
            return
        else:
            await self._log(ctx.message.channel, ctx.message.author, "NSFW toggled", channel.nsfw)
            await _add_checkmark(ctx)

    @commands.command()
    async def pin(self, ctx: Any):
        """Pin a message. Reply to the message you want to pin with this command."""
        if ctx.message.channel.category is None or ctx.message.channel.category != self._category:
            await ctx.message.channel.send("Wrong category")
            return

        response = ctx.message.reference
        if response is None:
            await ctx.message.channel.send("You're not replying to a message :(")
            return
        message = await ctx.fetch_message(response.message_id)
        if message is None:
            await ctx.message.channel.send("Could not load message being replied to.")
            return
        await message.pin()

    @commands.command()
    async def unpin(self, ctx: Any):
        """Unpin a message. Reply to the message you want to unpin with this command."""
        if ctx.message.channel.category is None or ctx.message.channel.category != self._category:
            await ctx.message.channel.send("Wrong category")
            return

        response = ctx.message.reference
        if response is None:
            await ctx.message.channel.send("You're not replying to a message :(")
            return
        message = await ctx.fetch_message(response.message_id)
        if message is None:
            await ctx.message.channel.send("Could not load message being replied to.")
            return
        await message.unpin()

    @commands.command(aliases=['🔫'])
    async def päng(self, ctx):
        await ctx.message.channel.send("Pew pew pew!")

    @commands.command()
    async def xkcd(self, ctx, nr:int):
        await ctx.message.channel.send("https://xkcd.com/{}/".format(nr))


def setup(bot):
    """Load the anarchy extension.

    Args:
        bot (discord.Client) - The discord bot to attach to.
    """
    anarchy: Anarchy = Anarchy(bot, bot._custom_config)
    bot.add_cog(anarchy)

