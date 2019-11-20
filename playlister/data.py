from csv import reader, writer
from typing import Iterable, Dict, List, Optional

from . import Config, log
from .entities import Track


class TableError(Exception):
    pass


class Table:
    instance: Optional['Table'] = None
    columns: List[str] = [
        'id', 'title', 'artist', 'spotify.id', 'spotify.title',
        'spotify.artist', 'spotify.album', 'active'
    ]

    def __new__(cls, name, bases, namespace):
        if cls.instance:
            return cls.instance
        instance = super().__new__(cls, name, bases, namespace)
        cls.instance = instance
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

    def add(self, track: Track) -> None:
        if not isinstance(track, Track):
            raise ValueError(f"Cannot add a {type(track)} to the table")
        if track in self:
            self.tracks.append(track)
            self.index[track.id] = track

    def read(self):
        log.info('Reading track table')
        with open(self.path) as data:
            self.tracks = data.readlines()

    def write(self):
        log.info('Writing track table')
        rows = [
            getattr(track, column)
            for track in self.tracks
            for column in self.columns
        ]
        with open(self.path, 'w') as output:
            writer(output, [self.columns] + rows)
