#!/usr/bin/env python3
from flask import Flask, request, jsonify
import requests
import rospy
from std_msgs.msg import String
import json
import threading

app = Flask(__name__)

# local network
# server_url = 'http://10.0.0.131:5000/receive'

# robot_5 network
server_url = 'http://192.168.1.100:5000/receive'

connor = "192.168.1.101"
mehdi = "192.168.1.102"
jay = "192.168.1.103"
james = "192.168.1.104"

@app.route('/receive', methods=['POST'])
def receive_json():
    print("received message from server")
    data = request.get_json()
    print(f"Received JSON: {data}")
    pub = rospy.Publisher('/server_sub', String, queue_size=10)
    pub.publish(json.dumps(data))
    print("sent message to server_sub")
    return jsonify({"status": "success"}), 200

def callback(data):
    print("received message from robot_main")
    message = json.loads(data.data) # already json, might need a 

    # Send POST request with JSON data
    response = requests.post(server_url, json=message)

    # Print the response from the server
    try:
        print(f"Response from server: {response.json()}")
    except ValueError:
        rospy.logerr(f"Failed to decode JSON: {response.text}")



def message_passer():
    rospy.init_node('message_passer', anonymous=True)
    rospy.Subscriber('/server_pub', String, callback)
    print("Client-side Initialised")



if __name__ == '__main__':
    message_passer()
    app.run(debug=True, host=connor, port=5000)


