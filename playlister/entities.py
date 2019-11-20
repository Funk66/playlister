from datetime import date
from re import sub, IGNORECASE
from typing import Optional, List, Any, Tuple
from dataclasses import dataclass

from . import today


TrackId = Tuple[str, str]


@dataclass
class SpotifyTrack:
    id: str
    title: str
    artist: str
    album: str


# class Timeline(list):
    # def append(self, day):
        # if not isinstance(day, date):
            # raise ValueError(f"Cannot add type {type(day)} to timeline")
        # last_date = self[-1]
        # if day < last_date:
            # log.warning(f"Not adding older dates to the timeline: {day}")
        # elif day != last_date:
            # super().append(day)

    # @property
    # def last(self) -> date:
        # return self[-1]


class Track:
    def __init__(self, artist: str, title: str):
        self.title = title
        self.artist = artist
        self.active = False
        self.timeline: List[date] = [today]
        self.spotify: Optional[SpotifyTrack] = None

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
            if not obj:
                return ''
        return obj

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
        # line = sub(r'\W', ' ', line)
        # line = sub(r' \w ', ' ', line)
        line = sub(r'\s+', ' ', line)
        return line.split(' feat. ', 1)[0].strip()

    def played(self):
        if self.timeline[-1] != today:
            self.timeline.append(today)
