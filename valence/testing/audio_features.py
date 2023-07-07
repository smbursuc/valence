import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
import csv

client_id = 'e6bdbe153e794797ad80dea613c1c324'
client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

analysis = sp.audio_analysis('spotify:track:53QkoELbY2Vzzb4EMkFJOB')

# write analysis to csv
with open('analysis_otherworldly.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for key, value in analysis.items():
        writer.writerow([key, value])

