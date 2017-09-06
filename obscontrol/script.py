#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
Command INDI ccd with indi_setprop & indi_getprop

"""


import logging
from time import sleep
import subprocess
from astropy import units as u
from astropy.coordinates import Angle, SkyCoord

import ccd_shell
import telescope_shell


log = logging.getLogger()
log.setLevel(logging.DEBUG)

formatter  = logging.Formatter('%(asctime)s| %(levelname)-7s| %(message)s')
#~ formatter1 = logging.Formatter('%(asctime)s > %(message)s')
formatter1 = logging.Formatter(' > %(message)s')
#File logger
fh = logging.FileHandler('shtel.log','w')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)
#Console logger
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter1)
log.addHandler(ch)

#TODO: From config file??####################

rc = '\033[0m' #reset color
cr = '\033[91m'#red
cg ='\033[32m' #green
cw = '\033[33m'#yellow
cb = '\033[94m'#blue
cy = '\033[36m'#cyan
cd = '\033[100m'#gray background


def_timeout = 2

filters =[{"name":"B", "slot":"1"},
          {"name":"V", "slot":"2"},
          {"name":"R", "slot":"3"},
          {"name":"I", "slot":"4"}]

fits_path = 'fits/rawdata' #Absolute path!
seq_file  = 'seq_lines.txt'
##############################################




def pr(s):
    print('{}{}{}'.format(cd,s,rc))


def check_indi():
    
    cmd = ['ps','--no-headers','-C','indiserver','-o','pid']
    log.debug('Checking if indiverver is running'+('').join(cmd))
    
    try:
        subprocess.check_output(cmd)
        log.info ("{}***  INDISERVER is running   ***{}".format(cg,rc))
        print('='*60,'\n')
        return
    except:
        log.error(cr+"### INDISERVER IS NOT RUNNING ###"+rc)
        sys.exit()
    




def main(args):

    #First of all, check if indiserver is running
    check_indi()

    #Define divices objects
    camera = ccd_shell.Camera()
    filterw = ccd_shell.Filter(filters)
    telescope = telescope_shell.Telescope()
    
    #Connect devices to indiserver
    telescope.connect()
    camera.connect()
    
    #Initial delay to ensure connections are ready
    sleep(2)
    
    
    filterw.getf
    

    #Reading properties
    telescope.get_all_properties()
    sleep(1)
    camera.get_all_properties()

    #Defining some targets:
    vega = {'object': "Vega",
            'ra':  '18:37:02.255',
            'dec': '38:48:03.64' }
            
    mel20 = {'object': "Mel20",
             'ra':'03h25m34.2s',
             'dec':'+49d55m42s'}         
            
    m34 = {'object': "M34",
             'ra': '02h43m14.6s',
             'dec': '+42:51:29'}         


    Vega = SkyCoord(vega['ra'],vega['dec'],unit=(u.hourangle, u.deg))
    Mel20 = SkyCoord(mel20['ra'],mel20['dec'],unit=(u.hourangle, u.deg))
    M34 = SkyCoord(m34['ra'],m34['dec'],unit=(u.hourangle, u.deg))

    target1 = (Vega.ra.hour, Vega.dec.degree)
    target2 = (Mel20.ra.hour, Mel20.dec.degree)
    target3 = (M34.ra.hour, M34.dec.degree)



    camera.set_upload_mode("BOTH")

    telescope.set_park('Off') #TODO!!!

    #~ filterw.getf #is a property
    
    with open(seq_file,'r') as f:
        pr('-------------- START EXEC -------------')
        for line in f:
            exec line
        pr('--------------  END EXEC --------------')
    
    #Only for test
    telescope.set_track('Off')

    
    telescope.set_park('On') #TODO!
    
    telescope.disconnect()
    camera.disconnect()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
