# leo_communication
ROS Package created to provide communication between robots on a local network as part of my PhD research. 

Two approaches: server and client
Communication is p2p between clients, with the server for logging and user control during experiments. 

Clients receive messages and publish them to ROS topics for other nodes to work with, and subscribe to topics for messages to send out to the network. Messaging is threaded to minimise latency. 

## How to use:
Launch a rosclient.launch on each robot (adjust IPs accordingly) and server.launch (optionally) on your laptop. 

Messages received by the robot will be published on the **\server_sub** topic, and messages published to the **\server_pub** topic will be sent out to other clients / server depending on the message content.

Used for robot experiments, so most of the functionality revolves around specific message structures and other admin tools. Integrates directly with my leo_navigation package. 
