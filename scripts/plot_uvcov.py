#!/usr/bin/env python
import argparse
import glob
import signal
import os
import sys
import matplotlib as mpl
mpl.use('Agg')
import matplotlib
import matplotlib.pyplot as plt
import numpy
import casacore.tables as pt


def input2strlist_nomapfile(invar):
   """
   from bin/download_IONEX.py
   give the list of MSs from the list provided as a string
   """
   str_list = None
   if type(invar) is str:
       if invar.startswith('[') and invar.endswith(']'):
           str_list = [f.strip(' \'\"') for f in invar.strip('[]').split(',')]
       else:
           str_list = [invar.strip(' \'\"')]
   elif type(invar) is list:
       str_list = [str(f).strip(' \'\"') for f in invar]
   else:
       raise TypeError('input2strlist: Type '+str(type(invar))+' unknown!')
   return str_list


def string2bool(instring):
    if isinstance(instring, bool):
        return instring
    if instring.upper() == 'TRUE' or instring == '1':
        return True
    elif instring.upper() == 'FALSE' or instring == '0':
        return False
    else:
        raise ValueError('string2bool: Cannot convert string "'+instring+'" to boolean!')


def main(input, output, title='uv coverage', limits=',,,', timeslots='0,0,0', antennas='-1', kilolambda=True,
         markersize=2, wideband=True, sameuv=True, debug=False, flagged=True):

        debug = string2bool(debug)
        MSlist = input2strlist_nomapfile(input)
        if len(MSlist) == 0:
                print 'Error: You must specify at least one MS name.'
                sys.exit(1)
        plottitle = title
        fileformat = output.split('.')[-1]
        if fileformat not in ['png','pdf','eps','ps']:
                print 'Error: Unknown file extension'
                sys.exit(1)
        axlimits = limits.strip().split(',')
        if len(axlimits) == 4:
                xmin,xmax,ymin,ymax = axlimits
        else:
                print 'Error: You must specify four axis limits'
                sys.exit(1)
        timeslots = timeslots.split(',')
        if len(timeslots) != 3:
                print 'Error: Timeslots format is start,skip,end'
                sys.exit(1)
        for i in range(len(timeslots)):
                timeslots[i] = int(timeslots[i])
                if timeslots[i] < 0:
                        print 'Error: timeslots values must not be negative'
                        sys.exit(1)
        antToPlotSpl = antennas.split(',')
        antToPlot = []
        for i in range(len(antToPlotSpl)):
                tmpspl = antToPlotSpl[i].split('..')
                if len(tmpspl) == 1:
                        antToPlot.append(int(antToPlotSpl[i]))
                elif len(tmpspl) == 2:
                        for j in range(int(tmpspl[0]),int(tmpspl[1])+1):
                                antToPlot.append(j)
                else:
                        print 'Error: Could not understand antenna list.'
                        sys.exit(1)
        plotLambda = string2bool(kilolambda)
        markerSize = int(markersize)
        wideband = string2bool(wideband)
        sameuv = string2bool(sameuv)
        flagged = string2bool(flagged)

        badval = 0.0
        xaxisvals = numpy.array([])
        yaxisvals = numpy.array([])
        flagvals = numpy.array([], dtype=bool)
        savex = numpy.array([])
        savey = numpy.array([])
        numPlotted = 0
        for inputMS in MSlist:
                # open the main table and print some info about the MS
                print 'Getting info for', inputMS
                t = pt.table(inputMS, readonly=True, ack=False)
                tfreq = pt.table(t.getkeyword('SPECTRAL_WINDOW'),readonly=True,ack=False)
                ref_freq = tfreq.getcol('REF_FREQUENCY',nrow=1)[0]
                ch_freq = tfreq.getcol('CHAN_FREQ',nrow=1)[0]
                print 'Reference frequency:\t%f MHz' % (ref_freq/1.e6)
                if wideband:
                        ref_wavelength = 2.99792458e8/ch_freq
                else:
                        ref_wavelength = [2.99792458e8/ref_freq]
                print 'Reference wavelength:\t%f m' % (ref_wavelength[0])
                if sameuv and numPlotted > 0:
                        print 'Assuming same uvw as first MS!'
                        if plotLambda:
                                for w in ref_wavelength:
                                        xaxisvals = numpy.append(xaxisvals,[savex/w/1000.,-savex/w/1000.])
                                        yaxisvals = numpy.append(yaxisvals,[savey/w/1000.,-savey/w/1000.])
                        else:
                                print 'Plotting more than one MS with same uv, all in kilometers... do you want -k?'
                                xaxisvals = numpy.append(xaxisvals,[savex,-savex])
                                yaxisvals = numpy.append(yaxisvals,[savey,-savey])
                        if not flagged:
                            continue

                firstTime = t.getcell("TIME", 0)
                lastTime = t.getcell("TIME", t.nrows()-1)
                intTime = t.getcell("INTERVAL", 0)
                print 'Integration time:\t%f sec' % (intTime)
                nTimeslots = (lastTime - firstTime) / intTime
                print 'Number of timeslots:\t%d' % (nTimeslots)
                if timeslots[1] == 0:
                        if nTimeslots >= 100:
                                timeskip = int(nTimeslots/100)
                        else:
                                timeskip = 1
                else:
                        timeskip = int(timeslots[1])
                print 'For each baseline, plotting one point every %d samples' % (timeskip)
                if timeslots[2] == 0:
                        timeslots[2] = nTimeslots
                # open the antenna subtable
                tant = pt.table(t.getkeyword('ANTENNA'), readonly=True, ack=False)

                # Station names
                antList = tant.getcol('NAME')
                if len(antToPlot)==1 and antToPlot[0]==-1:
                        antToPlot = range(len(antList))

                # select by time from the beginning, and only use specified antennas
                tsel = t.query('TIME >= %f AND TIME <= %f AND ANTENNA1 IN %s AND ANTENNA2 IN %s' % (firstTime+timeslots[0]*intTime,firstTime+timeslots[2]*intTime,str(antToPlot),str(antToPlot)), columns='ANTENNA1,ANTENNA2,UVW,FLAG_ROW')

                # Now we loop through the baselines
                i = 0
                nb = (len(antToPlot)*(len(antToPlot)-1))/2
                for tpart in tsel.iter(["ANTENNA1","ANTENNA2"]):
                        ant1 = tpart.getcell("ANTENNA1", 0)
                        ant2 = tpart.getcell("ANTENNA2", 0)
                        if ant1 not in antToPlot or ant2 not in antToPlot: continue
                        if ant1 == ant2: continue
                        i += 1
                        # Get the values to plot
                        if not sameuv or numPlotted == 0:
                                uvw = tpart.getcol('UVW', rowincr=timeskip)
                                savex = numpy.append(savex,[uvw[:,0],-uvw[:,0]])
                                savey = numpy.append(savey,[uvw[:,1],-uvw[:,1]])
                        if flagged:
                            # Get the flags
                            flags = tpart.getcol('FLAG_ROW', rowincr=timeskip)
                        if plotLambda:
                                for w in ref_wavelength:
                                        if not sameuv:
                                            xaxisvals = numpy.append(xaxisvals,[uvw[:,0]/w/1000.,-uvw[:,0]/w/1000.])
                                            yaxisvals = numpy.append(yaxisvals,[uvw[:,1]/w/1000.,-uvw[:,1]/w/1000.])
                                        if flagged:
                                            flagvals = numpy.append(flagvals,[flags[:], flags[:]])
                        else:
                                if not sameuv:
                                    xaxisvals = numpy.append(xaxisvals,[uvw[:,0]/1000.,-uvw[:,0]/1000.])
                                    yaxisvals = numpy.append(yaxisvals,[uvw[:,1]/1000.,-uvw[:,1]/1000.])
                                if flagged:
                                    flagvals = numpy.append(flagvals,[flags[:], flags[:]])
                numPlotted += 1

        print 'Plotting uv points ...'

        # Plot the data
        if debug:
                print xaxisvals
        xaxisvals = numpy.array(xaxisvals)
        yaxisvals = numpy.array(yaxisvals)
        tmpvals = numpy.sqrt(xaxisvals**2+yaxisvals**2)
        uvmax = max(xaxisvals.max(),yaxisvals.max())
        uvmin = min(xaxisvals.min(),yaxisvals.min())
        uvuplim = 0.02*(uvmax-uvmin)+uvmax
        uvlolim = uvmin-0.02*(uvmax-uvmin)
        if xmin == '':
                minx = uvlolim
        else:
                minx = float(xmin)
        if xmax == '':
                maxx = uvuplim
        else:
                maxx = float(xmax)
        if ymin == '':
                miny = uvlolim
        else:
                miny = float(ymin)
        if ymax == '':
                maxy = uvuplim
        else:
                maxy = float(ymax)
        if minx == maxx:
                minx = -1.0
                maxx = 1.0
        if miny == maxy:
                miny = -1.0
                maxy = 1.0
        if plotLambda:
                plt.xlabel(r'u [k$\lambda$]')
                plt.ylabel(r'v [k$\lambda$]')
                plt.xlim([minx,maxx])
                plt.ylim([miny,maxy])
        else:
                plt.xlabel('u [km]')
                plt.ylabel('v [km]')
                plt.xlim([minx,maxx])
                plt.ylim([miny,maxy])
        plt.plot(xaxisvals[tmpvals!=badval], yaxisvals[tmpvals!=badval],'.',
                 markersize=markerSize)
        if flagged:
            flagged_ind = numpy.where(numpy.logical_and(tmpvals!=badval, flagvals))
            plt.plot(xaxisvals[flagged_ind], yaxisvals[flagged_ind],'.',
                     markersize=markerSize, c='r')
        plt.title(plottitle)
        plt.axes().set_aspect('equal')
        plt.grid(True)

        plt.savefig(output)

