#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
Command INDI ccd with indi_setprop & indi_getprop

"""
#~ import hashlib
from datetime import datetime

import logging
from time import sleep

import ConfigParser

from session import Session 


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



#~ def hashfile(path, blocksize = 65536):
    #~ afile = open(path, 'rb')
    #~ hasher = hashlib.md5()
    #~ buf = afile.read(blocksize)
    #~ while len(buf) > 0:
        #~ hasher.update(buf)
        #~ buf = afile.read(blocksize)
    #~ afile.close()
    #~ return hasher.hexdigest()




#~ def md5Checksum(filePath):
    #~ with open(filePath, 'rb') as fh:
        #~ m = hashlib.md5()
        #~ while True:
            #~ data = fh.read(8192)
            #~ if not data:
                #~ break
            #~ m.update(data)
        #~ return m.hexdigest()




def pr(s):
    print('{}{}{}'.format(cd,s,rc))



def main(args):

    try:
        session = Session("lx200gps.cfg")
        #~ session = Session("simulator_config.cfg")

        #~ session.init("20170912 13:14:50")
        session.init()
        
        #~ session.exec_lines()
        #~ pr("...sleeping 3...")
        #~ sleep(3)
        img = session.exec_lines()
        #~ session.telescope.target_coord(0.5,0.5)
        image = session.camera.expose()
        #~ image = '/home/a02/fits/rawdata/M57/_M57__006.fits'
        img_coord = session.wcs.solve(image)
        session.telescope.sync_coord(img_coord)
        #~ session.phd2.equipment("On")
        #~ session.phd2.pause("Off",full=True)
        #~ sleep(2)
        #~ session.phd2.single_capture()
        #~ sleep(5)
        #~ session.phd2.select_star()
        #~ sleep(5)
        #~ session.phd2.app_state()
        #~ sleep(1)
        #~ session.phd2.loop()
        #~ session.focuser_get_pos()
        #~ session.focuser_move_to(22000)
        #~ session.focuser_get_pos()
        #~ session.focuser_set_move("OUT")

        #~ session.focuser_in(500)

        #~ session.focuser_get_pos()

        #~ session.focuser_out(1500)

        #~ session.focuser_get_pos()

        #~ session.focuser_move_to(18000)
        sleep(5)
        session.stop()


    except(KeyboardInterrupt,SystemExit):
        log.warning(cw+"TELESCOPE HALTED!"+rc)
        session.telescope.halt
        session.stop()
        #~ session.telescope.disconnect()
        #~ session.camera.disconnect()
        #~ session.filterw.disconnect()
        #~ raise



    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
