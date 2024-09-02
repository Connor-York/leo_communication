#!/usr/bin/env python3
import urllib.request
import json

url = 'http://10.0.0.131:8000'  # Change the URL if the server runs on a different machine or port

data_request = {
    'name': 'Client',
    'request': True,                                                                                                                              
}

data_update = {
    'name': 'Client',
    'request': False,
    'rewards': [1,2,3,4],
    'no_rewards': [5,6,7,8]
}

user_input = input("Update or Req: [u or r] ")

if user_input == 'u':
    data_update = json.dumps(data_update).encode('utf-8')
    req = urllib.request.Request(url, data=data_update, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8')) 
else: 
    data_request = json.dumps(data_request).encode('utf-8')
    req = urllib.request.Request(url, data=data_request, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8'))
