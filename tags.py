from typing import Any, Union

from discord import Client, Emoji
import discord.ext.commands as commands

from database import Tag, session, engine, DBSession
from sqlalchemy.orm import Session


def is_owner():
    async def predicate(ctx):
        return ctx.author.id == 147399559247691776
    return commands.check(predicate)


class Tags(commands.Cog):
    """Store user created tags/commands."""

    def __init__(self, client, config):
        self._client: Client = client
        self._channel_ids = config["java_channels"]

    @commands.command()  # name='!'
    async def tag(self, ctx: Any, name: str):
        """"""
        with DBSession():
            q: Tag = session.query(Tag).filter(Tag.name == name).limit(1).first()
        if q is None:
            await ctx.send("I don't know that tag <:sadness:591779689689907211>")
            return
        await ctx.send(q.contents)

    @commands.command()
    @is_owner()
    async def set_tag(self, ctx: Any, name: str, *content: Union[str, Emoji]):
        try:
            with DBSession():
                q: Tag = session.query(Tag).filter(Tag.name == name).limit(1).first()
            if q is None:
                with DBSession():
                    q = Tag(name, ' '.join(content))
                    session.add(q)
                    session.commit()
            else:
                with DBSession():
                    q.contents = ' '.join(content)
                    session.add(q)
                    session.commit()
        except Exception as e:
            print(e)
            await ctx.message.add_reaction("❎")
            return
        await ctx.message.add_reaction("✅")

    @commands.command()
    @is_owner()
    async def del_tag(self, ctx: Any, name: str):
        try:
            with DBSession():
                q: Tag = session.query(Tag).filter(Tag.name == name).limit(1).first()
            if q is not None:
                with DBSession():
                    session.delete(q)
                    session.commit()
            else:
                await ctx.message.add_reaction("❓")
        except Exception as e:
            print(e)
            await ctx.message.add_reaction("❎")
            return
        await ctx.message.add_reaction("✅")



def setup(bot):
    """

    Args:
        bot (discord.Client) - The discord bot to attach to.
    """
    java_react: Tags = Tags(bot, bot._custom_config)
    bot.add_cog(java_react)
