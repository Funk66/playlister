import logging
from re import sub
from urllib3 import PoolManager
from datetime import date
from html import parser
from urllib.request import Request, urlopen
from spotipy import Spotify, util, client


class Track:
    date = date.today()
    artist: str
    title: str
    spotify: bool
    playlist: bool  # old ones = False


def clean(line):
    line = sub(r'[\[|\(][^)]*[\]|\)]', '', line).strip()
    return line.split(' feat. ', 1)[0].replace('&#39;', "'")


def get():
    logging.info('Fetching page')
    http = PoolManager()
    page = http.request('GET', 'http://www.radioswissjazz.ch/en/music-programme')
    matches = findall('<span class="titletag">([\w\W]+)</span>*<span class="artist">()</span>')

    lines = page.readlines()
    logging.info('Parsing')
    n = 0
    tracks = []
    while n < len(lines):
        line = lines[n].strip()
        if line.startswith(b'<span class="titletag">'):
            title = clean(line[23:-7].decode())
            n += 4
            artist = clean(parser.unescape(lines[n].decode()))
            tracks.append((artist, title))
        n += 1


def load():
    request = Request(headers={'Authorization': 'Bearer {token}'})

    token = util.prompt_for_user_token(username=conf['username'],
                                       scope=conf['scopes'],
                                       client_id=conf['client_id'],
                                       client_secret=conf['client_secret'],
                                       redirect_uri=conf['redirect_uri'])
    spotify = Spotify(auth=token)

    good = '\033[92m\u2713\033[0m'
    fail = '\033[91m\u2717\033[0m'
    tracks = []
    try:
      for artist, song in music:
          try:
              query = f'artist:{artist}+title{title}'.replace(' ', '+')
              result = spotify.search(query, limit=1)
          except client.SpotifyException:
              pass
          if result['tracks'] and result['tracks']['items']:
              tracks.append(result['tracks']['items'][0]['id'])
              logging.info('{} {} - {}'.format(good, artist, song))
          else:
              logging.info('{} {} - {}'.format(fail, artist, song))
    except KeyboardInterrupt:
      pass

    logging.info('Updating paylist...')
    for i in range(0, len(tracks), 100):
        spotify.user_playlist_replace_tracks(
            conf['username'],
            conf['playlist_id'],
            tracks[i:i+100]
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
