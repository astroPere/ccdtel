#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function


from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy import units as u

from astropy.wcs import WCS
import os
import time
import sys
import glob
import re
import subprocess
import tempfile
import shutil
import logging


rc = '\033[0m' #reset color
cr = '\033[91m'#red
cg ='\033[32m' #green
cw = '\033[33m'#yellow
cb = '\033[94m'#blue
cy = '\033[36m'#cyan

log = logging.getLogger(__name__)



class WcsSolver(object):

    def __init__(self, **data):
        for key in data:
            setattr(self, key, data[key])


    def parseDMS(self,strin):
        """Parse string in degrees notation to float"""
        mul=1.
        fraction=1.
        subres=0.
        ret=0.
        neg = False
        strin = strin.replace(" ",":")
        for x in strin:
            if x == ':':
                ret+=subres/mul
                subres=0
                fraction=1.
                mul *= 60.0
            elif x >= '0' and x <= '9':
                if fraction >= 1:
                    subres = fraction*subres + int(x)
                    fraction*=10
                else:
                    subres = subres + int(x)*fraction
                    fraction/=10
            elif x == '+' and mul == 1 and fraction == 1:
                neg = False
            elif x == '-' and mul == 1 and fraction == 1:
                neg = True
            elif x == '.':
                ret+=subres/mul
                fraction=0.1
                subres=0
            elif x == ' ':
                pass
            else:
                raise Exception('Cannot parse {0} - problem with {1}'.format(strin,x))  
        ret+=subres/mul
        if neg:
            ret*=-1
        return ret


    def solve(self,image):

        t1 = time.time()
        #~ dirc = glob.glob(str(self.ipath))
        dirc = glob.glob(str(image))
        solved_pos = None
        errA,errD = [],[]
        RA,DEC = '',''
        proc = ''
        not_solved = []
        solved = []
        for image in sorted(dirc):
            print ('-'*40)
            img_hdulist = fits.open(image)
            img_hdr = img_hdulist[0].header
            RA = img_hdr[str(self.ra_header)]
            DEC = img_hdr[str(self.dec_header)]
            fits_pos = SkyCoord(RA,DEC,unit=(u.hourangle, u.deg))
            #~ ra=self.parseDMS(RA)*15
            #~ dec=self.parseDMS(DEC)
            ra=fits_pos.ra.hour
            dec=fits_pos.dec.degree

            InFileImg = str(image)
            ImgName = str(os.path.basename(image))
            OutDir2 = str(self.ipath)
            OutDir = tempfile.mkdtemp()
            Radius = str(self.search_rad)
            Sampl = str(self.sampling)
            PixResHi = str(float(self.pix_res)+0.5)
            PixResLo = str(float(self.pix_res)-0.5)
            Sigma = str(self.sigma)
            WcsImg =  OutDir2+'/'+str(self.prefix)+ImgName
            OutImg = OutDir + '/input.fits'
            Indexes = '10,20,40,60,100,120,140'
            shutil.copy(image, OutImg)
            proces=['solve-field','--batch','--no-fits2fits','-O','-u','app','-p','-r','--objs','50',
                '-N',WcsImg,'-U','none','-M','none','-R','none','-B','none',
                '-D',OutDir,
                '--ra',str(ra),
                '--dec',str(dec),
                '--radius',str(Radius),
                '-z', Sampl,
                '-d',Indexes,
                '-L',PixResLo,
                '-H',PixResHi,
                '--sigma',Sigma]

            #~ self.textBrowser.setText(' '.join(proces))

            proces.append(OutImg)
            print(cw+proc)
            proc=subprocess.Popen(proces,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

            radecline1=re.compile('Field center: \(RA H:M:S, Dec D:M:S\) = \(([^,]*),(.*)\).')
            #~ radecline2=re.compile('Field size: \(RA H:M:S, Dec D:M:S\) = \(([^,]*),(.*)\).')
            print('Solving WCS...')
            while True:
                a=proc.stdout.readline()
                print(cw+a.strip('\n')+rc)
                if a == '':
                    break
                #~ print a.strip('\n')
                match1=radecline1.match(a)
                if match1:
                    solved_pos = SkyCoord(match1.group(1),match1.group(2),unit=(u.hourangle, u.deg))
                    fits_pos = SkyCoord(RA,DEC,unit=(u.hourangle, u.deg))
                    print(ImgName)
                    print('Fits           >  ra: {}  dec: {}'.format(
                            (fits_pos.ra).to_string(u.hour),str(fits_pos.dec)))
                    print('Solved         >  ra: {}  dec: {}'.format(
                            (solved_pos.ra).to_string(u.hour),str(solved_pos.dec)))
                    print('Pointing error >  ra: {:2.3f} arcmin   dec:{:2.3f} arcmin'.format(
                            (fits_pos.ra - solved_pos.ra).arcminute,(fits_pos.dec - solved_pos.dec).arcminute))
                    print('Ang.Dist.      >      {:2.3f} arcmin'.format(
                            solved_pos.separation(fits_pos).arcminute))

                    errA.append((fits_pos.ra - solved_pos.ra).arcminute)
                    errD.append((fits_pos.dec - solved_pos.dec).arcminute)
                    solved.append(ImgName)
                if 'Did not solve (or no WCS file was written).' in a:
                    print ('{} not solved!'.format(ImgName))
                    not_solved.append(ImgName)
                    
            shutil.rmtree(OutDir)
            
        return solved_pos.ra,solved_pos.dec
        #~ print '----------------------------------------------------------------------------'
        #~ print '>','%2.2f' % (time.time() - t1)



    ### TODO: Add plotting option
    ### TODO: Ensure destination path exixts!
