import requests
import json

url = 'https://api.github.com/users'

login = 'mojombo'

response = requests.get(f'{url}/{login}/repos')

with open('reposlist.json', 'w') as out_file:
    json.dump(response.json(), out_file)

for i in response.json():
    print({i['name']})