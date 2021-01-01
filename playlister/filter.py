from dateparser import parse
from typing import Iterable, List, Tuple
from rich.console import Console
from rich.table import Table, Column
from difflib import SequenceMatcher

from .tracks import Track


Tracks = Iterable[Track]


def sort_by_frequency(tracks: Tracks) -> Tracks:
    return sorted(tracks, key=lambda t: len([p for p in t.timeline]), reverse=True)


def sort_by_similarity(tracks: Iterable[Track], field: str) -> Iterable[Track]:
    assert field in ["artist", "title"], "Invalid field"
    scores: List[Tuple[float, Track]] = []
    for track in tracks:
        if not track.spotify:
            continue
        scores.append(
            (
                SequenceMatcher(
                    None, getattr(track, field), getattr(track.spotify, field)
                ).ratio(),
                track,
            )
        )
    return [track for score, track in sorted(scores, key=lambda s: s[0])]


def timeline(tracks: Iterable[Track]):
    pass


def song(tracks: Tracks, name: str):
    return (track for track in tracks if track.title == name)


def artist(tracks: Tracks, name: str) -> Tracks:
    return (track for track in tracks if track.artist == name)


def since(tracks: Tracks, date: str) -> Tracks:
    limit = parse(date)
    if not limit:
        raise ValueError(f"{date} is not a valid date")
    for track in tracks:
        for play_date in reversed(track.timeline):
            if play_date > limit:
                yield track


def matched(tracks: Tracks) -> Tracks:
    return (track for track in tracks if track.spotify)


def unmatched(tracks: Tracks):
    return (track for track in tracks if not track.spotify)
