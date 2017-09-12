#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

"""
Command INDI Telescope with indi_setprop, indi_getprop & indi_eval

"""
import ConfigParser
import io
import sys
import logging
from collections import namedtuple
from time import sleep
from datetime import datetime
import subprocess
import re
import camera as ccd
import telescope as tel
import filterwheel as fltw
from astropy import units as u
from astropy.coordinates import Angle, SkyCoord,FK5,ICRS

import utils

rc = '\033[0m' #reset color
cr = '\033[91m'#red
cg ='\033[32m' #green
cw = '\033[33m'#yellow
cb = '\033[94m'#blue
cy = '\033[36m'#cyan
cd = '\033[100m'#gray background

log = logging.getLogger(__name__)



class Session(object):

    def __init__(self,config_file):

        conf = self._load_config(config_file)

        #Initialize general parameters
        self.allowed_delay = conf.get('general', 'allowed_delay')
        self.max_wait = conf.get('general', 'max_wait')
        self.exec_file = conf.get('general','exec_file')
        self.execline_conf = conf.get('general', 'exec_conf')

        # instruments config
        instr_file = conf.get('instruments','data_file')
        instr_conf = conf.get('instruments','data_conf')
        self.instruments = self._parsing_config_file(instr_file,instr_conf)

        # targets config
        targets_file = conf.get('targets','data_file')
        targets_conf = conf.get('targets','data_conf')
        self.targets = self._parsing_config_file(targets_file,targets_conf)

        # constrains config
        obsconstr_file = conf.get('obsconstrains','data_file')
        obsconstr_conf = conf.get('obsconstrains','data_conf')
        self.obsconstrains = self._parsing_config_file(obsconstr_file,obsconstr_conf)

        #filters/slots config
        self.filters = dict(conf.items('filters'))

        # images output path
        self.fits_path = conf.get('images','download_path')

        #Initialize telescope, camera, filterwheel
        self.camera = ccd.Camera(name = conf.get('camera','name'),
                                 address = conf.get('camera','address'),
                                 port = conf.get('camera','port'),
                                 timeout = conf.get('camera','timeout'))

        self.telescope = tel.Telescope(name = conf.get('telescope','name'),
                                 address = conf.get('telescope','address'),
                                 port = conf.get('telescope','port'),
                                 timeout = conf.get('telescope','timeout'),
                                 settle_timeout = conf.get('telescope','settle_timeout'))

        self.filterw = fltw.FilterWheel(name = conf.get('filterw','name'),
                                 address = conf.get('filterw','address'),
                                 port = conf.get('filterw','port'),
                                 timeout = conf.get('filterw','timeout'),
                                 filters = self.filters)

        self.halt_flag = False
        
        

#### Configuration functions ###############################################

    def _load_config(self,config_file="simulator_config.cfg"):

        log.info("Loading configuration file: '{}'".format(config_file))

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

    def _getlist(self,option, sep=',', chars=None):
        """Return a list from a ConfigParser option. By default,
           split on a comma and strip whitespaces."""
        return [piece.strip(chars) for piece in option.split(sep)]


    def _parsing_config_file(self,data_file, data_conf):

        data_conf = self._getlist(data_conf)
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
############################################################################


    def init(self, at_time=False):

        log.info("Setting GLOBAL STATE = 'On'")

        if not self._check_indi():
            #~ return -1
            sys.exit()

        if at_time:
            init_time = self._format_date(at_time)
            log.info('Executing wait for {}'.format(init_time))
            delay = int((init_time-datetime.utcnow()).total_seconds())
            #TODO: Should MIN/MAX allowed delay be configured??
            #~ if -60 <= delay <= 60:#in seconds!
            if delay < 0:
                log.warning(cw+'    Skipping due to a {}s delay.'.format(delay)+rc)                
                log.error(cr+"Can't initialize session at {}".format(at_time)+rc)
                sys.exit()
            
            log.info(cg+'... Waiting {}s -> {}'.format(delay,init_time)+rc)
            while init_time > datetime.utcnow():
                sleep(1)
        #First of all check if indi is running

        #~ try:    
            #Connect devices to indiserver
        self.telescope.connect()### TODO: FIFO connection!!! <---!!!
        self.camera.connect()### TODO: FIFO connection!
        self.filterw.connect()### TODO: FIFO connection!
        #~ except:
            #~ log.error(cr+"ERROR: Unable to connect one or more devices"+rc)
            #~ return 1
        #Initial delay to ensure connections are ready
        sleep(2)
        #Reading properties
        self.telescope.get_all_properties()
        self.camera.get_all_properties()
        self.filterw.get_all_properties()
        #Getting present filter
        self.filterw.getf
        #Setting camera upload mode
        self.camera.set_upload_mode("BOTH")
        #Unpark telescope
        self.telescope.park('Off') #TODO!!!


        
    def exec_lines(self):
        
        lcount = 0
        with open(self.exec_file,'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    lcount += 1
                    #~ if self.halt_flag:
                        #~ log.info("Stopped at line #{}".format(lcount))
                        #~ break
                    xline=line.strip('\n').strip()
                    xline = self._parsing_exec_line(xline)
                    log.info("Executing line #{}:  {} {}".format(
                             lcount,xline.function,xline.pti.lower()))
                    #~ #waiting for execution date/time
                    if self.wait(xline.edate+xline.etime):
                        exec "self.{}('{}')".format(xline.function.lower(),xline.pti.lower())
        
        



    def _check_indi(self):

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



    def _pstoi(self,toi,text_pattern):
        """extract name = x from toi id. = j"""
        xxx = ''
        try:
            for name in text_pattern:
                xx =re.findall(r'{0}\d+'.format(name),toi)
                xxx =xxx+''.join(xx)
            return xxx
        except:
            return xxx


    def track(self,t):

        log.debug('Executing track={}'.format(t))
        t = self._pstoi(t,'pt')
        atarget = next(trg for trg in self.targets if trg.ID==t)
        t_coord = self._coord2EOD(atarget,atarget.equinox)
        log.info("Looking for '{}' cooordinates: {}.".format(
                            atarget.obj_name, atarget.coord_value))
        self.telescope.target_coord(*t_coord)
        return

    def observe(self,i):

        log.debug('Executing observe={}'.format(i))
        t = self._pstoi(i,'pt')
        self.track(t)
        i_instr = self._pstoi(i,'pi')
        ainstr = next(ins for ins in self.instruments if self._pstoi(ins.ID,'pi')==i_instr)
        i_targ = self._pstoi(i,'pt')
        obj_name = next(trg.obj_name for trg in self.targets if self._pstoi(trg.ID,'pt')==i_targ)

        self.camera.upload_object(obj_name)
        self.camera.upload_path(self.fits_path+obj_name+"/")
        self.camera.upload_prefix("_"+obj_name+"_")
        self.filterw.setf(ainstr.ifilter)

        for x in range(int(ainstr.exposures)):
            self.camera.expose(float(ainstr.exp_time),x+1,ainstr.exposures)



    def expose(self,i):

        log.debug('Executing expose={}'.format(i))

        i_instr = self._pstoi(i,'pi')
        ainstr = next(ins for ins in self.instruments if self._pstoi(ins.ID,'pi')==i_instr)
        i_targ = self._pstoi(i,'pt')
        obj_name = next(trg.obj_name for trg in self.targets if self._pstoi(trg.ID,'pt')==i_targ)

        self.camera.upload_object(obj_name)
        self.camera.upload_path(self.fits_path+obj_name+"/")
        self.camera.upload_prefix("_"+obj_name+"_")
        self.filterw.setf(ainstr.ifilter)

        for x in range(int(ainstr.exposures)):
            self.camera.expose(float(ainstr.exp_time),x+1,ainstr.exposures)


    def _coord2EOD(self,atarget,equinox):

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


    def _parsing_exec_line(self,aline):

        log.debug('Parsing line: {}'.format(aline))

        _execline_conf = self._getlist(self.execline_conf)
        ex = namedtuple(*_execline_conf)
        aline = [_line.strip() for _line in aline.split(',') if len(_line)>0]
        aline = ex(*aline)
        log.debug('Parsed  line: {}'.format(aline))

        return aline


    def wait(self,edatetime):

        log.debug('Executing wait for {}'.format(edatetime))

        exectime = datetime.strptime(edatetime,'%Y%m%d%H:%M:%S')
        delay = int((exectime-datetime.utcnow()).total_seconds())
        #TODO: Should MIN/MAX allowed delay be configured??
        #~ if -60 <= delay <= 60:#in seconds!
        if -(int(self.allowed_delay)) <= delay <= int(self.allowed_delay):#in seconds!
            log.info('    Line in time, {}s delayed'.format(delay))
            return True
        elif int(self.max_wait) > delay > int(self.allowed_delay):#in seconds!)
            log.info(cw+'... Waiting {}s -> {}'.format(delay,exectime)+rc)
            while exectime >= datetime.utcnow():
                sleep(1)
            return True
        else:
            log.warning(cw+'    Skipping line due to a {}s delay.'.format(delay)+rc)
            return False


    def stop(self):
        
        log.info("Setting GLOBAL STATE = 'Off'")
        self.telescope.park('On') #TODO eval park state!
        sleep(1)
        self.telescope.disconnect()
        sleep(1)
        self.camera.disconnect()
        sleep(1)
        self.filterw.disconnect()
        sleep(1)
        
        
        



    def halt(self):
        return self.halt_flag == True


    def _format_date(self,date):
        """ Verify input Date format"""
        try:
            date = datetime.strptime(date, '%Y%m%d %H:%M:%S')
            return date
        except ValueError:
            log.error(cr+'ERROR: Incorrect date format, should be YYmmdd H:M:S.'+rc)
            sys.exit()



def pr(s):
    print('{}{}{}'.format(cd,s,rc))
















