from re import findall
from urllib3 import HTTPConnectionPool
from typing import Iterable, Dict, List

from . import Config, log
from .entities import Track


class TableError(Exception):
    pass


class Table:
    __instance__ = None

    def __new__(cls, name, bases, namespace):
        if cls.__instance__:
            return cls.__instance__
        instance = super().__new__(cls, name, bases, namespace)
        cls.__instance__ = instance
        return instance

    def __init__(self):
        self.index: Dict[int, Track] = {}
        self.tracks: List[Track] = []
        self.path = Config.path.parent / 'data.csv'
        if self.path.exists():
            self.read()

    def __getitem__(self, track_id: int) -> Track:
        try:
            return self.index[track_id]
        except KeyError:
            raise TableError('No such track in table')

    def __contains__(self, track: Track) -> bool:
        return track.id in self.index

    def __iter__(self) -> Iterable[Track]:
        return self.tracks.__iter__()

    def __len__(self):
        return len(self.tracks)

    def read(self):
        with open(self.path) as data:
            self.tracks = data.readlines()

    def write(self):
        with open(self.path, 'w') as output:
            output.write(self.tracks)

    def add(self, track: Track):
        if track not in self:
            self.tracks.append(track)
            self.index[track.id] = track


class TrackTable:
    columns = [
        'id', 'title', 'artist', 'spotify.id', 'spotify.title',
        'spotify.artist', 'spotify.album', 'active'
    ]

    def write(self):
        pass

    def read(self):
        pass


class TimelineTable:
    columns = ['track', 'date']
