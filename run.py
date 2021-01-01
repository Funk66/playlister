from datetime import date
from re import search
from time import sleep

from playlister.client import Table, Channel, Spotify


red_cross = "\033[91m\u2717\033[0m"
green_check = "\033[92m\u2713\033[0m"

spotify = Spotify()
pop = Table(Channel.jazz)
print(f"Pop: {len([_ for _ in pop.unmatched()])}/{len(pop.tracks)}")
print("# Top 10:")
for track in pop.most_played()[:10]:
    sign = green_check if track.spotify else red_cross
    print(f"{sign} {len(track.timeline): <3} || {track}")
print("# Top 10 (month):")
for track in pop.most_played(date(2020, 10, 1))[:10]:
    total = len([_ for _ in track.timeline if _ > date(2020, 10, 1)])
    sign = green_check if track.spotify else red_cross
    print(f"{sign} {total: <3} || {track}")
# jazz = Table(Channel.jazz)
# classic = Table(Channel.classic)
# modified = 0
# for track in classic.unmatched():
    # print(track)
    # if (match := search('"(.*?)"', track.title)):
        # if (result := spotify.search(title=match.group(1), artist=track.artist)):
            # print(f"{result.artist} - {result.title} {green_check}")
            # track.spotify = result
            # modified += 1
            # sleep(0.5)
# classic.write()
