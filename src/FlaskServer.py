#!/usr/bin/env python3

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

server_url_local = '10.0.0.131'
server_url = '192.168.1.100'

#clients:
connor = "http://192.168.1.101:5000/receive"
mehdi = "http://192.168.1.102:5000/receive"
jay = "http://192.168.1.103:5000/receive"
james = "http://192.168.1.104:5000/receive"
clients = [connor] #,mehdi,jay,james] # Make sure the robot IDs are set in the order of this list



# Endpoint to receive JSON data
@app.route('/receive', methods=['POST'])
def receive_json():
    data = request.get_json()  # Get the JSON data from the request
    print("Received JSON:")
    print(data)
    print("================")
    # print("Data type:")
    # print(type(data))
    respond_all(data)
    # if data["targets"] == None:
    #     respond_all(data)
    # else:
    #     target = data["targets"]
    #     response = requests.post(clients[target], json=data)
    #     print(f"Sent data to {clients[target]}, response status: {response.status_code}")

    return jsonify({'status': 'success'}), 200

def respond_all(data):

    for count, client_url in enumerate(clients):
        if count != int(data["source"]): # dont send message back to yourself
            try:
                response = requests.post(client_url, json=data)
                print(f"Sent data to {client_url}, response status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to send data to {client_url}: {e}")


if __name__ == '__main__':
    app.run(debug=True, host=server_url_local, port=5000)
