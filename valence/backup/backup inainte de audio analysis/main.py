import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from scipy.stats import expon
from scipy.stats import lognorm
from scipy.stats import norm
import math
from scipy import stats
import csv
import numpy as np
import copy


# Replace these with your own credentials
client_id = 'e6bdbe153e794797ad80dea613c1c324'
client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_related_artists(artist_id):
    """Get the related artists for a given artist"""
    results = sp.artist_related_artists(artist_id)
    #print(results['artists'][0]['name'])
    return [artist['id'] for artist in results['artists']]

def mean_feature(audio_features):
    feature_means = {}
    for track in audio_features:
        if track is None:
            continue
        for feature, value in track.items():
            if feature != "type" and feature != "id" and feature != "uri" and feature != "track_href" and feature != "analysis_url" and feature != "duration_ms" and feature != "time_signature":
                if feature in feature_means:
                    feature_means[feature].append(float(value))
                else:
                    feature_means[feature] = [float(value)]
    for feature in feature_means:
        #print(feature, feature_means[feature], sum(feature_means[feature]))
        feature_means[feature] = np.sum(feature_means[feature]) / len(feature_means[feature])
    return feature_means

def euclidean_distance(x, y):
    keywords = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
    norm = 0
    for keyword in keywords:
        if keyword in x and keyword in y:
            norm += (x[keyword] - y[keyword]) ** 2
    return math.sqrt(norm)


def euclidian_distance_similarity(artist1, artist2):
    artist_1_name = artist1['band_name']
    artist_2_name = artist2['band_name']

    # Get the top tracks for each artist
    artist_1_tracks = sp.search(q='artist:' + artist_1_name, type='track', limit=40)['tracks']['items']
    artist_1_top_track_ids = [track['id'] for track in artist_1_tracks]

    artist_2_tracks = sp.search(q='artist:' + artist_2_name, type='track', limit=40)['tracks']['items']
    artist_2_top_track_ids = [track['id'] for track in artist_2_tracks]

    # Get the audio features for each artist's top tracks
    artist_1_audio_features = sp.audio_features(artist_1_top_track_ids)
    artist_2_audio_features = sp.audio_features(artist_2_top_track_ids)

    artist_1_mean_features = mean_feature(artist_1_audio_features)
    artist_2_mean_features = mean_feature(artist_2_audio_features)

    similarity_score = euclidean_distance(artist_1_mean_features, artist_2_mean_features)
    return similarity_score

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def calculate_similarity(artist1, artist2, ed_score, sensitivity):
    """Calculate a similarity score between two artists"""
    artist1_id = artist1['id']
    artist2_id = artist2['id']
    artist1_related = set(get_related_artists(artist1_id))
    artist2_related = set(get_related_artists(artist2_id))
    common_artists = artist1_related.intersection(artist2_related)
    if(len(artist1_related.union(artist2_related)) == 0):
        related_score = 0
    else:
        related_score = len(common_artists) / len(artist1_related.union(artist2_related))

    artist1_genres = set(sp.artist(artist1_id)['genres'])
    artist2_genres = set(sp.artist(artist2_id)['genres'])

    copy_artist1_genres = artist1_genres.copy()
    copy_artist2_genres = artist2_genres.copy()

    #print(artist1_genres, artist2_genres)
    for genre in copy_artist1_genres:
        genre_words = genre.split()
        if len(genre_words) > 1:
            artist1_genres.remove(genre)
            for word in genre_words:
                artist1_genres.add(word)
    
    for genre in copy_artist2_genres:
        genre_words = genre.split()
        if len(genre_words) > 1:
            artist2_genres.remove(genre)
            for word in genre_words:
                artist2_genres.add(word)

    #print(artist1_genres, artist2_genres)
    common_genres = artist1_genres.intersection(artist2_genres)
    if(len(artist1_genres.union(artist2_genres)) == 0):
        genre_score = 0
    else:
        genre_score = len(common_genres) / len(artist1_genres.union(artist2_genres))

    limit_ = 50

    #print(artist1['band_name'], artist2['band_name'])
    if artist1_genres is None or artist2_genres is None:
        genre_score = 0
    else:
        songs_a1_id = []
        songs_a2_id = []
        for song in artist1['songs']:
            songs_a1_id.append(song['song_id'])
        for song in artist2['songs']:
            songs_a2_id.append(song['song_id'])
        #print(song1_id, song2_id, artist1['id'], artist2['id'], list(artist1_genres), list(artist2_genres))
        recommendations_song1 = sp.recommendations(seed_artists=[artist1['id']], seed_tracks=songs_a1_id[:2], seed_genres=list(copy_artist1_genres)[:2], limit=limit_)
        recommendations_song2 = sp.recommendations(seed_artists=[artist2['id']], seed_tracks=songs_a2_id[:2], seed_genres=list(copy_artist2_genres)[:2], limit=limit_)

    # for rec in recommendations_song1['tracks']:
    #     print(rec['artists'][0]['name'], rec['name'])

    # print("--------------------------------------------------")
    # for rec in recommendations_song2['tracks']:
    #     print(rec['artists'][0]['name'], rec['name'])
    # print("--------------------------------------------------")
    common_rec_songs = 0
    for i in range(limit_):
        song1 = recommendations_song1['tracks'][i]
        song1_name = song1['name']
        artist1_name = song1['artists'][0]['name']
        for j in range(limit_):
            song2 = recommendations_song2['tracks'][j]
            song2_name = song2['name']
            artist2_name = song2['artists'][0]['name']
            if artist1_name + " " + song1_name == artist2_name + " " + song2_name:
                common_rec_songs += 1
                #print(artist1_name + " " + song1_name + " " + artist2_name + " " + song2_name)

    #print(common_rec_songs)

    favorite_points = 0
    for track in recommendations_song2['tracks']:
        for song in artist1['songs']:
            if track['name'] == song['song_name']:
                favorite_points += 5
    
    for track in recommendations_song1['tracks']:
        for song in artist2['songs']:
            if track['name'] == song['song_name']:
                favorite_points += 5
    
    #print(favorite_points)
    # print("--------------")
    # print(artist1.get('band_name'))
    # print(artist2.get('band_name'))
    # print(genre_score)
    # print(related_score)
    # print(common_rec_songs)
    # print(favorite_points)

    vals = [genre_score, related_score, common_rec_songs, favorite_points, sensitivity-ed_score]
    weights = [0.3, 0.1, 0.1, 0.1, 0.4]
    k = 0.9
    a = 3

    f_genre_score = sigmoid(k*(2*(vals[0]+vals[1]+vals[2])-a))
    w_ed = copy.copy(weights[4])
    w_ed = f_genre_score * w_ed
    weights[4] = w_ed

    # print(vals)
    # print(weights)

    similarity_score = np.sum([x*y for x,y in zip(vals, weights)])
    return similarity_score * 100

def band_dict(songs):
    bands = {}
    for song in songs:
        band_name = song['track']['artists'][0]['name']
        if band_name not in bands:
            bands[band_name] = {}
            attrs = {}
            attrs["id"] = song['track']['artists'][0]['id']
            attrs["band_name"] = band_name
            bands[band_name] = attrs
        if "songs" not in bands[band_name]:
            attrs['songs'] = []
            song_dict = {}
            song_dict["song_name"] = song['track']['name']
            song_dict["song_id"] = song['track']['id']
            song_dict["release_date"] = song['track']['album']['release_date']
            attrs['songs'].append(song_dict)
        else:
            song_dict = {}
            song_dict["song_name"] = song['track']['name']
            song_dict["song_id"] = song['track']['id']
            song_dict["release_date"] = song['track']['album']['release_date']
            bands[band_name]['songs'].append(song_dict)
        # genre of the song
    return bands
def playlist_csv(bands):
    with open('playlist.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['band_name','genres','songs','year'])
        for band in bands:
            row = [band]
            genres = list(set(sp.artist(bands[band]['id'])['genres']))
            row.append(str(genres))
            songs = []
            for song in bands[band]['songs']:
                songs.append(song['song_name'])
            row.append(str(songs))
            release_dates = []
            for song in bands[band]['songs']:
                release_dates.append(song['release_date'])
            row.append(str(release_dates))
            writer.writerow(row)
    f.close()

def write_to_csv(band1,band2,score):
    with open('similarity_test.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([band1,band2,score])
    f.close()

# playlist_csv(bands)

# print(bands)

def run_test():
    playlists = ["6lMwBloRrv8QJaK5IkuIyn","2m9IehM3nSffOqFTpEza1t","4HBEjovyMpQwc62dIBcpbn"]
    playlist_id = 'spotify:playlist:' + playlists[1]
    results = sp.playlist(playlist_id, fields="tracks,next")
    tracks = results['tracks']

    #print(results)

    songs = tracks['items']
    bands = band_dict(songs)
    print(bands)

    #print(songs[0]['track'])
    # song1_id = songs[0]['track']['id']
    # song2_id = songs[1]['track']['id']
    # print(song1_id, song2_id)
    # recommendations = sp.recommendations(seed_tracks=[song1_id], limit=50)

    # for rec in recommendations['tracks']:
    #     print(rec['artists'][0]['name'], rec['name'])

    #print(recommendations)
    keys = list(bands.keys())
    max_score = 0
    sensitivity = 10
    for i in range(len(keys)):
        for j in range(i+1,len(keys)):
            it = 1
            sum = 0
            # distanta euclidiana trebuie calculata o singura data, salvam API call-uri
            ed_score = euclidian_distance_similarity(bands[keys[i]], bands[keys[j]])
            for k in range(it):
                sum += calculate_similarity(bands[keys[i]], bands[keys[j]],ed_score,sensitivity)
            score = sum / it
            # original
            # print("Band "+ keys[i] + " and band " + keys[j] + " have the similarity score " + str(score) + "\n")
            
            # works ok
            # print("Band "+ keys[i] + " and band " + keys[j] + " have the similarity score " + str(norm.cdf(score)) + "\n")
            
            # print("Band "+ keys[i] + " and band " + keys[j] + " have the similarity score " + str(lognorm.cdf(x=200, scale=(200-score))) + "\n")
            
            
            print("Band "+ keys[i] + " and band " + keys[j] + " have the similarity score " + str(score) + "\n")
            write_to_csv(keys[i],keys[j],score)


        # print("-------------------------------")
        # print("Band "+ keys[i] + " and band " + keys[j] + " are " + str(calculate_similarity(bands[keys[i]], bands[keys[j]])) + "%% similar")
        # print("-------------------------------")

    # print(calculate_similarity(artist1, artist2))

if __name__ == "__main__":
    run_test()