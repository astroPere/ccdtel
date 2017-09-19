#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function


import socket
import sys
import logging
import time
import json

rc = '\033[0m' #reset color
cr = '\033[91m'#red
cg ='\033[32m' #green
cw = '\033[33m'#yellow
cb = '\033[94m'#blue
cy = '\033[36m'#cyan
cd = '\033[100m'#gray background

log = logging.getLogger(__name__)

class PhdClient(object):

    def __init__(self, **kargs):

        self.address = kargs['address']
        self.port = kargs['port']
        self.timeout = float(kargs['timeout'])
        self.phd_id = int(kargs['phd_id'])



    def equipment(self,status="On",_id=None):

        if not _id: _id = self.phd_id
        if status == "On":
            stat = True
        elif status == "Off":
            stat = False
        else:
            log.error(
            cr+'ERROR: {} is a invalid status value ("On"/"Off")'.format(status)+rc)
            return None

        log.info("PHD id_{}: turning equipment = '{}'".format(_id,status.upper()))

        msg = {"method":"set_connected", "params":[stat], "id":_id}
        msg = json.dumps(msg)
        recv = self._socket(msg)



    def pause(self,status="On", _id=None):

        if not _id: _id = self.phd_id

        if status == "On":
            stat = True
        elif status == "Off":
            stat = False
        else:
            log.error(
            cr+'ERROR: {} is a invalid status value ("On"/"Off")'.format(status)+rc)
            return None

        log.info("PHD id_{}: pausing = '{}'".format(_id,status.upper()))

        msg = {"method":"set_paused", "params":[stat], "id":_id}
        msg = json.dumps(msg)
        recv = self._socket(msg)


    def select_star(self, _id=None):

        if not _id: _id = self.phd_id

        log.info("PHD id_{}: auto-selecting star.".format(_id))

        msg = {"method":"find_star", "id":_id}
        msg = json.dumps(msg)
        recv = self._socket(msg)



    def single_capture(self, _id=None):

        if not _id: _id = self.phd_id

        log.info("PHD id_{}: single capture.".format(_id))

        msg = {"method":"capture_single_frame", "id":_id}
        msg = json.dumps(msg)
        recv = self._socket(msg)



    def stop(self, _id=None):

        if not _id: _id = self.phd_id

        log.info("PHD id_{}: stop capturing and guiding.".format(_id))

        msg = {"method":"stop_capture", "id":_id}
        msg = json.dumps(msg)
        recv = self._socket(msg)



    def app_state(self, _id=None):

        if not _id: _id = self.phd_id

        log.info("PHD id_{}: get app state.".format(_id))
        msg = {"method":"get_app_state", "id":_id}
        msg = json.dumps(msg)

        recv = self._socket(msg)
        print(cw,recv,rc)


    def loop(self, _id=None):

        if not _id: _id = self.phd_id

        log.info("PHD id_{}: exposing loop.".format(_id))

        msg = {"method":"loop", "id":_id}
        msg = json.dumps(msg)
        print(cw,msg,rc)
        recv = self._socket(msg)



    def _socket(self, msg):

        logmsg = 'Sending socket message: {} '.format(msg)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        recv = None
        try:
            sock.connect((self.address, int(self.port)))
            for attempt in range(5):
                log.debug(logmsg+'Attempt: {}'.format(attempt+1))
                sock.send(msg+'\n')
                time.sleep(1+attempt)
                received = sock.recv(1024)
                for recv in received.strip().split('\n'):
                    recv = json.loads(recv)
                    if 'jsonrpc' in recv:
                        sock.close()
                        return recv

        except ValueError:
            pass
        except socket.error:
            log.error(cr+"ERROR: Can't connect to PHD server!. Is it running?"+rc)
        else:
            sock.close()
        finally:
            if recv and "error" not in recv:
                return recv
            elif not recv:
                return False
            else:
                log.error(cr+"ERROR: {}.".format(recv['error']['message'])+rc)
                return False





###############################################################################

#Guide with Settle parameters (1.5,8,40) | No recalibration (false))
#~ m ='{"method": "guide", "params": [{"pixels": 1.5, "time": 5, "timeout": 40}, false], "id": 1}'

#Guide with Settle parameters (1.5,8,40) | Recalibration (true)
#~ m ='{"method": "guide", "params": [{"pixels": 1.5, "time": 5, "timeout": 40}, true], "id": 1}'

#Start capturing, or, if guiding, stop guiding but continue capturing
#~ m = '{"method":"loop", "id":1}'

#Auto-select a star
#~ m = '{"method":"find_star", "id":1}'

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

#Get exposure time
#~ m ='{"method":"get_exposure","id":1}'

#Set exposure time
#~ m = '{"method": "set_exposure", "params": [500], "id": 1}'

#Get App state
#~ m ='{"method":"get_app_state","id":1}'

#Dither with Settle parameters
#~ m = '{"method": "dither", "params": [2, false, {"pixels": 1.5, "time": 8, "timeout": 40}], "id": 1}'


#~ # Create a socket (SOCK_STREAM means a TCP socket)
#~ sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#~ try:
    #~ # Connect to server and send data
    #~ sock.connect((HOST, PORT))
    #~ # Receive data from the server and shut down
    #~ sock.send(m+'\n')
    #~ time.sleep(1)
    #~ received = sock.recv(1024)

#~ finally:
    #~ sock.close()

#~ print ("Received:     {}".format(received))
#~ print('-'*30)
#~ for x in received.strip().split('\n'):
    #~ if 'jsonrpc' in json.loads(x):

        #~ print ("Received: {}".format(json.loads(x)))

