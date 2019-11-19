from html.parser import unescape
from datetime import date
from hashlib import md5
from re import sub, IGNORECASE
from typing import Optional, List
from dataclasses import dataclass

from . import today
from .data import Table


@dataclass
class SpotifyTrack:
    id: str
    title: str
    artist: str
    album: str


class Track:
    title: str
    artist: str
    spotify: Optional[SpotifyTrack]
    timeline: List[date]
    active: bool = False

    def __new__(self, name, bases, namespace) -> 'Track':
        table = Table()
        track_id = 0
        if track_id in table:
            return table[track_id]
        return super().__new__(name, bases, namespace)

    def __init__(self, artist: str, title: str):
        self.title = title
        self.artist = artist
        self.timeline = [today]
        self.active = False

    def __hash__(self) -> int:
        return int(
            md5(bytes(self.artist + self.title, 'utf8')).hexdigest(), 16)

    def __repr__(self) -> str:
        return f'Track(artist={self.artist}, title={self.title})'

    def __str__(self) -> str:
        return f'{self.artist} - {self.title}'

    @property
    def id(self) -> int:
        if not hasattr(self, '__id__'):
            self.__id__ = hash(self)
        return self.__id__

    @property
    def simplified_title(self) -> str:
        return self.sanitize(self.title)

    @property
    def simplified_artist(self) -> str:
        return self.sanitize(self.artist)

    @staticmethod
    def sanitize(line: str) -> str:
        line = unescape(line)
        line = sub(r'\(.*?\)', ' ', line)
        line = sub('".*?"', ' ', line)
        line = sub('[/\\-]', ' ', line)
        line = sub(r'[^\w\']', ' ', line)
        line = sub(' and ', ' ', line, flags=IGNORECASE)
        line = sub(r'\s+', ' ', line)
        return line.split(' feat. ', 1)[0].strip()

    def played(self):
        if self.timeline[-1] != today:
            self.timeline.append(today)
