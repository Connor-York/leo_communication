import requests
import rospy
from std_msgs.msg import String
import json

# local network
# server_url = 'http://10.0.0.131:5000/receive'

# robot_5 network
server_url = 'http://192.168.1.100:5000/receive


def callback(data):
    message = data.data # already json, might need a 

    # Send POST request with JSON data
    response = requests.post(server_url, json=message)

    # Print the response from the server
    print(f"Response from server: {response.json()}")




def message_passer():
    rospy.init_node('message_passer', anonymous=True)
    rospy.Subscriber('/server_pub', String, callback)
    print("Client-side Initialised")
    rospy.spin()



if __name__ == '__main__':
    message_passer()
