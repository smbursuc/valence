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
import audio_analysis
import json


# Replace these with your own credentials
client_id = 'e6bdbe153e794797ad80dea613c1c324'
client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

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


def euclidian_distance_similarity(artist1, artist2, audio_features_file_data):
    artist_1_name = artist1['band_name']
    artist_2_name = artist2['band_name']

    # Get the top tracks for each artist
    artist_1_tracks = sp.search(q='artist:' + artist_1_name, type='track', limit=40)['tracks']['items']
    artist_1_top_track_ids = [track['id'] for track in artist_1_tracks]

    artist_2_tracks = sp.search(q='artist:' + artist_2_name, type='track', limit=40)['tracks']['items']
    artist_2_top_track_ids = [track['id'] for track in artist_2_tracks]


    for track_id in artist_1_top_track_ids:
        if track_id not in audio_features_file_data:
            audio_features_file_data[track_id] = sp.audio_features(track_id)
    
    for track_id in artist_2_top_track_ids:
        if track_id not in audio_features_file_data:
            audio_features_file_data[track_id] = sp.audio_features(track_id)
    
    with open('audio_features.json', 'w') as file:
        file.write(json.dumps(audio_features_file_data))

    # Get the audio features for each artist's top tracks
    artist_1_audio_features = []
    for track_id in artist_1_top_track_ids:
        artist_1_audio_features.append(audio_features_file_data[track_id])

    artist_2_audio_features = []
    for track_id in artist_2_top_track_ids:
        artist_2_audio_features.append(audio_features_file_data[track_id])

    artist_1_mean_features = mean_feature(artist_1_audio_features)
    artist_2_mean_features = mean_feature(artist_2_audio_features)

    similarity_score = euclidean_distance(artist_1_mean_features, artist_2_mean_features)
    return similarity_score

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def audio_analysis_mean(aa_res, use_keys):
    aa_mean = {}
    for key in use_keys:
        aa_mean[key] = 0
    #all_keys_general = ['num_samples', 'duration', 'sample_md5', 'offset_seconds', 'window_seconds', 'analysis_sample_rate', 'analysis_channels', 'end_of_fade_in', 'start_of_fade_out', 'loudness', 'tempo', 'tempo_confidence', 'time_signature', 'time_signature_confidence', 'key', 'key_confidence', 'mode', 'mode_confidence', 'codestring']
    used_keys_general = ['loudness', 'tempo_confidence', 'time_signature', 'time_signature_confidence', 'key', 'key_confidence', 'mode', 'mode_confidence']
    for track in aa_res:
        song_id = track['id']
        try:
            aa = sp.audio_analysis(song_id)
        except Exception as e:
            print(e)
            return {"error": "error"}
        for key in aa_mean.keys():
            if key != 'track':
                for v in aa[key]:
                    v_aux = np.array([])
                    for value in list(v.values()):
                        if isinstance(value, list):
                            v_aux = np.append(v_aux, np.array(value))
                        else:
                            v_aux = np.append(v_aux, value)
                    aa_mean[key] += v_aux
                aa_mean[key] /= len(aa[key])
            else:
                for key in used_keys_general:
                    aa_mean['track'] += aa['track'][key]
                aa_mean['track'] /= len(used_keys_general)
    return aa_mean

        

def ed_weight_function(A, B, k):
    return A+k/(abs(B)+k)


def calculate_similarity(artist1, artist2, ed_score, **kwargs):
    limit = 5
    use_keys = ['beats','bars', 'sections', 'track']
    if not kwargs.get('use_cache'):
        artist1_id = artist1['id']
        artist1_genres = set(sp.artist(artist1_id)['genres'])
        copy_artist1_genres = artist1_genres.copy()

        #print(artist1_genres, artist2_genres)
        for genre in copy_artist1_genres:
            genre_words = genre.split()
            if len(genre_words) > 1:
                artist1_genres.remove(genre)
                for word in genre_words:
                    artist1_genres.add(word)
        a1_top_tracks = sp.artist_top_tracks(artist1_id)['tracks'][:limit]
        a1_aa_mean = audio_analysis_mean(a1_top_tracks, use_keys)
    else:
        artist1_genres = kwargs.get('a1_genres')
        a1_aa_mean = kwargs.get('a1_aa_mean')
        
    
    artist2_id = artist2['id']

    artist2_genres = set(sp.artist(artist2_id)['genres'])

    copy_artist2_genres = artist2_genres.copy()

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

    a2_top_tracks = sp.artist_top_tracks(artist2_id)['tracks'][:limit]
    a2_aa_mean = audio_analysis_mean(a2_top_tracks, use_keys)

    for key in use_keys:
        if key != 'track':
            if 'error' in a1_aa_mean or 'error' in a2_aa_mean:
                return 100000, None, None
            if isinstance(a1_aa_mean[key], int) or isinstance(a2_aa_mean[key], int):
                return 100000, None, None
        else:
            if(a1_aa_mean[key] == 0 or a2_aa_mean[key] == 0):
                return 100000, None, None
    audio_analysis_res = audio_analysis.audio_analysis_results(a1_aa_mean, a2_aa_mean)

    bars_score = audio_analysis_res['bars']
    beats_score = audio_analysis_res['beats']
    sections_score = audio_analysis_res['sections']
    segments_score = audio_analysis_res['segments']
    tatums_score = audio_analysis_res['tatums']
    general_track_score = audio_analysis_res['general_track_analysis_score']


    vals = [genre_score, bars_score, beats_score, sections_score, segments_score, tatums_score, general_track_score , ed_score]
    # vals = [0 if val==k_distance else val/k_distance for val in vals]
    weights = [1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0]
    k = 1.5
    # a = 3

    # norm_factor = max(vals[1:6])
    # f_genre_score = sigmoid(k*(np.sum(vals[:6])/norm_factor-a))
    # w_ed = copy.copy(weights[7])
    # w_ed = f_genre_score * w_ed
    # weights[7] = w_ed

    # weights[7] = ed_weight_function(general_track_score, (bars_score+beats_score+sections_score+segments_score+tatums_score)/(len(use_keys)-1), k)

    # print(vals)
    # print(weights)

    # print(artist1['band_name'] + " vs " + artist2['band_name'])
    # print(vals)
    # print(weights)

    #similarity_score = np.sum([x*y for x,y in zip(vals, weights)])
    aa_features_mean = (bars_score+beats_score+sections_score+segments_score+tatums_score)/(len(use_keys)-1)
    similarity_score = ed_score*(general_track_score+1-genre_score)*aa_features_mean
    # print(similarity_score)
    if kwargs.get('use_cache')==False:
        return similarity_score, a1_aa_mean, artist1_genres
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