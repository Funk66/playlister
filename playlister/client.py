import logging
from urllib3 import PoolManager
from re import findall

from .entities import Track


class ParserError(Exception):
    pass


TODAY = datetime.today()


class DB:
    def __init__(self):
        # load csv
        self.data = None

    def add(self, artist, title, played: bool = True):
        track_id = (artist, title)
        if track_id in self.data:
            track = self.data[track_id]
        else:
            track = Track(artist, title, track_id)
        if played and not track.timeline.today:
            track.timeline.played()

    def playlist(self):
        pass


class Timeline(list):
    """ Ordered list """
    def __init__(self, data):
        self.data = sorted(data)

    def add(self, date):
        if date <= self.data[-1]:
            raise ValueError()
        self.data.append(date)


def load():
    return


def download():
    # page = PoolManager().request('GET',
    # 'http://www.radioswissjazz.ch/en/music-programme/search')
    # html = page.data.decode()
    with open('page.html') as p:
        html = ''.join(p.readlines())
    regex = r'<span class="{}">([\W\w\s]*?)</span>'
    artists = findall(regex.format("artist"), html)
    titles = findall(regex.format("titletag"), html)
    return zip(artists, titles)


def update():
    logging.info('Fetching page')
    for artist, title in download():
        db.add(artist, title)
    # return [Track(artists[i].strip(), titles[i]) for i in range(len(artists))]
