from difflib import SequenceMatcher


def sort_by_similarity(tracks: Iterable[Track], field: str) -> Iterable[Track]:
    assert field in ["artist", "title"], "Invalid field"
    scores = []
    for track in tracks:
        if not track.spotify:
            continue
        if field == "artist":
            scores.append(SequenceMatcher(None, track.artist, track.spotify.artist).ratio(), track)
        elif field == "title":
            scores.append(SequenceMatcher(None, track.title, track.spotify.title).ratio(), track)
    return reversed(sorted(scores))
