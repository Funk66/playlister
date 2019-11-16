import webbrowser
from time import time
from json import loads, dumps
from typing import List
from base64 import b64encode
from certifi import where
from urllib3 import PoolManager
from urllib.parse import urlencode

from . import Config, server, log


class Spotify:
    accounts_url = 'https://accounts.spotify.com'
    api_url = 'https://api.spotify.com/v1'
    redirect_uri = 'http://localhost:8888'

    def __init__(self, config: Config):
        if not (config.client and config.secret):
            raise Exception('Missing Spotify client credentials')
        self.config = config
        self.client = PoolManager(ca_certs=where())

    def post(self, url: str, body: dict, headers: dict = None) -> dict:
        log.debug(f'Calling {url} with {body}')
        response = self.client.request(
            'POST', self.accounts_url + url, headers=headers, body=dumps(body))
        return response
        if response.status == 304:
            log.info(f'Access denied: {response.reason}')
            self.authenticate(1)
            return self.post(url, body, auth=True)
        elif response.status != 200:
            raise ConnectionError(
                f'Failed with code {response.status}: {response.reason}')
        return loads(response.data)

    def get(self, url: str, headers: dict) -> dict:
        return {}

    @property
    def token(self) -> str:
        if not self.config.token:
            self.authorize()
        elif self.config.validity > time():
            self.refresh()
        return self.config.token

    def authorize(self) -> None:
        payload = {
            'client_id': self.config.client,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': 'playlist-modify-public',
        }
        log.info('Opening browser for authorization')
        webbrowser.open(f"{self.accounts_url}/authorize?{urlencode(payload)}")
        code = server.listen()
        self.authenticate(code)

    def authenticate(self, code: str) -> None:
        payload = {
            'redirect_uri': self.redirect_uri,
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.config.client,
            'client_secret': self.config.secret,
        }
        log.info('Authenticating client')
        response = self.post('/api/token', body=payload)
        self.config.update(
            token=response['access_token'],
            validity=time() + response['expires_in'],
            refresh=response['refresh_token'])

    def refresh(self):
        payload = {
            'refresh_token': self.token.refresh,
            'grant_type': 'refresh_token'
        }
        keys = f"{self.config.client}:{self.config.secret}"
        encoded_keys = b64encode(keys.encode("ascii")).decode("ascii")
        headers = {'Authorization': f'Basic {encoded_keys}'}
        log.info('Refreshing token')
        response = self.post('/api/token', body=payload, headers=headers)
        self.config.update(
            token=response['access_token'],
            validity=time() + response['expires_in'])

    def search(self, artist: str, title: str):
        headers = {'Authorization': f"Bearer {self.token}"}
        return self.get('/search', headers=headers)

    def add(self, tracks: List['Track']):
        pass

    def remove(self, tracks):
        pass
