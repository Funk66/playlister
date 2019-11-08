import logging
from spotipy import Spotify
from spotipy.util import prompt_for_user_token
from typing import Any, List
from csv import reader, writer
from re import findall, sub, IGNORECASE
from urllib3 import PoolManager
from datetime import date as dt
from html import parser
# from spotipy import Spotify, util, client

CSV = 'radiss.csv'
TODAY = dt.today()
HTTP = PoolManager()


class ParserError(Exception):
    pass


class DB:
    def __init__(self):
        with open(CSV) as csv:
            self.tracks = {
                row[1] + row[2]: Track(row) for row in reader(csv).readlines()
            }

    def download(self):
        logging.info('Fetching page')
        with open('page.html') as p:
            html = ''.join(p.readlines())
        # page = HTTP.request('GET',
        # 'http://www.radioswissjazz.ch/en/music-programme/search')
        # html = page.data.decode()
        regex = '<span class="{}">([\W\w\s]*?)</span>'
        artists = findall(regex.format("artist"), html)
        titles = findall(regex.format("titletag"), html)
        if len(artists) != len(titles):
            raise ParserError(
                "Found {len(artists)} artists and {len(titles)} titles")
        for i in len(artists):
            track = Track(artists[i], titles[i], row=len(self.tracks) + 1)
            self.tracks.append(track)

    @property
    def spotify(self):
        if not hasattr(self, "_spotify"):
            token = prompt_for_user_token("funkadelico")
            self._spotify = Spotify(auth=token)
        return self._spotify

    def update(self):

        uris = [track.uri for track in self.tracks if track.date is TODAY]
        Spotify.update(uris)

    def save(self):
        with open(CSV) as csv:
            writer(self.tracks)


class Spotify:
    instance = None

    @staticmethod
    def client():
        if not Spotify.instance:
            token = prompt_for_user_token("funkadelico")
            Spotify.instance = Spotify(auth=token)
        return Spotify.instance

    def search(cls, artist, title):
        q = f'{title} artist:{artist}'
        return Spotify.instance.search(q, limit=1)


class Track(list):
    id: int
    artist_web: str
    title_web: str
    artist_query: str
    title_query: str
    artist_spotify: str
    title_spotify: str
    date: dt
    active: bool
    uri: str
    columns = ['id', 'artist_web', 'title_web', 'artist_query', 'title_query',
               'artist_spotify', 'title_spotify', 'date', 'active', 'uri']

    def __init__(self, data: List[Any]):
        super().__init__(data)
        if len(data) == 3:
            self.artist_query, self.title_query = self.clean(data[1:2])
            self.date = TODAY
            match = Spotify.search(self.artist_query, self.title_query)
            for key, value in match.items():
                setattr(self, key, value)
        elif len(data) == len(self.columns):
            self.id = int(self.id)
            self.active = self.active == 'True'
        else:
            raise ValueError(f'Got list of length {len(data)}')

    def __getattr__(self, key):
        try:
            return self[self.columns.index(key)]
        except ValueError:
            raise AttributeError(f'{key} is not an attribute of A')

    def __setattr__(self, key, value):
        try:
            self[self.columns.index(key)] = value
        except ValueError:
            raise AttributeError(f'{key} is not an attribute of A')

    @staticmethod
    def clean(line):
        line = parser.unescape(line)
        line = sub(r'\(.*?\)', ' ', line)
        line = sub('".*?"', ' ', line)
        line = sub('[/\\-]', ' ', line)
        line = sub('[^\w\']', ' ', line)
        line = sub(' and ', ' ', line, flags=IGNORECASE)
        line = sub(r'\s+', ' ', line)
        return line.split(' feat. ', 1)[0].strip()


class Spotify:
    @classmethod
    def search(self, artist, title):
        result = {}
        # Return empty strings if not found
        # self.artist_spotify = data['artists'][0]['name']
        # self.title_spotify = data['name']
        # self.uri = data['uri']
        # self.active = self.uri != ''
        return result['tracks']['items'][0]

    @classmethod
    def update(self, uris: List[str]):
        pass


def load():
    request = Request(headers={'Authorization': 'Bearer {token}'})

    token = util.prompt_for_user_token(
        username=conf['username'],
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
            conf['username'], conf['playlist_id'], tracks[i:i + 100])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    db = []
    load_csv(db)
    load_web(db)
    for artist, title in playlist:
        print(f'{artist} - {title}')
