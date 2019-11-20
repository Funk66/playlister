from enum import Enum
from html.parser import unescape
from datetime import date
from urllib3 import connection_from_url
from re import findall

from . import log, today
from .data import Table
from .entities import Track
from .spotify import Spotify


class Channel(Enum):
    jazz = 'jazz'
    pop = 'pop'


def update(channel: Channel, date: date = today):
    table = Table()
    spotify = Spotify()
    total = len(table)
    log.info('Downloading playlist')
    url = connection_from_url(f'http://www.radioswiss{channel.name}.ch')
    page = url.request(
        'GET', f'/en/music-programme/search/{date.year}{date.month}{date.day}')
    html = unescape(page.data.decode())
    regex = r'<span class="{}">\n\s+([\W\w\s]*?){}\n\s+</span>'
    artists = findall(regex.format('artist', ''), html)
    titles = findall(regex.format('titletag', r'\s+'), html)
    for artist, title in zip(artists, titles):
        track = Track(artist=artist, title=title)
        if track in table:
            track = table[track.id]
            track.played()
        else:
            track.spotify = spotify.search(track.simplified_artist,
                                           track.simplified_title)
            table.add(track)
    log.info(f"Got {len(table) - total} new tracks")
    table.write()
