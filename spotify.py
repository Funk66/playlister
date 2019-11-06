class Spotify:
    url = 'https://api.spotify.com/v1/search'

    def __init__(token):
        pass

    def search(artist, title):
        query = f'{self.url}&q=title:{title}+artist:{artist}&type=track'
        response = urlopen(query.replace(' ', '+'), )

    def add():
        pass
