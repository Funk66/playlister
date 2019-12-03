from argparse import ArgumentParser, Namespace
from datetime import date, timedelta
from html.parser import unescape
from logging import basicConfig
from re import findall
from subprocess import run

from urllib3 import connection_from_url

from . import Channel, Config, log
from .spotify import Spotify
from .tracks import Table, Track

today = date.today()
red_cross = '\033[91m\u2717\033[0m'
blue_arrow = '\033[94m\u279a\033[0m'
green_check = '\033[92m\u2713\033[0m'


def arguments() -> Namespace:
    parser = ArgumentParser(
        prog='Playlister',
        description='Create Spotify playlists from internet radio channels')
    parser.add_argument('-v', help='Verbose logging', dest='debug')
    parser.add_argument(
        '-c', nargs='+', help='Radio channels', type=Channel, dest='channel')
    return parser.parse_args()


def download(table: Table,
             spotify: Spotify,
             channel: Channel,
             date: date = today) -> None:
    total = len(table)
    log.info(f'Downloading playlist for {date}')
    url = connection_from_url(f'http://www.radioswiss{channel.name}.ch')
    page = url.request(
        'GET',
        f'/en/music-programme/search/{date.year}{date.month:02}{date.day:02}')
    html = unescape(page.data.decode())
    regex = r'<span class="{}">\n\s+([\W\w\s]*?){}\n\s+</span>'
    artists = findall(regex.format('artist', ''), html)
    titles = findall(regex.format('titletag', r'\s+'), html)
    if channel is Channel.classic:
        artists, titles = titles, artists
    for artist, title in zip(artists, titles):
        track = Track(artist=artist, title=title)
        if track in table:
            track = table[track.id]
            log.info(f"{blue_arrow} {track}")
        else:
            track.spotify = spotify.search(track.simplified_artist,
                                           track.simplified_title)
            icon = green_check if track.spotify else red_cross
            log.info(f"{icon} {track}")
            table.add(track)
        track.played(date)
    log.info(f"Got {len(table) - total} new tracks")
    table.write()


def git(*command: str) -> None:
    log.info(f"{command[0].title()}ing changes")
    ps = run(["git", *command], cwd=Config.path.parent, capture_output=True)
    output = ps.stdout.decode('utf8')
    if ps.returncode != 0:
        log.error(output)
        exit()
    log.debug(output)


def update() -> None:
    args = arguments()
    basicConfig(level=10 if args.debug else 20, format='%(message)s')
    if not (Config.client and Config.secret):
        client = input('Client id: ')
        secret = input('Client secret: ')
        Config.update(client=client, secret=secret)
    git('pull')
    for channel in (args.channel or Channel):
        if channel.name not in Config.playlists:
            Config.playlists.update({args.channel: input('Playlist URI: ')})
        table = Table(channel)
        spotify = Spotify()
        limit_date = today - timedelta(days=30)
        day = max(limit_date, table.last_date + timedelta(days=1))
        while day <= today:
            download(table, spotify, channel, day)
            day += timedelta(days=1)
        spotify.replace(Config.playlists[channel.name], table.selection())
    git('commit', '-am', f"Seeding {today}")
    git('push')
