from playlister import Channel
from playlister.filter import *
from playlister.output import *
from playlister.tracks import Table as DB


table = DB(Channel.jazz)
similar = sort_by_similarity(table.tracks, "artist")
compare_fields(list(similar)[:40], "artist")
