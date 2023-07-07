import requests

id = "7rqJQQxuUOCk052MK5kLsH"
url = 'https://api.spotify.com/v1/artists/' + id
headers = {'Authorization': "Bearer BQAeG20nvM0PE70lJteO9jvJpv5MFvYJG345MwPrhnMhwrUQN3sbRTsbRvw5vcGwktoQ0yPdHUBwr9yj261n2PmRpwxPtm7dwnz9fEtJpJUCaUHfsA8"}

response = requests.get(url, headers=headers)

# Do something with the response, such as parse the JSON data
data = response.json()

print(data)

print(data['artists']['items'][0]['id'])

print([data['tracks'][i]['name'] for i in range(len(data['tracks']))])

playlists = data['playlists']['items']

for playlist in playlists:
    print(playlist['name'])
    print(playlist['tracks'])

#print(playlists)