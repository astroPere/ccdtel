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



class Camera(object):
   

    def __init__(self, **kargs):#name, address, port, timeout, filters):
        
        self.Ut = utils.Utils(kargs['name'])
        self.ccd = kargs['name']
        self.adress = kargs['address']
        self.port = kargs['port']
        #~ self.timeout = str(kargs['timeout'])
        self.timeout = float(kargs['timeout'])
        self.ccd_properties = {}

    def connect(self):
        
        log.info("Connecting {} to indiserver.".format(self.ccd))
        
        if self.Ut.get2("CONNECTION.CONNECT._STATE") == "On":
            log.warning("{}*** {} already connected ***{}".format(cw,self.ccd,rc))
        cmd = "CONNECTION.CONNECT=On;DISCONNECT=Off"
        self.Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==1'
        self.Ut.eval2(cmd)

        log.info("{}*** {}  Connected!  ***{}".format(cg,self.ccd,rc))


    def disconnect(self):
        
        log.info("Disconnecting {} from indiserver.".format(self.ccd))
        
        if self.Ut.get2("CONNECTION.CONNECT._STATE") == "Off":
            log.warning("{}*** {} already disconnected ***{}".format(cw,self.ccd,rc))
        cmd = "CONNECTION.CONNECT=Off;DISCONNECT=On"
        self.Ut.set2(cmd)
        cmd = 'CONNECTION._STATE\"==0'
        self.Ut.eval2(cmd)

        log.info("{}*** {} Disconnected! ***{}".format(cr,self.ccd,rc))



    def expose(self,exp_time=5.0,frame=1, nframes=1):

        log.info('Starting {}s. exposure ({}/{}).'.format(exp_time,frame,nframes))

        path = self.Ut.get2("UPLOAD_SETTINGS.UPLOAD_DIR")

        cmd1 = self.Ut._set+["-t",str(exp_time+2),
                        "{}.CCD_EXPOSURE.CCD_EXPOSURE_VALUE={}".format(self.ccd,exp_time)]

        cmd2 = self.Ut._get+["-t",str(exp_time+20),"{}.CCD1.CCD1".format(self.ccd)] #Client UPLOAD

        log.debug('Running: {}'.format(' '.join(cmd1)))
        subprocess.check_call(cmd1)

        log.debug('Running: {}'.format(' '.join(cmd2)))
        subprocess.check_call(cmd2)

        log.info('    Exposure finished.')
        image = self.Ut.lastest_file(path)
        log.info('    File {}{}{} succesfully created.'.format(cy,image,rc))

        return image


    def set_filter(self,afilter):

        log.info('Setting {} filter'.format(afilter))
        self.Ut.set2("FILTER_SLOT.FILTER_SLOT_VALUE={}".format(afilter))
        self.Ut.eval2("FILTER_SLOT.FILTER_SLOT_VALUE\"=={}".format(afilter))
        log.info('Done. Filter at {} position'.format(afilter))

        return



    def upload_path(self,adir):

        log.info('Setting {} files path'.format(adir))

        if self.Ut.set2("UPLOAD_SETTINGS.UPLOAD_DIR={}".format(adir)):
        #~ sleep(1)#TODO: refine timeout for telescope hardware!
            log.debug('    Done. Files path = {} '.format(adir))
            return 0
        else:
            return False


    def upload_prefix(self,prefix):

        prefix = prefix+'_XXX' #Should be defined at main control application ?

        log.info('Setting {} files prefix'.format(prefix))

        self.Ut.set2("UPLOAD_SETTINGS.UPLOAD_PREFIX={}".format(prefix))
        log.debug('    Done. Files prefix = {} '.format(prefix))

        return


    def upload_object(self,name):

        log.info('Setting fits header OBJECT={}.'.format(name))

        self.Ut.set2("FITS_HEADER.FITS_OBJECT={}".format(name))
        #~ sleep(1)#TODO: refine timeout for telescope hardware!
        log.debug('    Done. Fits header OBJECT={}'.format(name))

        return


    def set_upload_mode(self, mode):

        log.info('Setting UPLOAD_MODE to {}.'.format(mode))

        if mode == 'CLIENT': val = ("On","Off","Off")
        if mode == 'LOCAL':  val = ("Off","On","Off")
        if mode == 'BOTH':   val = ("Off","Off","On")

        cmd1 = ["{}.UPLOAD_MODE.UPLOAD_CLIENT={};UPLOAD_LOCAL={};UPLOAD_BOTH={}".format(
                self.ccd,*(val))]
        self.Ut.run(self.Ut._set+cmd1,check=False)
        return


    def get_all_properties(self,timeout=2.0,verbose=False):
        timeout = str(self.timeout)
        return self.Ut.get_all_properties(timeout, verbose)


