#!/usr/bin/env python3
import rospy
from std_msgs.msg import Int16MultiArray
from std_msgs.msg import String
import json

temp_array = [1,2,3,4]

def talker():
    pub = rospy.Publisher('/server_pub', String, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    #rate = rospy.Rate(10) # 10hz
    server_message = {
            'name':"test_case",
            'request':True,
            'rewards':[0,1,2,3],
            'no_rewards':[4,5,6,7]
    }
    pub.publish(json.dumps(server_message))

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass