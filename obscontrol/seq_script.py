#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
Command INDI ccd with indi_setprop & indi_getprop

"""

import collections
import logging
from time import sleep
import subprocess
from astropy import units as u
from astropy.coordinates import Angle, SkyCoord
import ConfigParser
import io
import sys
import sequence_parser as seqp
import camera as ccd
import telescope as tel


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

### TODO: From config file??#########################################
#####################################################################
rc = '\033[0m' #reset color
cr = '\033[91m'#red
cg ='\033[32m' #green
cw = '\033[33m'#yellow
cb = '\033[94m'#blue
cy = '\033[36m'#cyan
cd = '\033[100m'#gray background

# instruments config
instr_file = ('instruments.txt')
instr_conf = ('Instr',
              'ID instrument img_type tracking exposures exp_time defoc binn roi ifilter')

# targets config
targets_file = ('targets.txt')
targets_conf = ('Target',
                'ID object coord_name coord_acr coord_value coord_epoch')

# constrains config
obsconst_file = ('obs_constrains.txt')
obsconst_conf = ('ObsConst',
                 'ID sun_elev min_air max_air moon_ph moon_elev moon_dist window')


# filters/slot config
filters =[{"name":"B", "slot":"1"},
          {"name":"V", "slot":"2"},
          {"name":"R", "slot":"3"},
          {"name":"I", "slot":"4"}]


# images output path
fits_path = '/home/pere/fits/rawdata/' #Absolute path!


# sequence file
seq_file  = 'seq_lines.txt'

#####################################################################
#####################################################################




def pr(s):
    print('{}{}{}'.format(cd,s,rc))


def check_indi():

    cmd = ['ps','--no-headers','-C','indiserver','-o','pid']
    log.debug('Checking if indiverver is running'+('').join(cmd))

    try:
        subprocess.check_output(cmd)
        log.info ("{}***  INDISERVER is running   ***{}".format(cg,rc))
        print('='*60,'\n')
        return True
    except:
        log.error(cr+"### INDISERVER IS NOT RUNNING ###"+rc)
        return False


def parsig_data_file(afile):

    i = collections.namedtuple(*instr_conf)
    instr_list=[]
    with open(afile,'r') as f:

        for line in f:
            print(cr+line.strip('\n')+rc)
            if not line.startswith('#'):
                fields = line.strip('\n').split('|')
                _name = fields[0].strip()
                _values = [x.strip() for x in fields[1:]]

                instr_list.append(i(_name,*_values))

    for x in instruments_list:
        print(x.ID)
        pr(x)


def config():
    
    config_file="config.cfg"
    log.info("Loading configuration file: '{}'".format(config_file))
    # Load the configuration file
    with open(config_file) as f:
        app_config = f.read()
    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(app_config))

    # log all contents
    for section in config.sections():
        log.debug(section)
        for options in config.options(section):
            log.debug("    {}: {}".format(options, config.get(section, options)))
    return config



def main(args):

    #read config file
    conf = config()
    #First of all, check if indiserver is running
    if not check_indi():
        sys.exit()

    #Initialize telescope & camera
    camera = ccd.Camera(conf.get('camera','name'),
                        conf.get('camera','address'),
                        conf.get('camera','port'),
                        conf.get('camera','timeout'))
    
    telescope = tel.Telescope(conf.get('telescope','name'),
                              conf.get('telescope','address'),
                              conf.get('telescope','port'),
                              conf.get('telescope','timeout'))
    
    
    sys.exit()
    parsig_data_file(inst_file)



    #Define divices objects
    camera = ccd.Camera()
    filterw = ccd.Filter(filters)
    telescope = tel.Telescope()

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

    with open(exec_file,'r') as f:
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
