import json
from os import environ

from dotenv import load_dotenv


def parse_config_from_env() -> dict:
    if "DISCORD_SERVER_ID" not in environ or len(environ["DISCORD_SERVER_ID"]) == 0:
        raise ValueError("missing server id")
    if "DISCORD_COMMAND_PREFIX" not in environ or len(environ["DISCORD_COMMAND_PREFIX"]) == 0:
        raise ValueError("missing prefix")
    if "DISCORD_TOKEN" not in environ or len(environ["DISCORD_TOKEN"]) == 0:
        raise ValueError("missing token")
    if "DISCORD_ANARCHY_CATEGORY" not in environ or len(environ["DISCORD_ANARCHY_CATEGORY"]) == 0:
        raise ValueError("missing anarchy category")

    return {
        "server_id": int(environ["DISCORD_SERVER_ID"]),
        "command_prefix": environ["DISCORD_COMMAND_PREFIX"],
        "token": environ["DISCORD_TOKEN"],
        "anarchy_category_id": int(environ["DISCORD_ANARCHY_CATEGORY"]),
        "anarchy_full_log_id":
            int(environ["DISCORD_FULL_LOG_CHANNEL"])
            if "DISCORD_FULL_LOG_CHANNEL" in environ and len(environ["DISCORD_FULL_LOG_CHANNEL"]) > 0
            else None,
        "anarchy_anon_log_id":
            int(environ["DISCORD_ANON_LOG_CHANNEL"])
            if "DISCORD_ANON_LOG_CHANNEL" in environ and len(environ["DISCORD_ANON_LOG_CHANNEL"]) > 0
            else None,
    }


load_dotenv()
config = parse_config_from_env()
