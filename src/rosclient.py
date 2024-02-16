#!/usr/bin/env python3
import urllib.request
import json
import rospy
from std_msgs.msg import String

url = 'http://10.0.0.131:8000'  # Change the URL if the server runs on a different machine or port

data_request = {
    'name': 'Client',
    'request': True,                                                                                                                              
}



def callback(data):
    # data_update = {
    #     'name': 'Leo_Connor',
    #     'request': False,
    #     'rewards': data.data,
    #     'no_rewards': [5,6,7,8]
    # }
    # data_update = json.dumps(data_update).encode('utf-8')
    # req = urllib.request.Request(url, data=data_update, headers={'Content-Type': 'application/json'})
    # with urllib.request.urlopen(req) as response:
    #     print(response.read().decode('utf-8')) 
    message = json.loads(data.data)
    if message["request"]: 
        #REQUEST, WANTS DATA RETURNED
        print("Request received, forwarding to server")
        data_request = data.data.encode('utf-8')
        req = urllib.request.Request(url, data=data_request, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
             print(response.read().decode('utf-8')) 
             #RETURN RESPONSE HERE
    else:
        #Not a request, doesn't want data returned.
        print("Update received, forwarding to server")
        data_update = data.data.encode('utf-8')
        update = urllib.request.Request(url, data=data_update, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(update) as response:
             print(response.read().decode('utf-8')) 
             #DONE

    


    

def message_passer():
    rospy.init_node('message_passer', anonymous=True)
    rospy.Subscriber('/server_pub', String, callback)
    rospy.spin()

# user_input = input("Update or Req: [u or r] ")

# if user_input == 'u':
#     data_update = json.dumps(data_update).encode('utf-8')
#     req = urllib.request.Request(url, data=data_update, headers={'Content-Type': 'application/json'})
#     with urllib.request.urlopen(req) as response:
#         print(response.read().decode('utf-8')) 
# else: 
#     data_request = json.dumps(data_request).encode('utf-8')
#     req = urllib.request.Request(url, data=data_request, headers={'Content-Type': 'application/json'})
#     with urllib.request.urlopen(req) as response:
#         print(response.read().decode('utf-8'))


if __name__ == '__main__':
    message_passer()
