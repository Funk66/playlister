from csv import reader, writer
from datetime import date
from re import IGNORECASE, sub
from typing import Dict, Iterable, List, Optional, Tuple

from . import Channel, Config, log
from .spotify import SpotifyTrack

TrackId = Tuple[str, str]


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
        line = sub(r'\.', '', line)
        line = sub(r'\(.*?\)', ' ', line)
        line = sub('".*?"', ' ', line)
        line = sub('[/\\-]', ' ', line)
        line = sub(r'[^\w\']', ' ', line)
        line = sub(' and ', ' ', line, flags=IGNORECASE)
        line = sub(r'\s+', ' ', line)
        return line.split(' feat ', 1)[0].strip()

    def played(self, date: date = date.today()):
        if not self.timeline:
            self.timeline.append(date)
        elif date not in self.timeline:
            for index, day in enumerate(reversed(self.timeline)):
                if day < date:
                    self.timeline.insert(-index or len(self.timeline), date)
                    break
            else:
                self.timeline.insert(0, date)


class TableError(Exception):
    pass


class Table:
    instance: Optional['Table'] = None

    def __new__(cls, *args, **kwargs):
        if cls.instance:
            return cls.instance
        instance = super().__new__(cls)
        cls.instance = instance
        return instance

    def __init__(self, channel: Channel):
        self.index: Dict[TrackId, Track] = {}
        self.tracks: List[Track] = []
        self.path = Config.path.parent / f'{channel.name}.csv'
        if self.path.exists():
            self.read()

    def __getitem__(self, track_id: TrackId) -> Track:
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
        if track not in self:
            self.tracks.append(track)
            self.index[track.id] = track

    def read(self):
        log.info('Reading track table')
        with open(self.path) as rows:
            for row in reader(rows):
                artist, title, *spotify, timeline = row
                timeline = [date.fromisoformat(d) for d in timeline.split()]
                track = Track(
                    artist=artist,
                    title=title,
                    spotify=SpotifyTrack(*spotify) if any(spotify) else None,
                    timeline=timeline)
                self.tracks.append(track)
                self.index[track.id] = track

    def write(self):
        log.info('Writing track table')
        spotify_attrs = SpotifyTrack.__annotations__
        rows = []
        for track in self.tracks:
            spotify = ([
                getattr(track.spotify, attr) for attr in spotify_attrs
            ] if track.spotify else [''] * len(spotify_attrs))
            timeline = ' '.join([str(day) for day in track.timeline])
            rows.append([track.artist, track.title, *spotify, timeline])
        with open(self.path, 'w', newline='') as output:
            writer(output).writerows(rows)

    @property
    def last_date(self) -> date:
        day = date(2000, 1, 1)
        for track in self.tracks:
            if track.timeline[-1] > day:
                day = track.timeline[-1]
        return day
