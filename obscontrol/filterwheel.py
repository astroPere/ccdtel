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



class FilterWheel(object):


    #~ def __init__(self, name, address, port, timeout, filters):
    def __init__(self, **kargs):#name, address, port, timeout, filters):
        
        self.Ut = utils.Utils(kargs['name'])
        self.fltw = kargs['name']
        self.adress = kargs['address']
        self.port = kargs['port']
        self.timeout = str(kargs['timeout'])
        self.filters = kargs['filters']
        self.fltw_properties = {}
        
        
        
    def connect(self):
        
        log.info("Connecting {} to indiserver.".format(self.fltw))
        
        if self.Ut.get2("CONNECTION.CONNECT._STATE") == "On":
            log.warning("{}*** {} already connected ***{}".format(cw,self.fltw,rc))
        cmd = "CONNECTION.CONNECT=On;DISCONNECT=Off"
        self.Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==1'
        self.Ut.eval2(cmd)

        log.info("{}*** {}  Connected!  ***{}".format(cg,self.fltw,rc))


    def disconnect(self):
        
        log.info("Disconnecting {} from indiserver.".format(self.fltw))
        
        if self.Ut.get2("CONNECTION.CONNECT._STATE") == "Off":
            log.warning("{}*** {} already disconnected ***{}".format(cw,self.fltw,rc))
        cmd = "CONNECTION.CONNECT=Off;DISCONNECT=On"
        self.Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==0'
        self.Ut.eval2(cmd)

        log.info("{}*** {} Disconnected! ***{}".format(cr,self.fltw,rc))



    def get_all_properties(self,timeout=2.0,verbose=False):
        timeout = self.timeout
        return self.Ut.get_all_properties(timeout, verbose)


    def setf(self,name):

        log.info('Setting {} filter.'.format(name))
        
        
        slot = next(key for key,val in self.filters.items() if val==name)
        self.Ut.set2("FILTER_SLOT.FILTER_SLOT_VALUE={}".format(slot))
        sleep(1)
        while self.Ut.eval2("FILTER_SLOT.FILTER_SLOT_VALUE\"=={}".format(slot)) != 0:
            log.debug("Switching filter to: {}: '{}'".format(slot,self.filters[slot]))
            sleep(self.timeout)
        log.info("    Done. Filter {}: '{}' in place.".format(slot,self.filters[slot]))


    @property
    def getf(self):

        log.info('Getting {} present filter.'.format(self.fltw))

        try:
            cmd = "FILTER_SLOT.FILTER_SLOT_VALUE"
            slot = self.Ut.get2(cmd)
            log.info("Filter {}: '{}' in place.".format(
                    slot,self.filters[slot]))
            return self.filters[slot]
        except:
            log.warning('Filter UNKNOW!')
            return False
