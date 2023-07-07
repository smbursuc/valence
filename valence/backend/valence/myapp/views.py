from django.http import HttpResponse
from django.http import JsonResponse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.shortcuts import render
import requests

def hello(request):
    return HttpResponse("Hello, world!")


def artist_lookup(request):
    query_dict = request.GET.dict()
    return JsonResponse({"artist": "The Beatles", "song": "Let It Be"})

def index(request):
    return render(request, 'index.html', context={'text': 'Hello World!'})


def artist_search(request):
    client_id = 'e6bdbe153e794797ad80dea613c1c324'
    client_secret = "cc2cff7dd55d4b1b9903aa41cefd9560"
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    query_dict = request.GET.dict()
    artist_name = query_dict['query']
    results = sp.search(q='artist:' + artist_name, type='artist')
    items = results['artists']['items']
    return JsonResponse({"results": items[:5]})

def artist_search_id(request):
    client_id = 'e6bdbe153e794797ad80dea613c1c324'
    client_secret = "cc2cff7dd55d4b1b9903aa41cefd9560"
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    query_dict = request.GET.dict()
    artist_id = query_dict['query']
    results = sp.artist(artist_id)
    return JsonResponse({"results": results})

def artist_info_lastfm(request):
    query_dict = request.GET.dict()
    artist_name = query_dict['query']
    response = requests.get('http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist=' + artist_name + '&api_key=9cb344e010b38bd815b32d44ab77f8b2&format=json')
    return JsonResponse({"results": response.json()})


