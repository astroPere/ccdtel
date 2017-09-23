#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

"""
Command INDI ccd with indi_setprop, indi_getprop & indi_eval

"""
import os
from glob import glob
from itertools import groupby
from operator import itemgetter
import subprocess
import logging
from time import sleep

from astropy import units as u
from astropy.coordinates import Angle, SkyCoord


#TODO: From config file??####################

rc = '\033[0m' #reset color
cr = '\033[91m'#red
cg ='\033[32m' #green
cw = '\033[33m'#yellow
cb = '\033[94m'#blue
cy = '\033[36m'#cyan

port = '7624'
address = '127.0.0.1'

a_get  = ["indi_getprop","-h",str(address),"-p",str(port)]
a_set  = ["indi_setprop","-h",str(address),"-p",str(port)]
a_eval = ["indi_eval","-h",str(address),"-p",str(port)]

##############################################


log = logging.getLogger(__name__)


# define Python user-defined exceptions
class Error(Exception):
   """Base class for other exceptions"""
   pass

class GetPropertyError(Error):
    pass


class SetPropertyError(Error):
    pass


class EvalPropertyError(Error):
    pass


class RunCommandError(Error):
    pass



class Utils(object):

    def __init__(self,device):
        self.d = device
        self.d_properties = {}
        self._get  = a_get
        self._set  = a_set
        self._eval = a_eval


    def run(self,cmd,check=False):

        try:
            log.debug('Running: {}'.format(' '.join(cmd)))
            if check:
                return subprocess.check_output(cmd)
            else:
                return subprocess.call(cmd)

        except subprocess.CalledProcessError as e:
            log.error('{}ERROR RUNNING: {}{}'.format(cr,e.cmd,rc))
            return False



    def get2(self,prop):

        prop = prop.split('.')
        fields ="{}"+ ".{}"*len(prop)

        log.debug(("Getting \""+fields+"\" properties").format(self.d,*prop))
        try:
            value = (self.run(self._get+[fields.format(
                     str(self.d),*prop)],check=True).split('='))[-1].strip()
            return value
        except AttributeError:
            log.error("ERROR: Unable to get {}".format(prop))
            return False




    def set2(self, prop, check=False):

        log.debug('Setting: {}.{}'.format(self.d,prop))
        cmd1 = "{}.{}".format(self.d,prop)

        return self.run(self._set+[cmd1], check)



    def eval2(self,prop,check=False,verbose=False):
        #TODO: refine timeouts!!!
        v=""
        if verbose: v="o"
        cmd = ["-w"+v,"-t","5","\"{}.{}".format(str(self.d),prop)]
        log.debug('Evaluation: {}'.format(cmd))
        state = (self.run(self._eval+cmd,check))

        return state



    def lastest_file(self,path):

        log.debug('Looking for latest file at {}'.format(path))
        list_of_files = glob(path+"/*.fits")
        latest_file = max(list_of_files, key=os.path.getctime)

        return latest_file
        
        
        
    def get_all_properties(self,timeout=2,verbose=False):


        log.info("Getting all {} properties.".format(self.d))

        self.device_properties = {}
        #TODO: Verify timeout value with real hardware
        #~ cmd=self._get+["-t",str(timeout),"{}.*.*".format(str(self.d))]
        cmd=self._get+["-1","{}.*.*".format(str(self.d))] #maybe usefull??
        try:
            lines = [msg.split('.',2) for msg in self.run(
                                        cmd,check=True).strip('\n').split('\n')]
            if not lines:
                raise GetPropertyError
            for key, items in groupby(lines, itemgetter(1)):
                self.device_properties[key]={}
                if verbose:
                    log.info('-'*60)
                    log.info('{}:'.format(key))
                else:
                    log.debug(key)
                for subitem in items:
                    self.device_properties[key].update(dict([subitem[-1].split('=')]))
                if verbose:
                    for element, value in self.device_properties[key].items():
                        log.info('    {} = {}'.format(element, value))
                else:
                    for element, value in self.device_properties[key].items():
                        log.debug('   {} = {}'.format(element, value))

            log.debug('    Total {} properties = {}.'.format(
                            self.d,len(self.device_properties)))

            return self.device_properties

        #~ except AttributeError:
        except AttributeError:
            log.error(cr+'ERROR: Unable to get all properties'+rc)
            return False
            


    #dummy funtion ;)
    def pb(x):
        print(cy,x,rc)
        return
