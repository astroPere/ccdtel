#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

"""
Command INDI Telescope with indi_setprop, indi_getprop & indi_eval

"""

import logging
from time import sleep

import utils

rc = '\033[0m' #reset color
cr = '\033[91m'#red
cg ='\033[32m' #green
cw = '\033[33m'#yellow
cb = '\033[94m'#blue
cy = '\033[36m'#cyan

#TODO: From config file??####################
#TODO: Verify security limits when tracking/slew!
tel =  "Losmandy Gemini"#"LX200 Generic"# #"Telescope Simulator"
port = '7624'
address = '127.0.0.1'

##############################################


log = logging.getLogger(__name__)


Ut = utils.Utils(tel)


class Telescope(object):

    
    def __init__(self, name, address, port, timeout):
        self.tel = name
        self.adress = address
        self.port = port
        self.timeout = 10
        self.tel_properties = {}

    
    def connect(self):
        
        log.info("Connecting {} to indiserver.".format(self.tel))
        
        if Ut.get2("CONNECTION.CONNECT._STATE") == "On":
            log.warning("{}***  {} already connected ***{}".format(cw,self.tel,rc))
        cmd = "CONNECTION.CONNECT=On;DISCONNECT=Off"
        Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==1'
        Ut.eval2(cmd)

        log.info("{}***  {}  Connected!  ***{}".format(cg,self.tel,rc))


    def disconnect(self):
        
        log.info("Disconnecting {} from indiserver.".format(self.tel))
        
        if Ut.get2("CONNECTION.CONNECT._STATE") == "Off":
            log.warning("{}***  {} already disconnected ***{}".format(cw,self.tel,rc))
        cmd = "CONNECTION.CONNECT=Off;DISCONNECT=On"
        Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==0'
        Ut.eval2(cmd)

        log.info("{}*** {} Disconnected! ***{}".format(cr,self.tel,rc))



    def target_coord(self,ra,dec):

        log.info('Slewing to  new target RA/DEC coordinates.')
        log.info('    RA -> {}'.format(ra))
        log.info('    DEC-> {}'.format(dec))
        
        cmd = Ut._set+["{}.EQUATORIAL_EOD_COORD.RA={};DEC={}".format(
                           str(self.tel),str(ra),str(dec))]
        Ut.run(cmd)
        sleep(3)
        #~ sleep(self.timeout) #TODO: refine timeout for telescope hardware!

        while Ut.eval2("EQUATORIAL_EOD_COORD._STATE\"==1") !=0:
            sleep(1)

        log.info('    Done. {} at target position.'.format(self.tel))



    def track(self,value='On'):
        
        log.info('Setting TRACK state to {}.'.format(value))
        
        if value == 'On':
            track, notrack = "On","Off"
        else:
            track, notrack = "Off","On"
              
        cmd1 = ["{}.TELESCOPE_TRACK_STATE.TRACK_ON={};TRACK_OFF={}".format(
                self.tel,str(track),str(notrack))]
        cmd = Ut._set + cmd1
        Ut.run(cmd)
        
        log.info("    Done. {}  TRACK = '{}'.".format(self.tel,track))
        
        
        
    def park(self,value='On'):
        
        log.info('Setting PARK state to {}.'.format(value))
       
        if value == 'On':
            park, unpark = "On","Off"
        else:
            park, unpark = "Off","On"
        
        cmd1 = ["{}.TELESCOPE_PARK.PARK={};UNPARK={}".format(
                self.tel,str(park),str(unpark))]
        cmd = Ut._set + cmd1
        Ut.run(cmd)#TODO: refine timeout for telescope hardware!
        sleep(2)
        if value=='On':Ut.eval2("EQUATORIAL_EOD_COORD._STATE\"==0")
        
        log.info("    Done. {}  PARK = '{}'.".format(self.tel,park))



    #~ def get_all_properties(self,timeout=10,verbose=False):
    def get_all_properties(self,timeout=2,verbose=False):
        return Ut.get_all_properties(timeout, verbose)




    @property
    def ra(self):
        return  float(Ut.get2("EQUATORIAL_EOD_COORD.RA._STATE"))

    @property
    def dec(self):
        return float(Ut.get2("EQUATORIAL_EOD_COORD.DEC._STATE"))

    @property
    def parked(self):
        return Ut.get2("TELESCOPE_PARK.PARK")

    @property
    def track(self):
        return Ut.get2("TELESCOPE_TRACK_STATE.TRACK_ON._STATE")
        
    @property
    def halt(self):
        #returs 0 if succesfully abort
        return Ut.set2("TELESCOPE_ABORT_MOTION.ABORT=Off")

