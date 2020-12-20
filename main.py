import discord
from discord.ext import commands

from discord.ext.commands import Bot

from os import environ
from dotenv import load_dotenv


def parse_config_from_env() -> dict:
    if "DISCORD_SERVER_ID" not in environ or len(environ["DISCORD_SERVER_ID"]) == 0:
        raise ValueError("missing server id")
    if "DISCORD_COMMAND_PREFIX" not in environ or len(environ["DISCORD_COMMAND_PREFIX"]) == 0:
        raise ValueError("missing prefix")
    if "DISCORD_COMMAND_CHANNEL" not in environ or len(environ["DISCORD_COMMAND_CHANNEL"]) == 0:
        raise ValueError("missing command channel")
    if "DISCORD_TOKEN" not in environ or len(environ["DISCORD_TOKEN"]) == 0:
        raise ValueError("missing token")
    if "DISCORD_ANARCHY_CATEGORY" not in environ or len(environ["DISCORD_ANARCHY_CATEGORY"]) == 0:
        raise ValueError("missing anarchy category")

    return {
        "server_id": int(environ["DISCORD_SERVER_ID"]),
        "command_prefix": environ["DISCORD_COMMAND_PREFIX"],
        "command_channel_id": int(environ["DISCORD_COMMAND_CHANNEL"]),
        "token": environ["DISCORD_TOKEN"],
        "anarchy_category_id": int(environ["DISCORD_ANARCHY_CATEGORY"]),
        "anarchy_full_log_id":
            int(environ["DISCORD_FULL_LOG_CHANNEL"])
            if "DISCORD_FULL_LOG_CHANNEL" in environ and len(environ["DISCORD_FULL_LOG_CHANNEL"]) > 0
            else None,
        "anarchy_anon_log_id":
            int(environ["DISCORD_ANON_LOG_CHANNEL"])
            if "DISCORD_ANON_LOG_CHANNEL" in environ and len(environ["DISCORD_ANON_LOG_CHANNEL"]) > 0
            else None
    }


async def send_cmd_help(ctx):
    cmd = ctx.command
    em = discord.Embed(title=f'Usage: {ctx.prefix + cmd.name + " " + cmd.signature}', color=discord.Color.green())
    em.description = cmd.help
    return em


async def on_command_error(ctx, error):
    send_help = (commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments,
                 commands.UserInputError)

    if isinstance(error, commands.CommandNotFound):  # fails silently
        pass

    elif isinstance(error, send_help):
        _help = await send_cmd_help(ctx)
        await ctx.send(embed=_help)


def main():
    load_dotenv()
    config: dict = parse_config_from_env()

    client = Bot(config["command_prefix"])

    client.add_listener(on_command_error, "on_command_error")

    client._custom_config = config
    client.load_extension("chaos")
    client.run(config["token"])


if __name__ == "__main__":
    main()
