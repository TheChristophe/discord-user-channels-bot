### State

End-of-line, because [discord.py](https://github.com/Rapptz/discord.py) has halted development.
See [here](https://gist.github.com/Rapptz/4a2f62751b9600a31a0d3c78100287f1).

## User-channel management bot

A bot to allow users to manage channels in a configured channel category without directly granting them permissions.

This may be desirable if you require 2FA, but do not want to require every regular user to have it (or don't want them
to suffer the banner).

To run:

1. `cp .env.example .env`
    - set env variables
1. `python -m venv .venv` if you haven't
1. `pip install -r requirements.txt` if you haven't
1. `python main.py`
