from html.parser import unescape
from datetime import date
from hashlib import md5
from re import sub, IGNORECASE
from typing import Optional, List, Any
from dataclasses import dataclass

from . import today


@dataclass
class SpotifyTrack:
    id: str
    title: str
    artist: str
    album: str


class Track:
    def __init__(self, artist: str, title: str):
        self.title = title
        self.artist = artist
        self.active = False
        self.timeline: List[date] = [today]
        self.spotify: Optional[SpotifyTrack] = None

    def __hash__(self) -> int:
        return int(
            md5(bytes(self.artist + self.title, 'utf8')).hexdigest(), 16)

    def __repr__(self) -> str:
        return f'Track(artist={self.artist}, title={self.title})'

    def __str__(self) -> str:
        return f'{self.artist} - {self.title}'

    def __eq__(self, obj) -> bool:
        if hasattr(obj, 'id'):
            return self.id == obj.id
        return False

    def __getattr__(self, name: str) -> Any:
        obj = self
        for attr in name.split('.'):
            obj = getattr(obj, attr)
        return obj

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
