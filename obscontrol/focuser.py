#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

"""
Command INDI Camera with indi_setprop, indi_getprop & indi_eval

"""

import subprocess
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



class Focuser(object):
   

    def __init__(self, **kargs):#name, address, port, timeout, filters):
        
        self.Ut = utils.Utils(kargs['name'])
        self.foc = kargs['name']
        self.adress = kargs['address']
        self.port = kargs['port']
        self.timeout = float(kargs['timeout'])
        self.ccd_properties = {}

    def connect(self):
        
        log.info("Connecting {} to indiserver.".format(self.foc))
        
        if self.Ut.get2("CONNECTION.CONNECT._STATE") == "On":
            log.warning("{}*** {} already connected ***{}".format(cw,self.foc,rc))
        cmd = "CONNECTION.CONNECT=On;DISCONNECT=Off"
        self.Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==1'
        self.Ut.eval2(cmd)

        log.info("{}*** {}  Connected!  ***{}".format(cg,self.foc,rc))


    def disconnect(self):
        
        log.info("Disconnecting {} from indiserver.".format(self.foc))
        
        if self.Ut.get2("CONNECTION.CONNECT._STATE") == "Off":
            log.warning("{}*** {} already disconnected ***{}".format(cw,self.foc,rc))
        cmd = "CONNECTION.CONNECT=Off;DISCONNECT=On"
        self.Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==0'
        self.Ut.eval2(cmd)

        log.info("{}*** {} Disconnected! ***{}".format(cr,self.foc,rc))


    def get_abs_pos(self):
        
        log.info('Getting {} absolute position.'.format(self.foc))

        try:
            cmd = "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION"
            pos = self.Ut.get2(cmd)
            log.info("    {} abs.position = '{}'.".format(self.foc,pos))
            return pos
        except:
            log.warning('    Position UNKNOW!')
            return False



    def set_move_mode(self, mode="IN"):

        log.info("Setting Focus Movement to '{}'.".format(mode))

        if mode == "IN": val = ("On","Off")
        if mode == "OUT":  val = ("Off","On")

        cmd1 = ["{}.FOCUS_MOTION.FOCUS_INWARD={};FOCUS_OUTWARD={}".format(
                self.foc,*val)]
        self.Ut.run(self.Ut._set+cmd1,check=False)
        sleep(2)
        log.info("    Done. Focus Move = '{}' ".format(mode))
        return



    def move_abs_pos(self,pos):

        log.info("Moving {} to  '{}' abs.position.".format(self.foc,pos))
        
        cmd = self.Ut._set+["{}.ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION={}".format(
                           self.foc,pos)]
        self.Ut.run(cmd)
        #~ sleep(self.timeout) #TODO: refine timeout for focuser hardware!
        sleep(2) #TODO: refine timeout for focuser hardware!

        self.Ut.eval2("ABS_FOCUS_POSITION._STATE\"==1")
        sleep(1)
        log.info("    Done. {} abs.position = '{}'.".format(self.foc,pos))

        return
        

    def move_steps_in(self,steps):
        
        log.info("Moving {} IN '{}' steps.".format(self.foc,steps))
        
        self.set_move_mode('IN')
        
        cmd = self.Ut._set+["{}.REL_FOCUS_POSITION.FOCUS_RELATIVE_POSITION={}".
                            format(str(self.foc),str(steps))]
        self.Ut.run(cmd)
        sleep(2) #TODO: refine timeout for focuser hardware!

        self.Ut.eval2("ABS_FOCUS_POSITION._STATE\"==1")
        #~ sleep(1)
        log.info("    Done. {} moved '{}' steps inwards.".format(self.foc,steps))

        return

    def move_steps_out(self,steps):
        
        log.info("Moving {} OUT '{}' steps.".format(self.foc,steps))
        
        self.set_move_mode('OUT')
        
        cmd = self.Ut._set+["{}.REL_FOCUS_POSITION.FOCUS_RELATIVE_POSITION={}".
                            format(self.foc,str(steps))]
        self.Ut.run(cmd)
        sleep(2) #TODO: refine timeout for focuser hardware!

        self.Ut.eval2("ABS_FOCUS_POSITION._STATE\"==1")
        #~ sleep(1)
        log.info("    Done. {} moved '{}' steps outwards.".format(self.foc,steps))

        return



    def defocus(self,steps, mode="IN"):
        
        log.info("Applying {} {} defocus".format(self.foc,mode))
        
        if mode.upper == "OUT": 
            self.move_steps_out(steps)
        else:
            self.move_steps_in(steps)

            


    def get_all_properties(self,timeout=2.0,verbose=False):
        timeout = str(self.timeout)
        return self.Ut.get_all_properties(timeout, verbose)


