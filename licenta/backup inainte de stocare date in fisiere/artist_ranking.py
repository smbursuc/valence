# -*- coding: utf-8 -*-
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import main
import translate as ts
import langid
import json

# Replace these with your own credentials
client_id = 'e6bdbe153e794797ad80dea613c1c324'
client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def lookup(artist):
    artist_id = artist['id']
    artist_genres = set(sp.artist(artist_id)['genres'])
    if artist_genres is None:
        return "no genres found"
    ranking = []
    seen = set()
    use_cache = False
    a1_aa_mean_ = {}
    a1_genres_ = set()
    for genre in artist_genres:
        to_lang_ = artist['country'][0]
        if(to_lang_ != 'en'):
            translator = ts.Translator(from_lang='en', to_lang=to_lang_)
            genre = translator.translate(genre)
        results = sp.search(q=genre, type='playlist', limit=5)
        print(genre)
        for playlist in results['playlists']['items']:
            playlist_id = playlist['id']
            results = sp.playlist(playlist_id, fields="tracks,next")
            tracks = results['tracks']
            songs = tracks['items'][:20]
            bands = main.band_dict(songs)
            for band in bands.keys():
                #print(artist['band_name'] + " vs " + band + ": " + str(main.calculate_similarity(artist, bands[band],ed_score,10)))
                if(band != artist['band_name'] and band not in seen):
                    with open('audio_features.json', 'r') as file:
                        json_data = file.read()
                    parsed_data = json.loads(json_data)
                    ed_score = main.euclidian_distance_similarity(artist, bands[band], parsed_data)
                    sim_score = 0
                    if use_cache:
                        sim_score = main.calculate_similarity(artist, bands[band],ed_score, a1_aa_mean=a1_aa_mean_, a1_genres=a1_genres_, use_cache=True)
                    else:
                        sim_score, a1_aa_mean_, a1_genres_ = main.calculate_similarity(artist, bands[band],ed_score, use_cache=False)
                        use_cache = True
                        if a1_aa_mean_ is None and a1_genres_ is None:
                            print("Couldn't pull data for given artist from Spotify, most likely absent from their database")
                            return
                    ranking.append((band, sim_score))
                    seen.add(band)
                if len(ranking) > 200:
                    ranking.sort(key=lambda x: x[1])
                    print(ranking[:30])
                    return
    ranking.sort(key=lambda x: x[1])
    print(ranking[:20])


def setup_by_name(band_name):
    band = {}
    band[band_name] = {}
    band_d = {}
    band_d["band_name"] = band_name
    results = sp.search(q=band_name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        artist = items[0]
        band_d["id"] = artist['id']
    artist_tracks = sp.search(q='artist:' + band_name, type='track', limit=20)['tracks']['items']
    songs = []
    song_names = ""
    for track in artist_tracks[:2]:
        song = {}
        song["song_name"] = track['name']
        song["song_id"] = track['id']
        song["release_date"] = track['album']['release_date']
        songs.append(song)
    for track in artist_tracks:
        song_names+=" " + track['name']
    band_d["songs"] = songs
    band_d["country"] = langid.classify(song_names)
    #band_d["country"] = ('en',100)
    band[band_name] = band_d
    print(band)
    return band

def setup_by_id(artist_id):
    artist_info = sp.artist(artist_id)
    artist_name = artist_info['name']
    band = {}
    band[artist_name] = {}
    band_d = {}
    band_d["band_name"] = artist_name
    band_d["id"] = artist_id
    artist_tracks = sp.artist_top_tracks(artist_id)['tracks'][:20]
    songs = []
    song_names = ""
    for track in artist_tracks[:2]:
        song = {}
        song["song_name"] = track['name']
        song["song_id"] = track['id']
        song["release_date"] = track['album']['release_date']
        songs.append(song)
    for track in artist_tracks:
        song_names+=" " + track['name']
    band_d["songs"] = songs
    band_d["country"] = langid.classify(song_names)
    band[artist_name] = band_d
    print(band)
    return band


band_name = "Imminence"
band_dict = setup_by_name(band_name)

# band_id = "7l5zSPffvPDaRRYkAHsyt7"
# band_dict = setup_by_id(band_id)
# band_info = sp.artist(band_id)
# band_name = band_info['name']
# print(band_name)
lookup(band_dict[band_name])