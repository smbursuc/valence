# -*- coding: utf-8 -*-
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from . import main
import translate as ts
import langid
import json
import os
from asyncio import sleep
from channels.exceptions import StopConsumer

# Replace these with your own credentials
client_id = 'e6bdbe153e794797ad80dea613c1c324'
client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


async def lookup(artist,self, payload):
    artist_id = artist['id']
    artist_genres = set(sp.artist(artist_id)['genres'])

    if artist_genres is None:
        return "no genres found"
    
    params = {}
    
    artist_genres_split = [word for item in artist_genres for word in item.split()]
    artist_genres_split = set(artist_genres_split)
    if payload['use_genre'] == True:
        params['artist_genres_split'] = artist_genres_split

    ranking = []
    seen = set()
    use_cache = False
    a1_aa_mean = {}
    track_limit = payload['tracks']
    artist1_top_tracks = sp.artist_top_tracks(artist_id)['tracks'][:track_limit]

    audio_features = {"acousticness":payload['acousticness'], "danceability":payload['danceability'], "energy":payload['energy'], "instrumentalness":payload['instrumentalness'], "liveness":payload['liveness'], "tempo":payload['tempo'], "valence":payload['valence'], "key":payload['key']}
    audio_analysis = {"bars":payload['bars'], "beats":payload['beats'], "sections":payload['sections'], "segments":payload['segments'], "tatums":payload['tatums']}
    params['audio_features'] = audio_features
    params['audio_analysis'] = audio_analysis
    

    params['artist1_top_tracks'] = artist1_top_tracks

    with open("E:\\licenta\\backend\\valence\\myapp\\components\\audio_features.json", 'r') as file:
        json_data = file.read()
    parsed_data = json.loads(json_data)

    # for genre in artist_genres_split:
    #     if genre not in artist_genres:
    #         artist_genres.add(genre)
    # print(artist_genres)
    
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
                    artist2_top_tracks = sp.artist_top_tracks(bands[band]['id'])['tracks'][:track_limit]
                    params["artist2_top_tracks"] = artist2_top_tracks
                    artist2_id = bands[band]['id']
                    use_audio_features = any(value for value in audio_features.values())
                    if use_audio_features:
                        ed_score = main.euclidian_distance_similarity(artist1_top_tracks, artist2_top_tracks, parsed_data, params['audio_features'])
                    else:
                        ed_score = None
                    sim_score = 0
                    if use_cache:
                        sim_score = main.calculate_similarity(artist2_id,ed_score, params, use_cache=True)
                    else:
                        sim_score, a1_aa_mean = main.calculate_similarity(artist2_id,ed_score, params, use_cache=False)
                        params['a1_aa_mean'] = a1_aa_mean
                        use_cache = True
                    ranking.append((band, sim_score))
                    seen.add(band)
                    artist_info = sp.artist(bands[band]['id'])
                    image_url = artist_info['images'][0]['url']
                    spotify_link = artist_info['external_urls']['spotify']
                    top_tracks = sp.artist_top_tracks(bands[band]['id'])['tracks'][:5]
                    tracks = []
                    for track in top_tracks:
                        track_info = {}
                        track_info['name'] = track['name']
                        track_info['image_url'] = track['album']['images'][0]['url']
                        track_info['preview_url'] = track['preview_url']
                        tracks.append(track_info)
                    await self.send(json.dumps({
                        'name': band,
                        'score': sim_score,
                        'id': bands[band]['id'],
                        'image_url': image_url,
                        'spotify_link': spotify_link,
                        'top_tracks': tracks
                    }))
                    await sleep(1)
                if len(ranking) > 100:
                    ranking.sort(key=lambda x: x[1])
                    print(ranking[:50])
                    await self.send(json.dumps({
                        "status": "done"
                    }))
                    return
    ranking.sort(key=lambda x: x[1])
    print(ranking[:50])



def setup_by_name(band_name):
    band = {}
    band[band_name] = {}
    band_d = {}
    band_d["band_name"] = band_name
    results = None
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


# band_name = "Imminence"
# band_dict = setup_by_name(band_name)

# # band_id = "1QexdJFYGyxdBlEpDSy0d4"
# # band_dict = setup_by_id(band_id)
# # band_info = sp.artist(band_id)
# # band_name = band_info['name']
# # print(band_name)
# lookup(band_dict[band_name])

# # print(rec_songs)