#!/usr/bin/env python3
from flask import Flask, request, jsonify
import requests
import rospy
from std_msgs.msg import String
import json
import threading

app = Flask(__name__)

# local network
server_url = 'http://10.0.0.131:5000/receive'
<<<<<<< HEAD

# robot_5 network
#server_url = 'http://192.168.1.100:5000/receive' #1.105 is adam?
=======
# robot_5 network
#server_url = 'http://192.168.1.105:5000/receive'
>>>>>>> 6c5986c40cbf6bdbc8d1bafb187679517a3f12b3

#connor = "192.168.1.101"
connor = "10.0.0.1"
mehdi = "192.168.1.102"
jay = "192.168.1.103"
james = "192.168.1.104"

# Global publisher
server_sub_pub = None

@app.route('/receive', methods=['POST'])
def receive_json():
    global server_sub_pub
    data = request.get_json()
    print(f"Received from server: {data}")
    server_sub_pub.publish(json.dumps(data))
    return jsonify({"status": "success"}), 200

def callback(data):
    message = json.loads(data.data)
    try:
        response = requests.post(server_url, json=message)
        print(f"Sent to server, status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        rospy.logerr(f"Failed to send to server: {e}")

def message_passer():
    global server_sub_pub
    rospy.init_node('message_passer', anonymous=True)
    server_sub_pub = rospy.Publisher('/server_sub', String, queue_size=10)
    rospy.Subscriber('/server_pub', String, callback)
    rospy.sleep(0.5)  # Give publisher time to connect
    print("Client-side Initialised")

if __name__ == '__main__':
    message_passer()
    
    # Run Flask in separate thread so ROS can spin
    flask_thread = threading.Thread(
        target=lambda: app.run(debug=False, host=connor, port=5000, threaded=True),
        daemon=True
    )
    flask_thread.start()
    
    rospy.spin()