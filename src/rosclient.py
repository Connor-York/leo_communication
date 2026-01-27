#!/usr/bin/env python3
from flask import Flask, request, jsonify
import requests
import rospy
from std_msgs.msg import String
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

server_url = 'http://192.168.1.100:5000/receive'
connor = "192.168.1.101"
mehdi = "192.168.1.102"
jay = "192.168.1.103"
james = "192.168.1.104"
clients = [connor, mehdi, jay, james]

executor = ThreadPoolExecutor(max_workers=4)
robot_id = None

# Global publisher
server_sub_pub = None

@app.route('/receive', methods=['POST'])
def receive_json():
    global server_sub_pub
    data = request.get_json()
    rospy.loginfo(f"Received from server: t={data.get('t_sent', 'N/A')} | raw={data.get('raw_time',0.0)} | raw_diff={time.time()-data.get('raw_time',0.0)}")
    server_sub_pub.publish(json.dumps(data))
    return jsonify({"status": "success"}), 200

def callback(msg):
    global robot_id
    data = json.loads(msg.data)
    
    if data['type'] == 'ready':
        robot_id = data['source']
        executor.submit(send_to_server, data)
    else:
        if data['source'] != robot_id:
            rospy.logerr(f"Source ID mismatch! Not sending. Expected {robot_id}, got {data['source']}")
            return
        send_to_robots(data)

def message_passer():
    global server_sub_pub
    rospy.init_node('message_passer', anonymous=True)
    server_sub_pub = rospy.Publisher('/server_sub', String, queue_size=10)
    rospy.Subscriber('/server_pub', String, callback)
    rospy.sleep(0.5)
    print("Client-side Initialised")

def send_to_server(data):
    try:
        requests.post(server_url, json=data, timeout=0.2)
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.RequestException as e:
        rospy.logerr(f"Failed to send to server: {e}")

def send_request(target_url, data):
    try:
        requests.post(target_url, json=data, timeout=0.2)
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.RequestException as e:
        rospy.logerr(f"Failed to send to {target_url}: {e}")

def send_to_robots(data):
    global robot_id
    for idx, target_ip in enumerate(clients):
        if idx != robot_id:
            target_url = f"http://{target_ip}:5000/receive"
            executor.submit(send_request, target_url, data)

if __name__ == '__main__':
    message_passer()
    flask_thread = threading.Thread(
        target=lambda: app.run(debug=False, host='0.0.0.0', port=5000, threaded=True),
        daemon=True
    )
    flask_thread.start()
    rospy.spin()