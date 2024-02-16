#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


reward_IDs = []
no_reward_IDs = []

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        #print(data)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        self._set_response()
        name = data["name"]
        if data["request"]: # MESSAGE BACK THE LIST OF REWARDS AND NOT REWARDS
            print(f"Request received from { name }")
            response = {
                'name': 'Server',
                'reward': reward_IDs,
                'no_reward': no_reward_IDs
            }
            response = json.dumps(response).encode('utf-8')
            self.wfile.write(response)
        else:
            print(f"Update received from {name}")
            for id in data["rewards"]:
                if id not in reward_IDs:
                    reward_IDs.append(id)
                if id in no_reward_IDs:
                    no_reward_IDs.remove(id)
            for id in data["no_rewards"]:
                if id not in no_reward_IDs:
                    no_reward_IDs.append(id)
                if id in reward_IDs:
                    reward_IDs.remove(id)
            print(reward_IDs)
            print(no_reward_IDs)
            self.wfile.write("Update received".encode('utf-8'))

            



        #self.wfile.write("Data received by the server:\n".encode())
        #self.wfile.write(json.dumps(data).encode())

    def send_message(self,message):
        print("test lol")
        self.wfile.write(message.encode())

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server started on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run()