#!/usr/bin/env python3
from flask import Flask, request, jsonify
import requests
import threading
import sys
import subprocess
import os
import logging
import rospy
from geometry_msgs.msg import PointStamped
import time

app = Flask(__name__)
#server_url = '10.0.0.131'
server_url = '192.168.1.100'

#clients:
connor = "http://192.168.1.101:5000/receive"
#connor = "http://10.0.0.1:5000/receive"
mehdi = "http://192.168.1.102:5000/receive"
jay = "http://192.168.1.103:5000/receive"
james = "http://192.168.1.104:5000/receive"
clients = [connor, mehdi, jay, james] #,james]

# Create named pipes for communication
# LOG_PIPE = "/tmp/server_log_pipe"
INPUT_PIPE = "/tmp/server_input_pipe"

def setup_pipes():
    """Create named pipes for inter-process communication"""
    for pipe in [INPUT_PIPE]:
        if os.path.exists(pipe):
            os.remove(pipe)
        os.mkfifo(pipe)

def input_window():
    """Open a separate terminal for user input"""
    script = f"""
#!/bin/bash
echo "=== Server Terminal Command Interface ==="
echo "Type your message and press Enter to broadcast to all clients"
echo "COMMANDS: "
echo "'start' - Start operation"
echo "'signal_on' - Robots start detecting signals"
echo ""
while true; do
    read -p "Server> " input
    echo "$input" > {INPUT_PIPE}
done
"""
    # Write script to temp file
    script_file = "/tmp/server_input_script.sh"
    with open(script_file, 'w') as f:
        f.write(script)
    os.chmod(script_file, 0o755)
    
    cmd = f"gnome-terminal -- bash {script_file}"
    subprocess.Popen(cmd, shell=True)

# Endpoint to receive JSON data
@app.route('/receive', methods=['POST'])
def receive_json():
    data = request.get_json()
    if data['type'] == 'ready':
        rospy.loginfo(f"Client {data['source']} is ready.")
    else:
        respond_all(data)
        #rospy.loginfo(f"Received message t = {data['t_sent']} | rawdiff = {time.time()-data.get('raw_time',0.0)}")
        #broadcast_message(data)
    return jsonify({'status': 'success'}), 200

def respond_all(message_data):
    for count, client_url in enumerate(clients):
        if count != int(message_data["source"]):
            threading.Thread(target=send_message_thread, args=(client_url, message_data), daemon=True).start()

def broadcast_message(message_data):
    """Send a message to all clients"""
    for client_url in clients:
        rospy.loginfo(f"Broadcasting to {client_url}: {message_data}")
        threading.Thread(target=send_message_thread, args=(client_url, message_data), daemon=True).start()

def send_message_thread(client_url, message_data):
    """
    Spins up a thread to send the http post
    Short timeout, warns on failures, ignores timeouts.
    Temporary solution for http post slowdown. 
    Should be replaced with sockets or some other communication method.
    """
    try:
        requests.post(client_url, json=message_data, timeout=0.2)
        #rospy.loginfo(f"Broadcast to {client_url}, response status: {response.status_code}")
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.RequestException as e:
        rospy.logwarn(f"Failed to broadcast to {client_url}: {e}")

def clicked_point_callback(msg):
    """Callback for /clicked_point - sends coordinates to all agents"""
    x = msg.point.x
    y = msg.point.y
    
    rospy.loginfo(f"Received clicked point: ({x:.4f}, {y:.4f})")
    
    # Create message in the same format as your other messages
    message_data = {
        'source': 1,
        'type': "signal",
        'source_found': ("False", None),
        'position': (x, y),
        'g_best': (-70, (x, y))  # Using clicked point as g_best
    }
    
    broadcast_message(message_data)
    rospy.loginfo(f"Broadcasted clicked point to all agents")

def flask_app():
    """Run Flask in a thread"""
    app.run(debug=False, host=server_url, port=5000, use_reloader=False, threaded=True)

def input_reader_loop():
    """Read commands from input window"""
    while True:
        try:
            with open(INPUT_PIPE, 'r') as f:
                user_input = f.readline().strip()
                
                if user_input:
                    if user_input == "gbest":
                        message_data = { 
                            'source': 2,
                            'type': "signal",
                            'source_found': ("False", None),
                            'position': (100, -100), 
                            'g_best': (-70, (1.4135, -0.3019))
                        }
                    elif user_input == "pos":
                        message_data = { 
                            'source': 2,
                            'type':"signal",
                            'source_found':("False", None),
                            'position':(1.3676, -4.3068), 
                            'g_best':(-70, (2.3284, -4.43496))
                        }
                    else:
                        message_data = {
                            "source": "server",
                            "message": user_input
                        }
                    broadcast_message(message_data)
        except:
            break

if __name__ == '__main__':
    # Initialize ROS node FIRST in main thread
    rospy.init_node('server_clicked_point_listener', anonymous=True)
    
    # Setup communication pipes
    setup_pipes()
    
    # Open separate windows
    input_window()
    
    # Give windows time to open
    import time
    time.sleep(1)
    

    rospy.loginfo("Server starting...")
    rospy.loginfo(f"Listening on {server_url}:5000")
    rospy.loginfo("ROS node initialized, listening to /clicked_point")
    
    # Subscribe to clicked_point in main thread
    rospy.Subscriber('/clicked_point', PointStamped, clicked_point_callback)
    
    # Start Flask in separate thread
    flask_thread = threading.Thread(target=flask_app, daemon=True)
    flask_thread.start()
    
    # Start input reader thread
    input_thread = threading.Thread(target=input_reader_loop, daemon=True)
    input_thread.start()
    
    # Keep main thread alive with rospy.spin()
    rospy.spin()
