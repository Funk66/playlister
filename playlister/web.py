from enum import Enum
from urllib3 import HTTPConnectionPool
from re import findall

from . import log
from .data import Table
from .entities import Track
from .spotify import Spotify


class Channel(Enum):
    jazz = 'jazz'
    pop = 'pop'


def update(self, channel: Channel):
    table = Table()
    spotify = Spotify()
    total = len(table)
    log.info('Downloading playlist')
    page = HTTPConnectionPool().request(
        'GET', 'http://www.radioswiss{channel}.ch/en/music-programme/search')
    html = page.data.decode()
    regex = r'<span class="{}">([\W\w\s]*?)</span>'
    artists = findall(regex.format("artist"), html)
    titles = findall(regex.format("titletag"), html)
    for artist, title in zip(artists, titles):
        track = Track(artist=artist, title=title)
        if track in table:
            track = table[track.id]
            track.played()
        else:
            track.spotify = spotify.search(track.simplified_artist,
                                           track.simplified_title)
            table.add(track)
    log.info(f"Got {len(self) - total} new tracks")
