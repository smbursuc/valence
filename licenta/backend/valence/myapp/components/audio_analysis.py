import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pprint
import csv
import numpy as np
import fastdtw
import copy

client_id = 'e6bdbe153e794797ad80dea613c1c324'
client_secret = 'cc2cff7dd55d4b1b9903aa41cefd9560'

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def DTW(track1,track2):
    n = len(track1)
    m = len(track2)
    DTW = np.zeros((n+1,m+1))

    for i in range(n+1):
        for j in range(m+1):
            DTW[i][j] = float('inf')
    DTW[0][0] = 0

    for i in range(1,n+1):
        for j in range(1,m+1):
            cost = abs(track1[i-1] - track2[j-1])
            DTW[i][j] = cost + min(DTW[i-1][j], DTW[i][j-1], DTW[i-1][j-1])
    
    return DTW[n][m]


def euclidian_distance(x, y):
    return np.linalg.norm(x - y)


def fast_dtw(track1, track2, dist):
    track1_matrix = []
    for i in range(len(track1)):
        track1_matrix.append(list(track1[i].values()))
    
    track2_matrix = []
    for i in range(len(track2)):
        track2_matrix.append(list(track2[i].values()))
    
    distance, path = fastdtw.fastdtw(track1_matrix, track2_matrix, dist=dist)
    return distance, path


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

def cosine_similarity(x, y):
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))

def manhattan_distance(x, y):
    return np.sum(np.abs(x - y))

def minkowski_distance(x, y, p_value):
    return np.sum(np.abs(x - y) ** p_value) ** (1 / p_value)

def hamming_distance(x, y):
    return np.sum(x != y) / len(x)



def audio_analysis_results(a1_mean, a2_mean, distance):
    aa_elements = ['bars', 'beats', 'sections', 'tatums', 'segments']
    aa_elements_values = [0,0,0,0,0]

    for i in range(len(aa_elements)):
        if aa_elements[i] in a1_mean and aa_elements[i] in a2_mean:
            if distance == 'euclidian':
                aa_elements_values[i] = euclidian_distance(a1_mean[aa_elements[i]], a2_mean[aa_elements[i]])
            if distance == 'cosine':
                aa_elements_values[i] = cosine_similarity(a1_mean[aa_elements[i]], a2_mean[aa_elements[i]])
            if distance == 'manhattan':
                aa_elements_values[i] = manhattan_distance(a1_mean[aa_elements[i]], a2_mean[aa_elements[i]])
            if distance == 'minkowski':
                aa_elements_values[i] = minkowski_distance(a1_mean[aa_elements[i]], a2_mean[aa_elements[i]], 3)
            if distance == 'hamming':
                aa_elements_values[i] = hamming_distance(a1_mean[aa_elements[i]], a2_mean[aa_elements[i]])
            if distance == 'dtw':
                # get rid of all 0s in the vector
                v1_no_zeros = [x for x in a1_mean[aa_elements[i]] if x != 0]
                v2_no_zeros = [x for x in a2_mean[aa_elements[i]] if x != 0]
                aa_elements_values[i], path = fastdtw.fastdtw(v1_no_zeros, v2_no_zeros, dist=euclidian_distance)
                #aa_elements_values[i] = DTW(v1_no_zeros, v2_no_zeros)
        


    results = {"bars": aa_elements_values[0], "beats": aa_elements_values[1], "sections": aa_elements_values[2], "tatums": aa_elements_values[3], "segments": aa_elements_values[4]}
    
    print("artist done")

    return results


def main():
    tracks = ["4UfJEKd1mJlHawZD35wJYo","6syEBcinz3tRLPwM9Kdemo","4c6gRbhSURaJL8lQISim8H","03LbwYl3uqYBVMMWhMw4SJ","6uWgCw5aA4hr8EAvnzcsIP","0tgVpDi06FyKpA1z0VMD4v"]

    track1 = sp.audio_analysis('spotify:track:' + tracks[0])

    # write analysis to csv
    # with open('analysis.csv', 'w') as csvfile:
    #     writer = csv.writer(csvfile)
    #     for key, value in track1.items():
    #         writer.writerow([key, value])

    for i in range(1,len(tracks)):
        track2 = sp.audio_analysis('spotify:track:' + tracks[i])

        dtw_distance_bars = DTW(track1['bars'],track2['bars'],euclidian_distance)
        print("DTW distance with bars: " + str(dtw_distance_bars))

        # dtw_distance_beats = DTW(track1['beats'],track2['beats'],euclidian_distance)
        # print("DTW distance with beats: " + str(dtw_distance_beats))

        dtw_distance_sections = DTW(track1['sections'],track2['sections'],euclidian_distance)
        print("DTW distance with sections: " + str(dtw_distance_sections))

        # dtw_distance_tatums = DTW(track1['tatums'],track2['tatums'],euclidian_distance)
        # print("DTW distance with tatums: " + str(dtw_distance_tatums))

        fast_dtw_distance_tatums, path = fast_dtw(track1['tatums'],track2['tatums'],euclidian_distance)
        print("Fast DTW distance with tatums: " + str(fast_dtw_distance_tatums))

        fast_dtw_distance_beats, path = fast_dtw(track1['beats'],track2['beats'],euclidian_distance)
        print("Fast DTW distance with beats: " + str(fast_dtw_distance_beats))

        # fast_dtw_distance_segments, path = fast_dtw_segments(track1['segments'],track2['segments'],euclidian_distance)
        # print("Fast DTW distance with segments: " + str(fast_dtw_distance_segments))

        general_track_analysis_score = track_general_analysis_score(track1['track'],track2['track'])
        print("General track analysis score using euclidian distance: " + str(general_track_analysis_score))


        # used_keys = ['loudness', 'tempo', 'tempo_confidence', 'time_signature', 'time_signature_confidence', 'key', 'key_confidence', 'mode', 'mode_confidence']
        # track1_dict_copy = copy.copy(track1['track'])
        # track2_dict_copy = copy.copy(track2['track'])
        # for key, value in track1['track'].items():
        #     if key not in used_keys:
        #         track1_dict_copy.pop(key, None)
        #         track2_dict_copy.pop(key, None)
        
        # print(track1_dict_copy)
        # general_tract_analysis_score_dtw = DTW([track1_dict_copy],[track2_dict_copy],euclidian_distance)
        # print("General track analysis score using DTW: " + str(general_tract_analysis_score_dtw))

        print()



if __name__ == "__main__":
    main()


