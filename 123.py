import requests

API_KEY = 'd015dbb01ebdf8d0ac71c7cf807da392'
BASE_URL = 'http://ws.audioscrobbler.com/2.0/'


def get_artist_info(artist_name):
    params = {
        'method': 'artist.getinfo',
        'artist': artist_name,
        'api_key': API_KEY,
        'format': 'json',
    }
    response = requests.get(BASE_URL, params=params)
    return response.json()


# Exemplo de uso
artist_name = 'Coldplay'
artist_info = get_artist_info(artist_name)
print(artist_info)
