#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
Command INDI ccd with indi_setprop & indi_getprop

"""
import datetime
import collections
import re
import logging
from time import sleep
import subprocess
from astropy import units as u
from astropy.coordinates import Angle, SkyCoord,FK5,ICRS
import ConfigParser
import io
import sys
import sequence_parser as seqp
import camera as ccd
import telescope as tel


rc = '\033[0m' #reset color
cr = '\033[91m'#red
cg ='\033[32m' #green
cw = '\033[33m'#yellow
cb = '\033[94m'#blue
cy = '\033[36m'#cyan
cd = '\033[100m'#gray background

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





def config():
    
    config_file="config.cfg"
    log.info("Loading configuration file: '{}'".format(config_file))
    # Load the configuration file
    with open(config_file) as f:
        app_config = f.read()

    config = ConfigParser.SafeConfigParser(allow_no_value=True)
    config.readfp(io.BytesIO(app_config))
    # log all contents
    for section in config.sections():
        log.debug(section)
        for options in config.options(section):
            log.debug("    {}: {}".format(options, config.get(section, options)))

    return config
    
    
def parsig_data_file(data_file, data_conf):
    
    data_conf = getlist(data_conf)
    i = collections.namedtuple(*data_conf)
    data_list=[]
    with open(data_file,'r') as f:
        for line in f:
            if not line.startswith('#'):
                fields = line.strip('\n').split('|')
                _name = fields[0].strip()
                _values = [x.strip() for x in fields[1:]]
                data_list.append(i(_name,*_values))

    return data_list
    
    
def getlist(option, sep=',', chars=None):
    """Return a list from a ConfigParser option. By default, 
       split on a comma and strip whitespaces."""
    return [ chunk.strip(chars) for chunk in option.split(sep) ]





#First of all, check if indiserver is running
#~ if not check_indi():
    #~ sys.exit()
#read config file
conf = config()
#Initialize general parameters
exec_file = conf.get('general','exec_file')
# instruments config
instr_file = conf.get('instruments','data_file')
instr_conf = conf.get('instruments','data_conf')
instruments = parsig_data_file(instr_file,instr_conf)

# targets config
targets_file = conf.get('targets','data_file')
targets_conf = conf.get('targets','data_conf')

targets = parsig_data_file(targets_file,targets_conf)

# constrains config
obsconstr_file = conf.get('obsconstrains','data_file')
obsconstr_conf = conf.get('obsconstrains','data_conf')
obsconstrains = parsig_data_file(obsconstr_file,obsconstr_conf)

filters = dict(conf.items('filters'))
# images output path
fits_path = conf.get('images','download_path')



#Initialize telescope & camera
camera = ccd.Camera(conf.get('camera','name'),
                    conf.get('camera','address'),
                    conf.get('camera','port'),
                    conf.get('camera','timeout'))

telescope = tel.Telescope(conf.get('telescope','name'),
                          conf.get('telescope','address'),
                          conf.get('telescope','port'),
                          conf.get('telescope','timeout'))

filterw = ccd.Filter(filters,
                     conf.get('filterw','name'),
                     conf.get('filterw','address'),
                     conf.get('filterw','port'),
                     conf.get('filterw','timeout'))


    #~ #Defining some targets:
    #~ vega = {'object': "Vega",
            #~ 'ra':  '18:37:02.255',
            #~ 'dec': '38:48:03.64' }

    #~ mel20 = {'object': "Mel20",
             #~ 'ra':'03h25m34.2s',
             #~ 'dec':'+49d55m42s'}

    #~ m34 = {'object': "M34",
             #~ 'ra': '02h43m14.6s',
             #~ 'dec': '+42:51:29'}
    
    #~ m92A = {'object': "M92_J2000",
             #~ 'ra': '17h17m06.0s',
             #~ 'dec':'+43d08m00s'}

    #~ m92B = {'object': "M92_EOD",
             #~ 'ra': ' 17h17m38.6s ',
             #~ 'dec':'+43d06m54s'}


    #~ Vega = SkyCoord(vega['ra'],vega['dec'],unit=(u.hourangle, u.deg))
    #~ Mel20 = SkyCoord(mel20['ra'],mel20['dec'],unit=(u.hourangle, u.deg))
    #~ M34 = SkyCoord(m34['ra'],m34['dec'],unit=(u.hourangle, u.deg))
    #~ M92A = SkyCoord(m92A['ra'],m92A['dec'],unit=(u.hourangle, u.deg))
    #~ M92B = SkyCoord(m92B['ra'],m92B['dec'],unit=(u.hourangle, u.deg))

    #~ target1 = (Vega.ra.hour, Vega.dec.degree)
    #~ target2 = (Mel20.ra.hour, Mel20.dec.degree)
    #~ target3 = (M34.ra.hour, M34.dec.degree)
    #~ target4 = (M92A.ra.hour, M92A.dec.degree)
    #~ target5 = (M92B.ra.hour, M92B.dec.degree)






    #~ with open(exec_file,'r') as f:
        #~ pr('-------------- START EXEC -------------')
        #~ for line in f:
            #~ exec line
        #~ pr('--------------  END EXEC --------------')















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

    

def pstoi(toi,text_pattern):
    """extract name = x from toi id. = j"""
    xxx = ''
    try:
        for name in text_pattern:
            xx =re.findall(r'{0}\d+'.format(name),toi)
            xxx =xxx+''.join(xx)
        return xxx
    except:
        return xxx



def track(t):

    atarget = next(trg for trg in targets if trg.ID==t)
    #~ t_ra, t_dec = coord2EOD(atarget,atarget.equinox)
    t_coord = coord2EOD(atarget,atarget.equinox)
    log.info('Looking for cooordinates: {}'.format(t_coord))
    telescope.target_coord(*t_coord)


def expose(i):

    ainstr = next(ins for ins in instruments if ins.ID==i)
    targ_instr = pstoi(i,'t')
    obj_name = next(trg.obj_name for trg in targets if pstoi(trg.ID,'t')==targ_instr)
    
    camera.upload_object(obj_name)
    camera.upload_path(fits_path+obj_name+"/")
    camera.upload_prefix("_"+obj_name+"_")
    
    filterw.setf(ainstr.ifilter)

    for x in range(int(ainstr.exposures)):
        camera.expose(float(ainstr.exp_time),x+1,ainstr.exposures)


def coord2EOD(atarget,equinox):
    
    #coordinates from targets file
    atarget = SkyCoord(atarget.coord_value,
                       unit=(u.hourangle, u.deg),
                       equinox=atarget.equinox)
    #coordinates EOD (UTC now)
    otarget = atarget.transform_to(FK5(equinox=datetime.datetime.utcnow()))

    return otarget.ra.hour, otarget.dec.degree
  
  
  

def main(args):

    #~ #First of all, check if indiserver is running
    if not check_indi():
        sys.exit()

    #Connect devices to indiserver
    telescope.connect()
    camera.connect()
    #Initial delay to ensure connections are ready
    sleep(2)
    #Setting camera upload mode
    camera.set_upload_mode("BOTH")
    #Reading properties
    telescope.get_all_properties()
    camera.get_all_properties()
    #Unpark telescope
    telescope.set_park('Off') #TODO!!!
    #Getting present filter
    filterw.getf

#*******************************************************************


    with open(exec_file,'r') as f:
        for line in f:
             if not line.startswith('#'):
                line=line.strip('\n')
                log.info('Executing line: {}'.format(line))
                exec line

    #~ target = next(trg for trg in targets if target.ID==t)
    #~ target.coord_value)




#*******************************************************************

    telescope.set_park('On') #TODO!

    telescope.disconnect()
    camera.disconnect()


    
    
    sys.exit()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
