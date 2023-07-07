import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
import csv
import numpy as np
import fastdtw

client_id = 'e6bdbe153e794797ad80dea613c1c324'
client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

tracks = ["4UfJEKd1mJlHawZD35wJYo","6syEBcinz3tRLPwM9Kdemo","4c6gRbhSURaJL8lQISim8H","03LbwYl3uqYBVMMWhMw4SJ","6uWgCw5aA4hr8EAvnzcsIP","0tgVpDi06FyKpA1z0VMD4v"]

track1 = sp.audio_analysis('spotify:track:' + tracks[0])

# write analysis to csv
# with open('analysis.csv', 'w') as csvfile:
#     writer = csv.writer(csvfile)
#     for key, value in track1.items():
#         writer.writerow([key, value])

track2 = sp.audio_analysis('spotify:track:' + tracks[4])

def DTW(track1,track2,dist):
    n = len(track1)
    m = len(track2)
    DTW = np.zeros((n+1,m+1))

    for i in range(n+1):
        for j in range(m+1):
            DTW[i][j] = float('inf')
    DTW[0][0] = 0

    for i in range(1,n+1):
        for j in range(1,m+1):
            track1_vector = np.array(list(track1[i-1].values()))
            track2_vector = np.array(list(track2[j-1].values()))
            cost = dist(track1_vector, track2_vector)
            DTW[i][j] = cost + min(DTW[i-1][j], DTW[i][j-1], DTW[i-1][j-1])
    
    return DTW[n][m]


def euclidian_distance(x, y):
    return np.linalg.norm(x - y)


dtw_distance_bars = DTW(track1['bars'],track2['bars'],euclidian_distance)
print("DTW distance with bars: " + str(dtw_distance_bars))

# dtw_distance_beats = DTW(track1['beats'],track2['beats'],euclidian_distance)
# print("DTW distance with beats: " + str(dtw_distance_beats))

dtw_distance_sections = DTW(track1['sections'],track2['sections'],euclidian_distance)
print("DTW distance with sections: " + str(dtw_distance_sections))

# dtw_distance_tatums = DTW(track1['tatums'],track2['tatums'],euclidian_distance)
# print("DTW distance with tatums: " + str(dtw_distance_tatums))

def fast_dtw(track1, track2, dist):
    track1_matrix = []
    for i in range(len(track1)):
        track1_matrix.append(list(track1[i].values()))
    
    track2_matrix = []
    for i in range(len(track2)):
        track2_matrix.append(list(track2[i].values()))
    
    distance, path = fastdtw.fastdtw(track1_matrix, track2_matrix, dist=dist)
    return distance, path


fast_dtw_distance_tatums, path = fast_dtw(track1['tatums'],track2['tatums'],euclidian_distance)
print("Fast DTW distance with tatums: " + str(fast_dtw_distance_tatums))

fast_dtw_distance_beats, path = fast_dtw(track1['beats'],track2['beats'],euclidian_distance)
print("Fast DTW distance with beats: " + str(fast_dtw_distance_beats))

def fast_dtw_segments(track1, track2, dist):
    track1_matrix = []
    all_keys = ['start', 'duration', 'confidence', 'loudness_start', 'loudness_max_time', 'loudness_max', 'loudness_end', 'pitches', 'timbre']
    used_keys = ['confidence', 'loudness_start', 'loudness_max_time', 'loudness_max', 'loudness_end','pitches', 'timbre']
    for i in range(len(track1)):
        for key, value in track1[i].items():
            if key in used_keys:
                if isinstance(value, list):
                    track1_matrix.extend(value)
                else:
                    track1_matrix.append(value)
    
    track2_matrix = []
    for i in range(len(track2)):
        for key, value in track2[i].items():
            if key in used_keys:
                if isinstance(value, list):
                    track2_matrix.extend(value)
                else:
                    track2_matrix.append(value)

    distance, path = fastdtw.fastdtw(track1_matrix, track2_matrix, dist=dist)
    return distance, path

fast_dtw_distance_segments, path = fast_dtw_segments(track1['segments'],track2['segments'],euclidian_distance)
print("Fast DTW distance with segments: " + str(fast_dtw_distance_segments))


