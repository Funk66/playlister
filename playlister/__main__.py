from . import Config
from .spotify import Spotify


if not (Config.client and Config.secret):
    client = input('Client id: ')
    secret = input('Client secret: ')
    Config.update(client=client, secret=secret)
spotify = Spotify()
track = spotify.search('sting', 'breath')
print(track)
