from typing import Iterable, List
from rich.console import Console
from rich.table import Table, Column

from .tracks import Track


console = Console()
Tracks = Iterable[Track]


def play_count(tracks: Tracks):
    table = Table("Artist", "Title", Column(header="Count", style="blue"))
    for track in tracks:
        table.add_row(track.artist, track.title, str(len(track.timeline)))
    console.print(table)


def compare_fields(tracks: Tracks, field: str):
    table = Table("Radio", "Spotify", title=field.capitalize())
    for track in tracks:
        if not track.spotify:
            continue
        table.add_row(getattr(track, field), getattr(track.spotify, field))
    console.print(table)
