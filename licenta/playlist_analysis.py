import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import numpy as np
import matplotlib.pyplot as plt


client_id = 'e6bdbe153e794797ad80dea613c1c324'
client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#2m9IehM3nSffOqFTpEza1t
def playlist_analysis(playlist_id):
    playlist_uri = 'spotify:playlist:' + playlist_id
    results = sp.playlist(playlist_uri, fields="tracks,next")
    tracks = results['tracks']

    songs = tracks['items']

    with open('audio_features.json', 'r') as file:
        json_data = file.read()
    parsed_data = json.loads(json_data)

    for song in songs:
        song_id = song['track']['id']
        new_ids = []
        if song_id not in parsed_data:
            new_ids.append(song_id)
        if len(new_ids) > 0:
            features = sp.audio_features(new_ids)
            for feature in features:
                parsed_data[feature['id']] = feature
            with open('audio_features.json', 'w') as file:
                file.write(json.dumps(parsed_data))
        
    features = ["danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"]
    features_data = []
    for song in songs:
        song_id = song['track']['id']
        feature_data = []
        for feature in features:
            feature_data.append(parsed_data[song_id][feature])
        features_data.append(feature_data)

    print(features_data)
    
    k = 0
    for i in range(len(features_data)):
        plt.scatter(features_data[i][k],features[k])

    plt.show()



    
    


playlist_analysis('2m9IehM3nSffOqFTpEza1t')
        
