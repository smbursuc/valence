import requests

url = 'https://api.spotify.com/v1/search?q=Imminence&type=artist'
headers = {'Authorization': 'Bearer BQDPz2p6NchQl6_HoVg_3IgL3h9H5zuP_IRN1b26agdy2CjP1xg-GfoG7Yk7tz39hFUz95_xZTyITFA2u-lI-1_IxgaRD06RYPqk9iNt6Q-PxqCua5Uz'}

response = requests.get(url, headers=headers)

# Do something with the response, such as parse the JSON data
data = response.json()

print(data['artists']['items'][0]['id'])

print([data['tracks'][i]['name'] for i in range(len(data['tracks']))])

playlists = data['playlists']['items']

for playlist in playlists:
    print(playlist['name'])
    print(playlist['tracks'])

#print(playlists)