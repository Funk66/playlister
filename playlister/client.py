from argparse import ArgumentParser, Namespace
from datetime import date, datetime, timedelta
from html.parser import unescape
from logging import DEBUG, INFO, basicConfig
from random import shuffle
from re import findall
from subprocess import run

from urllib3 import connection_from_url

from . import Channel, Config, log
from .spotify import Spotify
from .tracks import Table, Track

today = date.today()
red_cross = "\033[91m\u2717\033[0m"
blue_arrow = "\033[94m\u279a\033[0m"
green_check = "\033[92m\u2713\033[0m"


def arguments() -> Namespace:
    parser = ArgumentParser(
        prog="Playlister",
        description="Create Spotify playlists from internet radio channels",
    )
    parser.add_argument(
        "-v", help="Verbose logging", action="store_true", dest="verbose"
    )
    subparser = parser.add_subparsers(dest="command", required=True)
    update = subparser.add_parser("update", description="Update playlists")
    update.add_argument(
        "-w", help="Weekly update", action="store_true", dest="weekly"
    )
    fix_command = subparser.add_parser(
        "fix", description="Manually correlate Spotify tracks"
    )
    fix_command.add_argument("channel", help="Radio channel", type=Channel)
    return parser.parse_args()


def update() -> None:
    for channel in Channel:
        if channel.name not in Config.playlists:
            Config.playlists.update({channel.name: input("Playlist URI: ")})
        table = Table(channel)
        spotify = Spotify()
        limit_date = today - timedelta(days=30)
        day = max(limit_date, table.last_date + timedelta(days=1))
        while day <= today:
            download(table, spotify, channel, day)
            day += timedelta(days=1)
        spotify.replace(Config.playlists[channel.name], table.selection())
    git("commit", "-am", f"Seeding {today}")


def download(
    table: Table, spotify: Spotify, channel: Channel, date: date = today
) -> None:
    total = len(table)
    log.info(f"Downloading playlist for {date}")
    url = connection_from_url(f"http://www.radioswiss{channel.name}.ch")
    page = url.request(
        "GET", f"/en/music-programme/search/{date.year}{date.month:02}{date.day:02}"
    )
    html = unescape(page.data.decode())
    regex = r'<span class="{}">\n\s+([\W\w\s]*?){}\n\s+</span>'
    artists = findall(regex.format("artist", ""), html)
    titles = findall(regex.format("titletag", r"\s+"), html)
    if channel is Channel.classic:
        artists, titles = titles, artists
    for artist, title in zip(artists, titles):
        track = Track(artist=artist, title=title)
        if track in table:
            track = table[track.id]
            log.info(f"{blue_arrow} {track}")
        else:
            track.spotify = spotify.search(
                track.simplified_artist, track.simplified_title
            )
            icon = green_check if track.spotify else red_cross
            log.info(f"{icon} {track}")
            table.add(track)
        track.played(date)
    log.info(f"Got {len(table) - total} new tracks")
    table.write()


def fix(channel: Channel) -> None:
    table = Table(channel)
    spotify = Spotify()
    modified = False
    unmatched = [track for track in table.tracks if not track.spotify]
    shuffle(unmatched)
    while unmatched:
        track = unmatched.pop()
        try:
            print(f"{track.artist} - {track.title}")
            artist = input("Artist: ")
            title = input("Title: ")
        except KeyboardInterrupt:
            break
        tracks = spotify.search(title=title, artist=artist, limit=5)
        if not tracks:
            print("No tracks found")
            continue
        for num, match in enumerate(tracks):
            print(f"{num}. {match.artist} - {match.title}")
        try:
            selection = int(input("Selection: "))
            track.spotify = tracks[selection]
            modified = True
        except (ValueError, IndexError):
            print("Invalid selection")
            continue
    if modified:
        table.write()
        git("commit", "-am", f"Fixing tracks on the {channel.name} channel")
        git("push")


def stale(check: bool) -> None:
    if check:
        current_week = datetime.today().isocalendar()[:2]
        last_commit = git('show', '-s', '--format=%cI', verbose=False)
        last_week = datetime.fromisoformat(last_commit).isocalendar()[:2]
        if current_week <= last_week:
            log.info("Already up to date")
            exit(0)


def git(*command: str, verbose=True) -> str:
    if verbose:
        log.info(f"{command[0].title()}ing changes")
    ps = run(["git", *command], cwd=Config.path.parent, capture_output=True)
    output = ps.stdout.decode("utf8")
    if ps.returncode != 0:
        log.error(output)
        exit()
    if verbose:
        log.debug(output)
    return output.strip()


def main() -> None:
    args = arguments()
    basicConfig(level=DEBUG if args.verbose else INFO, format="%(message)s")
    if not (Config.client and Config.secret):
        client = input("Client id: ")
        secret = input("Client secret: ")
        Config.update(client=client, secret=secret)
    if args.command == "update":
        stale(args.weekly)
        git("pull")
        stale(args.weekly)
        update()
        git("push")
    elif args.command == "fix":
        fix(args.channel)
