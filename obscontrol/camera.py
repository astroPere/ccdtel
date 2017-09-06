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


#TODO: From config file??####################

ccd = "CCD Simulator"
port = '7624'
address = '127.0.0.1'

##############################################


log = logging.getLogger(__name__)


Ut = utils.Utils(ccd)


class Camera(object):
   

    def __init__(self):
        
        self.ccd = ccd
        self.adress = address
        self.port = port
        self.timeout = 2.0
        self.ccd_properties = {}



    def connect(self):
        
        log.info("Connecting {} to indiserver.".format(self.ccd))
        
        if Ut.get2("CONNECTION.CONNECT._STATE") == "On":
            log.warning("{}***  {} already connected ***{}".format(cw,self.ccd,rc))
        cmd = "CONNECTION.CONNECT=On;DISCONNECT=Off"
        Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==1'
        Ut.eval2(cmd)

        log.info("{}***  {}  Connected!  ***{}".format(cg,self.ccd,rc))


    def disconnect(self):
        
        log.info("Disconnecting {} from indiserver.".format(self.ccd))
        
        if Ut.get2("CONNECTION.CONNECT._STATE") == "Off":
            log.warning("{}***  {} already disconnected ***{}".format(cw,self.ccd,rc))
        cmd = "CONNECTION.CONNECT=Off;DISCONNECT=On"
        Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==0'
        Ut.eval2(cmd)

        log.info("{}*** {} Disconnected! ***{}".format(cr,self.ccd,rc))



    def expose(self,exp_time=5.0):

        log.info('Starting {}s. exposure.'.format(exp_time))

        path = Ut.get2("UPLOAD_SETTINGS.UPLOAD_DIR")

        cmd1 = Ut._set+["-t",str(exp_time+2),
                        "{}.CCD_EXPOSURE.CCD_EXPOSURE_VALUE={}".format(self.ccd,exp_time)]

        cmd2 = Ut._get+["-t",str(exp_time+2),"{}.CCD1.CCD1".format(self.ccd)] #Client UPLOAD

        log.debug('Running: {}'.format(' '.join(cmd1)))
        subprocess.check_call(cmd1)

        log.debug('Running: {}'.format(' '.join(cmd2)))
        subprocess.check_call(cmd2)

        log.info('Exposure finished.')
        log.info('File {}{}{} succesfully created.'.format(cy,Ut.lastest_file(path),rc))

        return


    def set_filter(self,afilter):

        log.info('Setting {} filter'.format(afilter))
        Ut.set2("FILTER_SLOT.FILTER_SLOT_VALUE={}".format(afilter))
        Ut.eval2("FILTER_SLOT.FILTER_SLOT_VALUE\"=={}".format(afilter))
        log.info('Done. Filter at {} position'.format(afilter))

        return



    def upload_path(self,adir):

        log.info('Setting {} files path'.format(adir))

        Ut.set2("UPLOAD_SETTINGS.UPLOAD_DIR={}".format(adir))
        sleep(1)
        log.debug('Done. Files path = {} '.format(adir))

        return



    def upload_prefix(self,prefix):

        prefix = prefix+'imr_XXX' #Should be defined at main control application ?

        log.info('Setting {} files prefix'.format(prefix))

        Ut.set2("UPLOAD_SETTINGS.UPLOAD_PREFIX={}".format(prefix))
        log.debug('Done. Files prefix = {} '.format(prefix))

        return


    def upload_object(self,name):

        log.info('Setting fits header OBJECT={}.'.format(name))

        Ut.set2("FITS_HEADER.FITS_OBJECT={}".format(name))
        sleep(1)
        log.debug('Done. Fits header OBJECT={}'.format(name))

        return





    def set_upload_mode(self, mode):

        log.info('Setting UPLOAD_MODE to {}.'.format(mode))

        if mode == 'CLIENT': val = ("On","Off","Off")
        if mode == 'LOCAL':  val = ("Off","On","Off")
        if mode == 'BOTH':   val = ("Off","Off","On")

        cmd1 = ["{}.UPLOAD_MODE.UPLOAD_CLIENT={};UPLOAD_LOCAL={};UPLOAD_BOTH={}".format(
                self.ccd,*(val))]
        Ut.run(Ut._set+cmd1,check=False)


    def get_all_properties(self,timeout=2,verbose=False):
        return Ut.get_all_properties(timeout, verbose)



class Filter():


    def __init__(self,filters):
        self.filters = filters #filters list from config file?


    def setf(self,name):

        log.info('Setting {} filter.'.format(name))

        flt = next(f for f in self.filters if f['name']==name)
        Ut.set2("FILTER_SLOT.FILTER_SLOT_VALUE={}".format(flt['slot']))
        Ut.eval2("FILTER_SLOT.FILTER_SLOT_VALUE\"=={}".format(flt['slot']))

        log.info("Done. Filter {}: '{}' in place.".format(*flt.values()))


    @property
    def getf(self):

        log.info('Getting present filter.')

        try:
            cmd = "FILTER_SLOT.FILTER_SLOT_VALUE"
            slot = Ut.get2(cmd)
            flt = next(f for f in self.filters if f['slot']==slot)
            log.info("Filter {}: '{}' in place.".format(*flt.values()))
            return flt
        except:
            log.warning('Filter UNKNOW!')
            return False

