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

import camera as ccd
import telescope as tel


log = logging.getLogger(__name__)


class SequenceLine(object):
    
    #~ def __init__(self):
        
    
    def parse_line(self,afile):
        
        for line in afile:
            print(line)
        
        
    
        
