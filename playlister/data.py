from datetime import date
from csv import reader, writer
from typing import Iterable, Dict, List, Optional

from . import Config, log
from .entities import Track, TrackId, SpotifyTrack


class TableError(Exception):
    pass


class Table:
    instance: Optional['Table'] = None

    def __new__(cls):
        if cls.instance:
            return cls.instance
        instance = super().__new__(cls)
        cls.instance = instance
        return instance

    def __init__(self):
        self.index: Dict[TrackId, Track] = {}
        self.tracks: List[Track] = []
        self.path = Config.path.parent / 'data.csv'
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
        with open(self.path) as tracks:
            for track in reader(tracks):
                artist, title, *spotify, timeline = track
                timeline = [date.fromisoformat(d) for d in timeline.split()]
                self.tracks.append(
                    Track(
                        artist=artist,
                        title=title,
                        spotify=SpotifyTrack(*spotify),
                        timeline=timeline))

    def write(self):
        log.info('Writing track table')
        spotify_attrs = SpotifyTrack.__annotations__.keys()
        rows = []
        for track in self.tracks:
            spotify = ([getattr(track.spotify, attr) for attr in spotify_attrs]
                       if track.spotify else [''] * len(spotify_attrs))
            timeline = ' '.join([str(day) for day in track.timeline])
            rows.append([track.artist, track.title, *spotify, timeline])
        with open(self.path, 'w', newline='') as output:
            writer(output).writerows(rows)
