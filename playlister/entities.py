from datetime import date
from re import sub, IGNORECASE
from typing import Optional, List, Tuple
from dataclasses import dataclass

from . import today

TrackId = Tuple[str, str]


@dataclass
class SpotifyTrack:
    artist: str
    title: str
    album: str
    uri: str


class Track:
    def __init__(self,
                 artist: str,
                 title: str,
                 spotify: Optional[SpotifyTrack] = None,
                 timeline: Optional[List[date]] = None):
        self.artist = artist
        self.title = title
        self.timeline = timeline or []
        self.spotify: Optional[SpotifyTrack] = spotify

    def __repr__(self) -> str:
        return f'Track(artist={self.artist}, title={self.title})'

    def __str__(self) -> str:
        return f'{self.artist} - {self.title}'

    def __eq__(self, obj) -> bool:
        if hasattr(obj, 'id'):
            return self.id == obj.id
        return False

    @property
    def id(self) -> TrackId:
        return (self.artist, self.title)

    @property
    def simplified_title(self) -> str:
        return self.sanitize(self.title)

    @property
    def simplified_artist(self) -> str:
        return self.sanitize(self.artist)

    @staticmethod
    def sanitize(line: str) -> str:
        line = sub(r'\(.*?\)', ' ', line)
        line = sub('".*?"', ' ', line)
        line = sub('[/\\-]', ' ', line)
        line = sub(r'[^\w\']', ' ', line)
        line = sub(' and ', ' ', line, flags=IGNORECASE)
        line = sub(r'\s+', ' ', line)
        return line.split(' feat. ', 1)[0].strip()

    def played(self, date: date = today):
        if not self.timeline:
            self.timeline.append(date)
        elif date not in self.timeline:
            for index, day in enumerate(reversed(self.timeline)):
                if day < date:
                    self.timeline.insert(-index or len(self.timeline), date)
