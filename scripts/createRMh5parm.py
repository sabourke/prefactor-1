#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extract RM values for a LOFAR observation. Fill h5parm

Created on Tue Aug 7 11:46:57 2018

@author: mevius
"""
from losoto.h5parm import h5parm
from RMextract import getRM
from RMextract import PosTools
import RMextract.getIONEX as ionex
import pyrap.tables as pt
import os
import numpy as np
import sys
import logging


def makesolset(MS, data, solset_name):
    solset = data.makeSolset(solset_name)    

    antennaFile = MS+"/ANTENNA"
    logging.info('Collecting information from the ANTENNA table.')
    antennaTable = pt.table(antennaFile, ack=False)
    antennaNames = antennaTable.getcol('NAME')
    antennaPositions = antennaTable.getcol('POSITION')
    antennaTable.close()
    antennaTable = solset.obj._f_get_child('antenna')
    antennaTable.append(zip(*(antennaNames,antennaPositions)))
    
    fieldFile = MS + "/FIELD"
    logging.info('Collecting information from the FIELD table.')
    fieldTable = pt.table(fieldFile, ack=False)
    phaseDir = fieldTable.getcol('PHASE_DIR')
    pointing = phaseDir[0, 0, :]
    fieldTable.close()

    sourceTable = solset.obj._f_get_child('source')
    # add the field centre, that is also the direction for Gain and Common*
    sourceTable.append([('pointing',pointing)])




def main(MSfiles, h5parmdb, solset_name = "sol000",timestepRM=300,
                ionex_server="ftp://ftp.aiub.unibe.ch/CODE/",
                ionex_prefix='CODG',ionexPath="./",earth_rot=0,proxyServer=None,proxyPort=None,proxyType=None,proxyUser=None,proxyPass=None):
    '''Add rotation measure to existing h5parmdb
    
    Args:
        MSfiles (string) :  path + filename of Measurement Set 
        h5parmdb (string) : name of existing h5parm
        solset_name (string) : optional name of solset in h5parmdb, 
                            if not set, first one will be chosen
        timestep (float) : timestep in seconds
        ionex_server (string) : ftp server for IONEX files
        ionex_prefix (string) : prefix of IONEX files
        ionexPath (string) : location where IONEX files are stored
        earth_rot (float) : parameter to determine how much earth rotation is taken \
        into account when interpolating IONEX data. (0 is none, 1 is full)
    '''
    
    mslist = MSfiles.lstrip('[').rstrip(']').replace(' ','').replace("'","").split(',')
    
    if len(mslist) == 0:
        raise ValueError("Did not find any existing directory in input MS list!")
        pass
    else:
        MS = mslist[0]
        pass
        
    #extract the timerange information
    (timerange,timestep,pointing,stat_names,stat_pos) = PosTools.getMSinfo(MS)
    start_time = timerange[0]
    end_time = timerange[1]
    timerange[0] = start_time - timestep
    timerange[1] = end_time + timestep
    times,timerange = PosTools.getIONEXtimerange(timerange, timestep)
    if len(times[-1]) == 0 or times[-1][-1] < timerange[1]:
        timestmp = list(times[-1])
        timestmp.append(timerange[1]) #add one extra step to make sure you have a value for all times in the MS in case timestep hase been changed
        times[-1] = np.array(timestmp)

    for time_array in times[::-1]:    #check in reverse order, since datamight not be available for latest days
        starttime = time_array[0]
        date_parms = PosTools.obtain_observation_year_month_day_fraction(starttime)
        if not proxyServer:
            if not "http" in ionex_server:      #ftp server use ftplib
                ionexf = ionex.getIONEXfile(time=date_parms,
                                              server  = ionex_server,
                                              prefix  = ionex_prefix,
                                              outpath = ionexPath)
            else:
                ionexf = ionex.get_urllib_IONEXfile(time  = date_parms,
                                              server  = ionex_server,
                                              prefix  = ionex_prefix,
                                              outpath = ionexPath)
            
        else:
            ionexf = ionex.get_urllib_IONEXfile(time  = date_parms,
                                              server  = ionex_server,
                                              prefix  = ionex_prefix,
                                              outpath = ionexPath,
                                              proxy_server = proxyServer,
                                              proxy_type   = proxyType,
                                              proxy_port   = proxyPort,
                                              proxy_user   = proxyUser,
                                              proxy_pass   = proxyPass)

        if ionexf == -1:
            if not "igsiono.uwm.edu.pl" in ionex_server:
                logging.info("cannot get IONEX data, try fast product server instead")
                if not proxyServer:
                    ionexf = ionex.get_urllib_IONEXfile(time = date_parms,
                                                     server  = "https://igsiono.uwm.edu.pl",
                                                     prefix  = "igrg",
                                                     outpath = ionexPath)
                else:
                    ionexf = ionex.get_urllib_IONEXfile(time = date_parms,
                                                     server  = "https://igsiono.uwm.edu.pl",
                                                     prefix  = "igrg",
                                                     outpath = ionexPath,
                                                  proxy_server = proxyServer,
                                                  proxy_type   = proxyType,
                                                  proxy_port   = proxyPort,
                                                  proxy_user   = proxyUser,
                                                  proxy_pass   = proxyPass)
        if ionexf == -1:
            logging.error("IONEX data not available, even not from fast product server")
            return -1
    
    
    if not proxyServer:
	    rmdict = getRM.getRM(MS,
                         server    = ionex_server, 
                         prefix    = ionex_prefix, 
                         ionexPath = ionexPath, 
                         timestep  = timestepRM,
                         earth_rot = earth_rot)
    else:
	    rmdict = getRM.getRM(MS,
                         server    = ionex_server, 
                         prefix    = ionex_prefix, 
                         ionexPath = ionexPath, 
                         timestep  = timestepRM,
                         earth_rot = earth_rot,
                         proxy_server = proxyServer,
                         proxy_type   = proxyType,
                         proxy_port   = proxyPort,
                         proxy_user   = proxyUser,
                         proxy_pass   = proxyPass)

    
    if not rmdict:
        if not ionex_server:
            raise ValueError("One or more IONEX files is not found on disk and download is disabled!\n"
                                 "(You can run \"bin/download_IONEX.py\" outside the pipeline if needed.)")
        else:
            raise ValueError("Couldn't get RM information from RMextract! (But I don't know why.)")
 
    data          = h5parm(h5parmdb, readonly=False)
    if not solset_name in data.getSolsetNames():
        makesolset(MS,data,solset_name)
    solset        = data.getSolset(solset_name)
    station_names = sorted(solset.getAnt().keys())

 
    logging.info('Adding rotation measure values to: ' + solset_name + ' of ' + h5parmdb)
    rm_vals=np.array([rmdict["RM"][stat].flatten() for stat in station_names])
    new_soltab = solset.makeSoltab(soltype='rotationmeasure', soltabName='RMextract',
                                   axesNames=['ant', 'time'], axesVals=[station_names, rmdict['times']],
                                   vals=rm_vals,
                                   weights=np.ones_like(rm_vals, dtype=np.float16))


    
    ########################################################################
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Adds CommonRotationAngle to an H5parm from RMextract.')

    parser.add_argument('MSfiles', type=str,
                        help='MS for which the parmdb should be created.')
    parser.add_argument('h5parm', type=str,
                        help='H5parm to which the results of the CommonRotationAngle is added.')
    parser.add_argument('--server', type=str, default='ftp://ftp.aiub.unibe.ch/CODE/',
                        help='URL of the server to use. (default: ftp://ftp.aiub.unibe.ch/CODE/)')
    parser.add_argument('--prefix', type=str, default='CODG',
                        help='Prefix of the IONEX files. (default: \"CODG\")')
    parser.add_argument('--ionexpath', '--path', type=str, default='./',
                        help='Directory where to store the IONEX files. (default: \"./\")')
    parser.add_argument('--solsetName', '--solset', type=str, default='sol000',
                        help='Name of the h5parm solution set (default: sol000)')
    parser.add_argument('-t','--timestep', help=
                        'timestep in seconds. for values <=0 (default) the timegrid of the MS is used ',
                        dest="timestep",type=float,default=300.)
    parser.add_argument('-e','--smart_interpol', help=
                        'float parameter describing how much of Earth rotation is taken in to account \
                        in interpolation of the IONEX files. 1.0 means time interpolation assumes \
                        ionosphere rotates in opposite direction of the Earth. 0.0 (default) means \
                        no rotation applied',dest="earth_rot",type=float,default=0)

    args = parser.parse_args()

    MS = args.MSfiles
    h5parmdb = args.h5parm
    logging.info("Working on: %s %s" % (MS, h5parmdb))
    main(MS, h5parmdb, ionex_server=args.server, ionex_prefix=args.prefix, 
                 ionexPath=args.ionexpath, solset_name=args.solsetName, 
                 timestep=args.timestep, earth_rot=args.earth_rot)
    
