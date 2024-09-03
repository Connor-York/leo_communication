from flask import Flask, request, jsonify

app = Flask(__name__)

server_url_local = '10.0.0.131'
server_url = '192.168.1.100'

#clients:
connor = "192.168.1.101"
mehdi = "192.168.1.102"
jay = "192.168.1.103"
james = "192.168.1.104"
clients = [connor,mehdi,jay,james]

# Endpoint to receive JSON data
@app.route('/receive', methods=['POST'])
def receive_json():
    data = request.get_json()  # Get the JSON data from the request
    print(f"Received JSON: {data}")

    if data.target = None:
        respond_all(data)
    else:
        response = requests.post(clients[data.target], json=data)
        print(f"Sent data to {clients[data.target]}, response status: {response.status_code}")

    # Send a response back
    response = {"message": "JSON received successfully!", "data_received": data}
    return jsonify(response)

def respond_all(data):

    for client_url in clients
        try:
            response = requests.post(client_url, json=data)
            print(f"Sent data to {client_url}, response status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send data to {client_url}: {e}")


if __name__ == '__main__':
    app.run(debug=True, host=server_url_local, port=5000)
