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


log = logging.getLogger(__name__)



class Telescope(object):

    
    def __init__(self, **kargs):
        
        self.Ut = utils.Utils(kargs['name'])
        self.tel = kargs['name']
        self.address = kargs['address']
        self.port = kargs['port']
        self.timeout = float(kargs['timeout'])
        self.settle_timeout = float(kargs['settle_timeout'])
        self.tel_properties = {}

    
    def connect(self):
        
        log.info("Connecting {} to indiserver.".format(self.tel))
        
        if self.Ut.get2("CONNECTION.CONNECT._STATE") == "On":
            log.warning("{}*** {} already connected ***{}".format(cw,self.tel,rc))
        cmd = "CONNECTION.CONNECT=On;DISCONNECT=Off"
        self.Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==1'
        self.Ut.eval2(cmd)

        log.info("{}*** {}  Connected!  ***{}".format(cg,self.tel,rc))


    def disconnect(self):
        
        log.info("Disconnecting {} from indiserver.".format(self.tel))
        
        if self.Ut.get2("CONNECTION.CONNECT._STATE") == "Off":
            log.warning("{}*** {} already disconnected ***{}".format(cw,self.tel,rc))
        cmd = "CONNECTION.CONNECT=Off;DISCONNECT=On"
        self.Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==0'
        self.Ut.eval2(cmd)

        log.info("{}*** {} Disconnected! ***{}".format(cr,self.tel,rc))



    def target_coord(self,ra,dec):

        log.info('Slewing to  new target RA/DEC coordinates.')
        log.info('    RA -> {}'.format(ra))
        log.info('    DEC-> {}'.format(dec))
        
        cmd = self.Ut._set+["{}.EQUATORIAL_EOD_COORD.RA={};DEC={}".format(
                           str(self.tel),str(ra),str(dec))]
        self.Ut.run(cmd)
        sleep(self.timeout) #TODO: refine timeout for telescope hardware!

        #~ while self.Ut.eval2("EQUATORIAL_EOD_COORD._STATE\"==1", verbose=True) !=0:
            #~ sleep(1)
        self.Ut.eval2("EQUATORIAL_EOD_COORD._STATE\"==1")
        sleep(1)
        log.info('    Done. {} at target position.'.format(self.tel))
        log.info('    Wait {}s.for telescope settle.'.format(self.settle_timeout))
        sleep(self.settle_timeout)
        



    def track(self,value='On'):
        
        log.info('Setting TRACK state to {}.'.format(value))
        
        if value == 'On':
            track, notrack = "On","Off"
        else:
            track, notrack = "Off","On"
              
        cmd1 = ["{}.TELESCOPE_TRACK_STATE.TRACK_ON={};TRACK_OFF={}".format(
                self.tel,str(track),str(notrack))]
        cmd = self.Ut._set + cmd1
        self.Ut.run(cmd)
        
        log.info("    Done. {}  TRACK = '{}'.".format(self.tel,track))
        
        
        
    def park(self,value='On'):
        
        log.info('Setting PARK state to {}.'.format(value))
       
        if value == 'On':
            park, unpark = "On","Off"
        else:
            park, unpark = "Off","On"
        
        cmd1 = ["{}.TELESCOPE_PARK.PARK={};UNPARK={}".format(
                self.tel,str(park),str(unpark))]
        cmd = self.Ut._set + cmd1
        self.Ut.run(cmd)#TODO: refine timeout for telescope hardware!
        #~ sleep(2)
        sleep(self.timeout)
        if value=='On':self.Ut.eval2("EQUATORIAL_EOD_COORD._STATE\"==0")
        
        log.info("    Done. {}  PARK = '{}'.".format(self.tel,park))


        
        
        
    def sync_coord(self,coord):
        
        log.info('Syncronicing Coordinates: {}.'.format(coord))

        
        cmd1 = ["{}.ON_COORD_SET.TRACK=Off;SLEW=Off;SYNC=On".format(self.tel)]
        cmd = self.Ut._set + cmd1
        self.Ut.run(cmd)#TODO: refine timeout for telescope hardware!
        sleep(self.timeout)
        
        cmd1 = ["{}.ON_COORD_SET.TRACK=On;SLEW=Off;SYNC=Off".format(self.tel)]
        cmd = self.Ut._set + cmd1
        self.Ut.run(cmd)#TODO: refine timeout for telescope hardware!
        sleep(self.timeout)
        
        log.info("    Done. RA,DEC = '{}'.".format(coord))
        



    def get_all_properties(self,timeout=2.0,verbose=False):
        timeout = self.timeout
        return self.Ut.get_all_properties(timeout, verbose)




    @property
    def ra(self):
        return  float(self.Ut.get2("EQUATORIAL_EOD_COORD.RA._STATE"))

    @property
    def dec(self):
        return float(self.Ut.get2("EQUATORIAL_EOD_COORD.DEC._STATE"))

    @property
    def isparked(self):
        return self.Ut.get2("TELESCOPE_PARK.PARK")

    @property
    def istrack(self):
        return self.Ut.get2("TELESCOPE_TRACK_STATE.TRACK_ON._STATE")
        
    @property
    def halt(self):
        #returs 0 if succesfully abort
        return self.Ut.set2("TELESCOPE_ABORT_MOTION.ABORT=Off")

