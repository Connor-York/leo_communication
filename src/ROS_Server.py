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

app = Flask(__name__)
server_url_local = '10.0.0.131'
server_url = '192.168.1.100'

#clients:
connor = "http://10.0.0.1:5000/receive"
mehdi = "http://192.168.1.102:5000/receive"
jay = "http://192.168.1.103:5000/receive"
james = "http://192.168.1.104:5000/receive"
clients = [connor]

# Create named pipes for communication
LOG_PIPE = "/tmp/server_log_pipe"
INPUT_PIPE = "/tmp/server_input_pipe"

def setup_pipes():
    """Create named pipes for inter-process communication"""
    for pipe in [LOG_PIPE, INPUT_PIPE]:
        if os.path.exists(pipe):
            os.remove(pipe)
        os.mkfifo(pipe)

def log_window():
    """Open a separate terminal for logging"""
    cmd = f"gnome-terminal -- bash -c 'echo \"=== Server Log Window ===\"; tail -f {LOG_PIPE}'"
    subprocess.Popen(cmd, shell=True)

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

def log_message(message):
    """Send message to log window"""
    try:
        with open(LOG_PIPE, 'w') as f:
            f.write(str(message) + '\n')
    except:
        pass  # Ignore if log window is closed

# Endpoint to receive JSON data
@app.route('/receive', methods=['POST'])
def receive_json():
    data = request.get_json()
    log_message("Received JSON:")
    log_message(data)
    log_message("================")
    respond_all(data)
    return jsonify({'status': 'success'}), 200

def respond_all(data):
    for count, client_url in enumerate(clients):
        if count != int(data["source"]):
            try:
                response = requests.post(client_url, json=data)
                log_message(f"Sent data to {client_url}, response status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                log_message(f"Failed to send data to {client_url}: {e}")

def broadcast_message(message_data):
    """Send a message to all clients"""
    for client_url in clients:
        try:
            response = requests.post(client_url, json=message_data)
            log_message(f"Broadcast to {client_url}, response status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            log_message(f"Failed to broadcast to {client_url}: {e}")

def clicked_point_callback(msg):
    """Callback for /clicked_point - sends coordinates to all agents"""
    x = msg.point.x
    y = msg.point.y
    
    log_message(f"Received clicked point: ({x:.4f}, {y:.4f})")
    
    # Create message in the same format as your other messages
    message_data = {
        'source': 1,
        'type': "signal",
        'source_found': ("False", None),
        'position': (x, y),
        'g_best': (-70, (x, y))  # Using clicked point as g_best
    }
    
    broadcast_message(message_data)
    log_message(f"Broadcasted clicked point to all agents")

def flask_app():
    """Run Flask in a thread"""
    app.run(debug=False, host=server_url_local, port=5000, use_reloader=False, threaded=True)

def input_reader_loop():
    """Read commands from input window"""
    while True:
        try:
            with open(INPUT_PIPE, 'r') as f:
                user_input = f.readline().strip()
                
                if user_input:
                    if user_input == "gbest":
                        message_data = { 
                            'source': 1,
                            'type': "signal",
                            'source_found': ("False", None),
                            'position': (100, -100), 
                            'g_best': (-50, (5.4135, -0.3019))
                        }
                    elif user_input == "pos":
                        message_data = { 
                            'source': 1,
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
    log_window()
    input_window()
    
    # Give windows time to open
    import time
    time.sleep(1)
    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # Only show errors, not INFO requests

    log_message("Server starting...")
    log_message(f"Listening on {server_url_local}:5000")
    log_message("ROS node initialized, listening to /clicked_point")
    
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