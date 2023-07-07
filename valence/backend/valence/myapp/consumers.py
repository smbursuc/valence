from channels.generic.websocket import AsyncWebsocketConsumer
import json
import random
from asyncio import sleep
from asyncio import current_task
from .components import artist_ranking
import urllib.parse
from channels.exceptions import StopConsumer
import asyncio
import requests

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .components import main
import translate as ts
import langid
import json
import os
from asyncio import sleep
from channels.exceptions import StopConsumer
import random


class WSConsumer(AsyncWebsocketConsumer):
    artist_name = ''
    artist_id = ''
    disconnectFlag = False

    async def connect(self):
        await self.accept()

        query_params = self.scope['query_string']
        query_dict = urllib.parse.parse_qs(query_params.decode('utf-8'))
        if 'artist_name' in query_dict:
            self.artist_name = query_dict['artist_name'][0][:-1]
        elif 'id' in query_dict:
            self.artist_id = query_dict['id'][0][:-1]

    async def receive(self, text_data):
        payload = json.loads(text_data)
        print(payload)
        if self.artist_name != '':
            setup = artist_ranking.setup_by_name(self.artist_name)
            asyncio.create_task(self.lookup(setup[self.artist_name], payload))
        else:
            print(self.artist_id)
            setup = artist_ranking.setup_by_id(self.artist_id)
            band_name = list(setup.keys())[0]
            asyncio.create_task(self.lookup(setup[band_name], payload))

    async def disconnect(self, code):
        self.disconnectFlag = True
        self.close()

    async def lookup(self, artist, payload):
        # Replace these with your own credentials
        client_id = 'e6bdbe153e794797ad80dea613c1c324'
        client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

        # Authenticate with Spotify API
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager)

        artist_id = artist['id']
        artist_genres = list(sp.artist(artist_id)['genres'])

        if len(artist_genres) == 0:
            api_key = '9cb344e010b38bd815b32d44ab77f8b2'
            url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={self.artist_name}&api_key={api_key}&format=json"
            response = requests.get(url)
            data = response.json()
            genres = [tag['name'] for tag in data['artist']['tags']['tag']]
            artist_genres = genres

        params = {}

        artist_genres_split = [
            word for item in artist_genres for word in item.split()]
        artist_genres_split = set(artist_genres_split)
        if payload['use_genre'] == True:
            params['artist_genres_split'] = artist_genres_split

        ranking = []
        seen = set()
        use_cache = False
        a1_aa_mean = {}
        track_limit = int(payload['tracks'])
        artist1_top_tracks = sp.artist_top_tracks(
            artist_id)['tracks'][:track_limit]

        audio_features = {"acousticness": payload['acousticness'], "danceability": payload['danceability'], "energy": payload['energy'],
                          "instrumentalness": payload['instrumentalness'], "liveness": payload['liveness'], "tempo": payload['tempo'], "valence": payload['valence'], "key": payload['key']}
        audio_analysis = {"bars": payload['bars'], "beats": payload['beats'],
                          "sections": payload['sections'], "segments": payload['segments'], "tatums": payload['tatums']}
        params['audio_features'] = audio_features
        params['audio_analysis'] = audio_analysis
        distance = payload['distance']

        params['artist1_top_tracks'] = artist1_top_tracks

        with open("E:\\licenta\\backend\\valence\\myapp\\components\\audio_features.json", 'r') as file:
            json_data = file.read()
        parsed_data = json.loads(json_data)

        # for genre in artist_genres_split:
        #     if genre not in artist_genres:
        #         artist_genres.add(genre)
        # print(artist_genres)

        if len(artist_genres) == 1:
            artist_genres = list(artist_genres_split)


        #artist_genres = list(artist_genres_split)
        random.shuffle(artist_genres)
        for genre in artist_genres:
            to_lang_ = artist['country'][0]
            if (to_lang_ != 'en'):
                translator = ts.Translator(from_lang='en', to_lang=to_lang_)
                genre = translator.translate(genre)
            results = sp.search(q=genre, type='playlist', limit=3)
            print(genre)
            for playlist in results['playlists']['items']:
                playlist_id = playlist['id']
                results = sp.playlist(playlist_id, fields="tracks,next")
                tracks = results['tracks']
                songs = tracks['items'][:20]
                bands = main.band_dict(songs)
                for band in bands.keys():
                    # print(artist['band_name'] + " vs " + band + ": " + str(main.calculate_similarity(artist, bands[band],ed_score,10)))
                    if (self.disconnectFlag):
                        ranking.sort(key=lambda x: x[1])
                        print(ranking)
                        return
                    if (band != artist['band_name'] and band not in seen):
                        artist2_top_tracks = sp.artist_top_tracks(
                            bands[band]['id'])['tracks'][:track_limit]
                        params["artist2_top_tracks"] = artist2_top_tracks
                        use_audio_features = any(
                            value for value in audio_features.values())
                        if use_audio_features:
                            ed_score = main.euclidian_distance_similarity(
                                artist1_top_tracks, artist2_top_tracks, parsed_data, params['audio_features'], distance)
                        else:
                            ed_score = None
                        sim_score = 0
                        if use_cache:
                            sim_score = main.calculate_similarity(
                                bands[band], ed_score, params, distance, use_cache=True)
                        else:
                            sim_score, a1_aa_mean = main.calculate_similarity(
                                bands[band], ed_score, params, distance, use_cache=False)
                            params['a1_aa_mean'] = a1_aa_mean
                            use_cache = True
                        ranking.append((band, sim_score))
                        seen.add(band)
                        artist_info = sp.artist(bands[band]['id'])
                        if len(artist_info['images']) != 0:
                            image_url = artist_info['images'][0]['url']
                        spotify_link = artist_info['external_urls']['spotify']
                        top_tracks = sp.artist_top_tracks(
                            bands[band]['id'])['tracks'][:5]
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
                            'top_tracks': tracks,
                        }))
                        await sleep(1)
                        if len(ranking) > 100:
                            ranking.sort(key=lambda x: x[1])
                            print(ranking[:50])
                            print(len(ranking))
                            await self.send(json.dumps({
                                "status": "done"
                            }))
                            return
        ranking.sort(key=lambda x: x[1])
        print(ranking[:50])
        await self.send(json.dumps({
            "status": "done"
        }))
