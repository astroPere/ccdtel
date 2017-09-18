#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function


import socket
import sys
import json
import time

HOST, PORT = "localhost", 4400

#Guide with Settle parameters (1.5,8,40) | No recalibration (false))
#~ m ='{"method": "guide", "params": [{"pixels": 1.5, "time": 5, "timeout": 40}, false], "id": 1}'

#Guide with Settle parameters (1.5,8,40) | Recalibration (true)
#~ m ='{"method": "guide", "params": [{"pixels": 1.5, "time": 5, "timeout": 40}, true], "id": 1}'

#Start capturing, or, if guiding, stop guiding but continue capturing
#~ m = '{"method":"loop", "id":1}'

#Stop capturing and also stop guiding
#~ m  = '{"method":"stop_capture", "id":1}'

#Set pause ON
#~ m ='{"method":"set_paused","params":[true,"full"],"id":1}'

#Connect (true)  all equipment
#~ m = '{"method":"set_connected", "params":[true], "id":1}'

#Disconnect (false) all equipment
#~ m = '{"method":"set_connected", "params":[false], "id":1}'

#Set pause OFF
#~ m ='{"method":"set_paused","params":[false,"full"],"id":1}'

#Find a start
#~ m ='{"method":"find_star","id":1}'

#Get exposure time
#~ m ='{"method":"get_exposure","id":1}'

#Set exposure time
#~ m = '{"method": "set_exposure", "params": [500], "id": 1}'

#Get App state
m ='{"method":"get_app_state","id":1}'

#Dither with Settle parameters
#~ m = '{"method": "dither", "params": [2, false, {"pixels": 1.5, "time": 8, "timeout": 40}], "id": 1}'


# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    # Receive data from the server and shut down
    sock.send(m+'\n')
    time.sleep(1)
    received = sock.recv(1024)
    
finally:
    sock.close()


print ("Sent:     {}".format(m))
print ("Received: {}".format(received))
