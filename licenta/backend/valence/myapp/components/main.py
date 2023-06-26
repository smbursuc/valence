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
from . import audio_analysis
import json
import sys
import requests
import fastdtw
from scipy.spatial.distance import euclidean


# Replace these with your own credentials
client_id = 'e6bdbe153e794797ad80dea613c1c324'
client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def mean_feature(audio_features, features, distance):
    feature_means = {}
    for track in audio_features:
        if track is None:
            continue
        for feature, value in track.items():
            if feature in features:
                if feature in feature_means:
                    feature_means[feature] = np.append(feature_means[feature], float(value))
                else:
                    feature_means[feature] = np.array([float(value)])

    v = np.array([])
    for feature in feature_means:
        v = np.append(v, feature_means[feature])
    return v
    


def euclidean_distance_features(x, y, audio_features_keys):
    norm = 0
    for feature in audio_features_keys:
        if feature in x and feature in y:
            norm += (x[feature] - y[feature]) ** 2
    return math.sqrt(norm)

def cosine_similarity_features(x, y, audio_features_keys):
    norm_x = 0
    norm_y = 0
    dot_product = 0
    for feature in audio_features_keys:
        if feature in x and feature in y:
            dot_product += x[feature] * y[feature]
            norm_x += x[feature] ** 2
            norm_y += y[feature] ** 2
    return dot_product / (math.sqrt(norm_x) * math.sqrt(norm_y))


def manhattan_distance_features(x, y, audio_features_keys):
    norm = 0
    for feature in audio_features_keys:
        if feature in x and feature in y:
            norm += abs(x[feature] - y[feature])
    return norm

def minkowski_distance_features(x, y, audio_features_keys):
    norm = 0
    for feature in audio_features_keys:
        if feature in x and feature in y:
            norm += abs(x[feature] - y[feature]) ** 3
    return norm ** (1 / 3)

def euclidean_distance(x, y):
    return np.linalg.norm(x - y)
    

def cosine_similarity(x, y):
    norm_x = 0
    norm_y = 0
    dot_product = 0
    for i in range(len(x)):
        dot_product += x[i] * y[i]
        norm_x += x[i] ** 2
        norm_y += y[i] ** 2
    return dot_product / (math.sqrt(norm_x) * math.sqrt(norm_y))

def manhattan_distance(x, y):
    norm = 0
    for i in range(len(x)):
        norm += abs(x[i] - y[i])
    return norm

def minkowski_distance(x, y):
    norm = 0
    for i in range(len(x)):
        norm += abs(x[i] - y[i]) ** 3
    return norm ** (1 / 3)

def euclidian_distance_similarity(artist1_top_tracks, artist2_top_tracks, audio_features_file_data, audio_features, distance):
    artist_1_top_track_ids = [track['id'] for track in artist1_top_tracks]
    artist_2_top_track_ids = [track['id'] for track in artist2_top_tracks]

    audio_features_keys = [key for key, value in audio_features.items() if value == True]

    new_track_ids = []
    for track_id in artist_1_top_track_ids:
        if track_id not in audio_features_file_data:
            new_track_ids.append(track_id)

    
    for track_id in artist_2_top_track_ids:
        if track_id not in audio_features_file_data:
            new_track_ids.append(track_id)

    
    if len(new_track_ids) > 0:
        new_audio_features = sp.audio_features(new_track_ids)
        for track in new_audio_features:
            if track is None:
                return 10000
            else:
                audio_features_file_data[track['id']] = track
    
    with open('audio_features.json', 'a') as file:
        file.seek(0, 2) 
        file.write(json.dumps(audio_features_file_data))
        file.close()

    artist_1_audio_features = []
    for track_id in artist_1_top_track_ids:
        artist_1_audio_features.append(audio_features_file_data[track_id])

    artist_2_audio_features = []
    for track_id in artist_2_top_track_ids:
        artist_2_audio_features.append(audio_features_file_data[track_id])
    
    artist_1_mean_features = mean_feature(artist_1_audio_features, audio_features_keys, distance)
    artist_2_mean_features = mean_feature(artist_2_audio_features, audio_features_keys, distance)

    if distance == 'euclidian':
        similarity_score = euclidean_distance(artist_1_mean_features, artist_2_mean_features)
    if distance == 'cosine':
        similarity_score = cosine_similarity(artist_1_mean_features, artist_2_mean_features)
    if distance == 'manhattan':
        similarity_score = manhattan_distance(artist_1_mean_features, artist_2_mean_features)
    if distance == 'minkowski':
        similarity_score = minkowski_distance(artist_1_mean_features, artist_2_mean_features)
    if distance == 'dtw':
        similarity_score, path = fastdtw.fastdtw(artist_1_mean_features, artist_2_mean_features, dist=euclidean_distance)
    return similarity_score

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def audio_analysis_mean(aa_res, use_keys, distance):
    aa_mean = {}
    used_keys_general = ['loudness', 'time_signature', 'key', 'mode', 'tempo']
    for key in use_keys:
        if key == 'track':
            aa_mean[key] = {}
            for used_key in used_keys_general:
                aa_mean[key][used_key] = 0
        else:
            aa_mean[key] = 0
    #all_keys_general = ['num_samples', 'duration', 'sample_md5', 'offset_seconds', 'window_seconds', 'analysis_sample_rate', 'analysis_channels', 'end_of_fade_in', 'start_of_fade_out', 'loudness', 'tempo', 'tempo_confidence', 'time_signature', 'time_signature_confidence', 'key', 'key_confidence', 'mode', 'mode_confidence', 'codestring']
    new_tracks = []
    for track in aa_res:
        song_id = track['id']
        try:
            aa = sp.audio_analysis(song_id)
        except Exception as e:
            print(e)
            continue
        for key in aa_mean.keys():
            if key != 'track':
                if distance == 'dtw':
                    v_dtw = np.array([])
                for v in aa[key]:
                    v_aux = np.array([])
                    if key=='segments' or key=='sections':
                        _list = list(v.values())[2:]
                    else:
                        _list = list(v.values())
                    for value in _list:
                        if isinstance(value, list):
                            v_aux = np.append(v_aux, np.array(value))
                        else:
                            v_aux = np.append(v_aux, value)
                    if distance == 'dtw':
                        v_dtw = np.append(v_dtw, v_aux)
                    else:
                        aa_mean[key] += v_aux
                if distance == 'dtw':
                    # if not isinstance(aa_mean[key], np.ndarray):
                    #     aa_mean[key] = np.array([])
                    # max_len = max(len(v_dtw), len(aa_mean[key]))
                    # v_dtw = np.pad(v_dtw, (0, max_len - len(v_dtw)), mode='constant')
                    # aa_mean[key] = np.pad(aa_mean[key], (0, max_len - len(aa_mean[key])), mode='constant')
                    aa_mean[key] = np.append(aa_mean[key], v_dtw)
            else:
                for key in used_keys_general:
                    aa_mean['track'][key] += aa['track'][key]

    if distance == 'dtw':
        return aa_mean
    
    for key in aa_mean.keys():
        if key != 'track':
            # print("aa mean print")
            # print(aa_mean[key])
            aa_mean[key] = aa_mean[key] / len(aa_res)
        else:
            for key in used_keys_general:
                aa_mean['track'][key] = aa_mean['track'][key] / len(aa_res)
            aa_mean['track'] = np.array(list(aa_mean['track'].values()))
    return aa_mean

        

def ed_weight_function(A, B, k):
    return A+k/(abs(B)+k)


def calculate_similarity(artist2_dict, ed_score, params, distance, **kwargs):
    use_audio_features = any(value for value in params['audio_features'].values())
    use_audio_analysis = any(value for value in params['audio_analysis'].values())
    use_genre = 'artist_genres_split' in params

    #print(use_audio_features, use_audio_analysis, use_genre)

    genre_score = 0
    aa_analysis_mean = 0
    a1_aa_mean = {}

    if use_audio_analysis:
        use_keys = [k for k, v in params['audio_analysis'].items() if v == True]
    
    #print(use_keys)

    if not kwargs.get('use_cache'):
        if use_audio_analysis:
            a1_top_tracks = params['artist1_top_tracks']
            a1_aa_mean = audio_analysis_mean(a1_top_tracks, use_keys, distance)
    else:
        if use_audio_analysis:
            a1_aa_mean = params['a1_aa_mean']
    

    if use_genre:
        artist1_genres = params['artist_genres_split']
        artist2_id = artist2_dict['id']
        artist2_genres = set(sp.artist(artist2_id)['genres'])
        if len(artist2_genres) == 0:
            artist2_name = artist2_dict['band_name']
            api_key = '9cb344e010b38bd815b32d44ab77f8b2'
            url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={artist2_name}&api_key={api_key}&format=json"
            response = requests.get(url)
            data = response.json()
            genres = [tag['name'] for tag in data['artist']['tags']['tag']]
            artist2_genres = genres
        artist_genres_split = [word for item in artist2_genres for word in item.split()]
        artist2_genres = list(set(artist_genres_split))

        common_genres = artist1_genres.intersection(artist2_genres)
        if(len(artist1_genres.union(artist2_genres)) == 0):
            genre_score = 0
        else:
            genre_score = len(common_genres) / len(artist1_genres.union(artist2_genres))

    if use_audio_analysis:
        a2_top_tracks = params['artist2_top_tracks']
        if(len(a2_top_tracks) == 0):
            return 100000000
        a2_aa_mean = audio_analysis_mean(a2_top_tracks, use_keys, distance)

        for key in use_keys:
            if key != 'track':
                if 'error' in a1_aa_mean or 'error' in a2_aa_mean:
                    return 10000000
                if isinstance(a1_aa_mean[key], int) or isinstance(a2_aa_mean[key], int):
                    return 10000000
            else:
                if(len(a1_aa_mean[key]) == 0 or len(a2_aa_mean[key]) == 0):
                    return 10000000
        audio_analysis_res = audio_analysis.audio_analysis_results(a1_aa_mean, a2_aa_mean, distance)

        bars_score = audio_analysis_res['bars']
        beats_score = audio_analysis_res['beats']
        sections_score = audio_analysis_res['sections']
        segments_score = audio_analysis_res['segments']
        tatums_score = audio_analysis_res['tatums']


        aa_analysis_mean = 0
        for key in use_keys:
            aa_analysis_mean += audio_analysis_res[key]
        aa_analysis_mean = aa_analysis_mean / (len(use_keys))

    if use_audio_analysis and not use_audio_features and not use_genre:
        similarity_score = aa_analysis_mean
    elif use_audio_features and not use_audio_analysis and not use_genre:
        similarity_score = ed_score
    elif use_audio_features and use_genre and not use_audio_analysis:
        similarity_score = ed_score*(1-genre_score)
    elif use_audio_analysis and use_genre and not use_audio_features:
        similarity_score = aa_analysis_mean*(1-genre_score)
    elif use_audio_analysis and use_audio_features and not use_genre:
        similarity_score = 0.5*aa_analysis_mean+0.5*ed_score
    elif not use_audio_analysis and not use_audio_features and use_genre:
        similarity_score = 1-genre_score
    else:
        similarity_score = aa_analysis_mean+(1-genre_score)*ed_score


    if kwargs.get('use_cache')==False:
        return similarity_score, a1_aa_mean
    else:
        return similarity_score

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
                sum += calculate_similarity(bands[keys[i]], bands[keys[j]],ed_score)
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