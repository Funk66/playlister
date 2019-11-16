from . import Config, spotify


def setup():
    config = Config()
    if not (config.client and config.secret):
        client = input('Client id: ')
        secret = input('Client secret: ')
        config.update(client=client, secret=secret)
    spotify.setup(config)
