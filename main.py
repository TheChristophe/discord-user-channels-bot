import discord

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
        "anarchy_category_id": int(environ["DISCORD_ANARCHY_CATEGORY"])
    }


def main():
    load_dotenv()
    config: dict = parse_config_from_env()

    client = Bot(config["command_prefix"])
    client._custom_config = config
    client.load_extension("chaos")
    client.run(config["token"])


if __name__ == "__main__":
    main()
