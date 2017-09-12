#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function


import socket
import sys
import json
import time

HOST, PORT = "localhost", 4400

#~ m ='{"method": "guide", "params": [{"pixels": 1.5, "time": 8, "timeout": 40}, false], "id": 1}'
m ='{"method":"set_paused","params":[true,"full"],"id":1}'
#~ m ='{"method":"find_star","id":1}'
#~ m ='{"method":"get_app_state","id":1}'
#~ m = '{"method": "dither", "params": [2, false, {"pixels": 1.5, "time": 8, "timeout": 40}], "id": 1}'


# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    # Receive data from the server and shut down
    sock.send(m+'\n')
    time.sleep(1)
    received = sock.recv(512)
    
finally:
    sock.close()


print ("Sent:     {}".format(m))
print ("Received: {}".format(received))
