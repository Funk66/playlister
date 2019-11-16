from html import parser
from datetime import datetime
from hashlib import md5
from re import sub, IGNORECASE
from typing import Tuple
from dataclasses import dataclass


@dataclass
class Track:
    artist: str
    title: str
    active: bool = False
    uri: str = ''

    @property
    def id(self) -> str:
        return md5(bytes(self.artist + self.title, 'utf8')).hexdigest()

    def query(self) -> Tuple[str, str]:
        return (self.sanitize(self.artist), self.sanitize(self.title))

    def sanitize(self, line: str) -> str:
        line = parser.unescape(line)
        line = sub(r'\(.*?\)', ' ', line)
        line = sub('".*?"', ' ', line)
        line = sub('[/\\-]', ' ', line)
        line = sub('[^\w\']', ' ', line)
        line = sub(' and ', ' ', line, flags=IGNORECASE)
        line = sub(r'\s+', ' ', line)
        return line.split(' feat. ', 1)[0].strip()


@dataclass
class Event:
    track: str
    date: datetime
