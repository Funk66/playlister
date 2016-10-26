#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from spotipy import Spotify, util, client


scopes = ''
username = ''
client_id = ''
client_secret = ''
redirect_uri = ''
playlist_id = ''

print('Downloading...')
page = requests.get('http://www.radioswissjazz.ch/en/music-programme')
print('Parsing...')
soup = BeautifulSoup(page.text, 'html.parser')
artists = [span.text.strip() for span in soup.find_all('span', class_="artist")]
songs = [span.text.strip() for span in soup.find_all('span', class_="titletag")]
music = zip(artists, songs)

print('Starting Spotify session...')
token = util.prompt_for_user_token(username=username, scope=scopes,
                                   client_id=client_id,
                                   client_secret=client_secret,
                                   redirect_uri=redirect_uri)
spotify = Spotify(auth=token)

good = '\033[92m\u2713\033[0m'
fail = '\033[91m\u2717\033[0m'
tracks = []
try:
  for artist, song in music:
      try:
          result = spotify.search(q=' '.join([artist, song]))
      except client.SpotifyException:
          pass
      if result['tracks'] and result['tracks']['items']:
          tracks.append(result['tracks']['items'][0]['id'])
          print('{} {} - {}'.format(good, artist, song))
      else:
          print('{} {} - {}'.format(fail, artist, song))
except KeyboardInterrupt:
  pass

print('Updating paylist...')
spotify.user_playlist_replace_tracks(username, playlist_id, tracks[:100])
for i in range(100, len(tracks), 100):
    spotify.user_playlist_add_tracks(username, playlist_id, tracks[i:i+100])
print('All done')

