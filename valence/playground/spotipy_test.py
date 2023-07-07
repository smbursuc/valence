import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Replace these with your own credentials
client_id = 'e6bdbe153e794797ad80dea613c1c324'
client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

artist_genres = list(sp.artist("1QpYiCxy3p5Wz7HtomBqHU")['genres'])

print(artist_genres)

