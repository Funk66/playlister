from logging import basicConfig
from datetime import date, timedelta
from argparse import ArgumentParser, Namespace

from . import Config, today, log
from .web import update, Channel
from .stats import Strategy


def arguments() -> Namespace:
    parser = ArgumentParser(
        prog='Playlister',
        description='Create Spotify playlists from internet radio channels')
    parser.add_argument('-v', help='Verbose logging', dest='debug')
    subparser = parser.add_subparsers(required=True, dest='command')
    download_parser = subparser.add_parser(
        'download', help='Get playlist from the website')
    download_parser.add_argument(
        '-d',
        '--date',
        help='Date of the broadcast in ISO format',
        default=str(today))
    download_parser.add_argument(
        '-c',
        '--channel',
        help='Radio channel',
        required=True,
        type=Channel)
    sync_parser = subparser.add_parser(
        'sync', help='Recalculate and update the Spotify playlist')
    sync_parser.add_argument(
        '-s',
        '--strategy',
        help='Selection model for the new playlist',
        type=Strategy)
    return parser.parse_args()


def run() -> None:
    args = arguments()
    basicConfig(level=10 if args.debug else 20, format='%(message)s')
    if not (Config.client and Config.secret):
        client = input('Client id: ')
        secret = input('Client secret: ')
        Config.update(client=client, secret=secret)
    if args.command == 'sync':
        if not (Config.channel[args.channel]):
            Config.channel.update({args.channel: input('Playlist URI: ')})
        # sync(args.strategy)
    else:
        if args.date:
            try:
                args.date = date.fromisoformat(args.date)
            except ValueError:
                return log.error(f"{args.date} is not a valid date")
            if args.date < today - timedelta(days=30) or args.date > today:
                return log.error("Date out of range")
        update(args.channel, args.date or today)
