#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
Command INDI ccd with indi_setprop & indi_getprop

"""
#~ import hashlib
from datetime import datetime
from collections import namedtuple
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
import filterwheel as fltw


rc = '\033[0m' #reset color
cr = '\033[91m'#red
cg ='\033[32m' #green
cw = '\033[33m'#yellow
cb = '\033[94m'#blue
cy = '\033[36m'#cyan
cd = '\033[100m'#gray background

log = logging.getLogger()
log.setLevel(logging.DEBUG)

#~ formatter  = logging.Formatter('%(asctime)s| %(levelname)-7s| %(message)s')
formatter  = logging.Formatter("[%(asctime)s|%(filename)s:%(lineno)s - %(funcName)s] %(message)s")
#~ formatter1 = logging.Formatter('%(asctime)s > %(message)s')
formatter1 = logging.Formatter(' > %(message)s')
#File logger
logfile = datetime.strftime(datetime.utcnow(),'%Y%m%d.log')
#~ fh = logging.FileHandler('fli_gemini.log','a')
fh = logging.FileHandler(logfile,'a')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(fh)
#Console logger
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter1)
log.addHandler(ch)





def config():

    #~ config_file="config.cfg"
    #~ config_file="simulator_config.cfg"
    config_file="gemini_fli_config.cfg"
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


def parsing_config_file(data_file, data_conf):

    data_conf = getlist(data_conf)
    i = namedtuple(*data_conf)
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
    return [ piece.strip(chars) for piece in option.split(sep) ]



def hashfile(path, blocksize = 65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()




def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()



#First of all, check if indiserver is running
#~ if not check_indi():
    #~ sys.exit()
#read config file
conf = config()
#Initialize general parameters
allowed_delay = conf.get('general', 'allowed_delay')
max_wait = conf.get('general', 'max_wait')
exec_file = conf.get('general','exec_file')
execline_conf = conf.get('general', 'exec_conf')

# instruments config
instr_file = conf.get('instruments','data_file')
instr_conf = conf.get('instruments','data_conf')
instruments = parsing_config_file(instr_file,instr_conf)

# targets config
targets_file = conf.get('targets','data_file')
targets_conf = conf.get('targets','data_conf')
targets = parsing_config_file(targets_file,targets_conf)

# constrains config
obsconstr_file = conf.get('obsconstrains','data_file')
obsconstr_conf = conf.get('obsconstrains','data_conf')
obsconstrains = parsing_config_file(obsconstr_file,obsconstr_conf)




filters = dict(conf.items('filters'))
# images output path
fits_path = conf.get('images','download_path')



#Initialize telescope, camera, filterwheel
camera = ccd.Camera(name = conf.get('camera','name'),
                    address = conf.get('camera','address'),
                    port = conf.get('camera','port'),
                    timeout = conf.get('camera','timeout'))

telescope = tel.Telescope(name = conf.get('telescope','name'),
                          address = conf.get('telescope','address'),
                          port = conf.get('telescope','port'),
                          timeout = conf.get('telescope','timeout'),
                          settle_timeout = conf.get('telescope','settle_timeout'))

filterw = fltw.FilterWheel(name = conf.get('filterw','name'),
                           address = conf.get('filterw','address'),
                           port = conf.get('filterw','port'),
                           timeout = conf.get('filterw','timeout'),
                           filters = filters)











def pr(s):
    print('{}{}{}'.format(cd,s,rc))


def check_indi():

    cmd = ['ps','--no-headers','-C','indiserver','-o','pid']
    log.debug('Checking if indiverver is running: {}'.format((' ').join(cmd)))

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

    log.debug('Executing track={}'.format(t))
    t = pstoi(t,'pt')
    atarget = next(trg for trg in targets if trg.ID==t)
    t_coord = coord2EOD(atarget,atarget.equinox)
    log.info('Looking for cooordinates: {}.'.format(t_coord[1]))
    telescope.target_coord(*t_coord)
    return

def observe(i):

    log.debug('Executing observe={}'.format(i))
    t = pstoi(i,'pt')
    track(t)
    i_instr = pstoi(i,'pi')
    ainstr = next(ins for ins in instruments if pstoi(ins.ID,'pi')==i_instr)
    i_targ = pstoi(i,'pt')
    obj_name = next(trg.obj_name for trg in targets if pstoi(trg.ID,'pt')==i_targ)

    camera.upload_object(obj_name)
    camera.upload_path(fits_path+obj_name+"/")
    camera.upload_prefix("_"+obj_name+"_")

    filterw.setf(ainstr.ifilter)

    for x in range(int(ainstr.exposures)):
        camera.expose(float(ainstr.exp_time),x+1,ainstr.exposures)



def expose(i):

    log.debug('Executing expose={}'.format(i))

    i_instr = pstoi(i,'pi')
    ainstr = next(ins for ins in instruments if pstoi(ins.ID,'pi')==i_instr)
    i_targ = pstoi(i,'pt')
    obj_name = next(trg.obj_name for trg in targets if pstoi(trg.ID,'pt')==i_targ)

    camera.upload_object(obj_name)
    camera.upload_path(fits_path+obj_name+"/")
    camera.upload_prefix("_"+obj_name+"_")

    filterw.setf(ainstr.ifilter)

    for x in range(int(ainstr.exposures)):
        camera.expose(float(ainstr.exp_time),x+1,ainstr.exposures)


def coord2EOD(atarget,equinox):

    log.debug('Parsing EOD coords. targ={}'.format(atarget))
    #coordinates from targets file
    atarget = SkyCoord(atarget.coord_value,
                       unit=(u.hourangle, u.deg),
                       equinox=atarget.equinox)
    #coordinates EOD (UTC now)
    otarget = atarget.transform_to(FK5(equinox=datetime.utcnow()))
    log.debug('Returned coords.RA:{} DEC:{}'.format(
              otarget.ra.hour, otarget.dec.degree))
    return otarget.ra.hour, otarget.dec.degree


def parsing_exec_line(aline):

    log.debug('Parsing line: {}'.format(aline))

    _execline_conf = getlist(execline_conf)
    ex = namedtuple(*_execline_conf)
    aline = [_line.strip() for _line in aline.split(',') if len(_line)>0]
    aline = ex(*aline)
    log.debug('Parsed  line: {}'.format(aline))

    return aline


def exec_wait(edatetime):

    log.debug('Executing wait for {}'.format(edatetime))

    exectime = datetime.strptime(edatetime,'%Y%m%d%H:%M:%S')
    delay = int((exectime-datetime.utcnow()).total_seconds())
    #TODO: Should MIN/MAX allowed delay be configured??
    #~ if -60 <= delay <= 60:#in seconds!
    if -(int(allowed_delay)) <= delay <= int(allowed_delay):#in seconds!
        log.info('    Line in time, {}s delayed'.format(delay))
        return True
    elif int(max_wait) > delay > int(allowed_delay):#in seconds (28800s = 8 hours!)
        log.info(cw+'... Waiting {}s -> {}'.format(delay,exectime)+rc)
        while exectime >= datetime.utcnow():
            sleep(1)
        return True
    else:
        log.warning(cw+'    Skipping line due to a {}s delay.'.format(delay)+rc)
        return False


def main(args):

    try:

        #~ #First of all, check if indiserver is running
        if not check_indi():
            sys.exit()

        #Connect devices to indiserver
        telescope.connect()### TODO: FIFO connection!!! <---!!!
        camera.connect()### TODO: FIFO connection!
        filterw.connect()### TODO: FIFO connection!

        #Initial delay to ensure connections are ready
        sleep(2)
        #Setting camera upload mode
        camera.set_upload_mode("BOTH")
        #Reading properties

        telescope.get_all_properties()
        #~ sleep(1)
        camera.get_all_properties()
        #~ sleep(1)
        filterw.get_all_properties()
        #Unpark telescope
        telescope.park('Off') #TODO!!!
        #Getting present filter
        filterw.getf

    #*******************************************************************

        lcount = 0
        with open(exec_file,'r') as f:
            for line in f:
                 if len(line.strip())>0 and not line.startswith('#'):
                    lcount += 1
                    xline=line.strip('\n').strip()
                    xline = parsing_exec_line(xline)
                    log.info("Executing line #{}:  {} {}".format(
                             lcount,xline.function,xline.pti.lower()))
                    #~ #waiting for execution date/time
                    if exec_wait(xline.edate+xline.etime):
                        exec "{}('{}')".format(xline.function.lower(),xline.pti.lower())

        sleep(2)
    #*******************************************************************

        telescope.park('On') #TODO eval park state!

        telescope.disconnect()
        sleep(1)
        camera.disconnect()
        sleep(1)
        filterw.disconnect()
        sleep(1)
    except(KeyboardInterrupt,SystemExit):
        log.warning(cw+"TELESCOPE HALTED!"+rc)
        telescope.halt
        telescope.disconnect()
        camera.disconnect()
        filterw.disconnect()
        #~ raise



    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
