import json
from typing import Optional

from discord import Forbidden
from discord.ext import commands
from discord.ext.commands import command, Cog
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

from helpers import is_mod


class Roles(Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("roles.json") as file:
            self.roles = json.loads(file.read())
        self.guild = None

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        self.guild = self.bot.get_guild(self.bot._custom_config["server_id"])
        if self.guild is None:
            raise RuntimeError("missing server id")

    @command()
    @is_mod()
    async def post_role_msg(self, ctx, reference: Optional[str] = None):
        def role_to_button(role: dict) -> Button:
            if "emoji" in role:
                return Button(style=ButtonStyle.grey, label=role["title"], id=str(role["id"]), emoji=role["emoji"])
            return Button(style=ButtonStyle.grey, label=role["title"], id=str(role["id"]))

        def split_if_necessary(l: list) -> list[list]:
            return [l[i:i+5] for i in range(0, len(l), 5)]

        for category in self.roles:
            if reference is not None:
                if category["ref"] != reference:
                    continue
            await ctx.send(
                category["topic"] + (category["body"] if "body" in category else ""),
                components=[*split_if_necessary([*map(role_to_button, category["roles"])])],
            )

    @Cog.listener()
    async def on_button_click(self, res):
        """
        Possible interaction types:
        - Pong
        - ChannelMessageWithSource
        - DeferredChannelMessageWithSource
        - DeferredUpdateMessage
        - UpdateMessage
        """
        role = self.guild.get_role(int(res.component.id))
        if role is None:
            await res.respond(
                type=InteractionType.ChannelMessageWithSource, content=f"Error: could not find role {res.component.label}"
            )
            print(f"Error: could not find role {res.component.label}")
            return

        member = self.guild.get_member(res.user.id)
        if member is None:
            await res.respond(
                type=InteractionType.ChannelMessageWithSource,
                content="Error: You are not in the server!"
            )
            print("Error: {res.user.id} is not in the server!")
            return

        if role in member.roles:
            try:
                await member.remove_roles(role)
            except Forbidden:
                await res.respond(
                    type=InteractionType.ChannelMessageWithSource,
                    content="Error: I am not allowed to remove your roles!"
                )
                print(f"Error: I am not allowed to remove roles from {res.user.id}!")
                return
            await res.respond(
                type=InteractionType.ChannelMessageWithSource,
                content=f"Okay! I have removed the {res.component.label} role from you."
            )
        else:
            try:
                await member.add_roles(role)
            except Forbidden:
                await res.respond(
                    type=InteractionType.ChannelMessageWithSource,
                    content="Error: I am not allowed to add roles to you!"
                )
                print(f"Error: I am not allowed to add roles to {res.user.id}!")
                return
            await res.respond(
                type=InteractionType.ChannelMessageWithSource,
                content=f"Okay! I have added the {res.component.label} role to you."
            )


def setup(bot):
    DiscordComponents(bot)  # If you have this in an on_ready() event you can remove this line.
    bot.add_cog(Roles(bot))
