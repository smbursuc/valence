from django.urls import path, re_path
from .views import hello
from .views import artist_lookup
from .consumers import WSConsumer
from .views import index
from .views import artist_search
from .views import artist_search_id
from .views import artist_info_lastfm

urlpatterns = [
    path('hello/', hello, name='hello'),
    path('similar_artists/', artist_lookup, name='sa'),
    re_path(r'^ws/some_url/$', WSConsumer.as_asgi()),
    re_path(r'^search_artist/$', artist_search, name='search_artist'),
    re_path(r'^search_artist_id/$', artist_search_id, name='search_artist_id'),
    re_path(r'^artist_info_lastfm/$', artist_info_lastfm, name='artist_info_lastfm'),
    path('', index, name='index')
]
