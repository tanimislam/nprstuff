#!/usr/bin/env python

import os, sys, numpy, calendar, pylab
import datetime, glob
from matplotlib.patches import Rectangle

def find_occupied_days( mon, year ):
    maindir = '/mnt/media/freshair'
    days = set([ int( os.path.basename( fname ).split('.')[2] ) for fname in
                 glob.glob( os.path.join( maindir, 'NPR.FreshAir.*.%02d.%d.m4a' % ( mon, year ) ) ) ])
    return days

def create_plot_year( year ):
    calendar.setfirstweekday( 6 )
    fig = pylab.figure( figsize = ( 8 * 3, 6 * 5 ) )
    days = [ 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT' ]
    matr = numpy.array([ [-2,-1,0],
                         [1, 2, 3],
                         [4, 5, 6],
                         [7, 8, 9],
                         [10, 11, 12] ],
                       dtype=int ).flatten()
    #
    ## these are empty plots
    ax = fig.add_subplot(5,3,1)
    pylab.axis('off')
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    #
    ax = fig.add_subplot(5,3,2)
    pylab.axis('off')
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    ax.text(0.5,0.5, '\n'.join([ '%d' % year, 'FRESH AIR', 'EPISODES' ]),
            fontdict = { 'fontsize' : 64, 'fontweight' : 'bold' },
            horizontalalignment = 'center', verticalalignment = 'center' )
    #
    ax = fig.add_subplot(5,3,3)
    pylab.axis('off')
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    ax.add_patch(Rectangle((0.1, 0.1), 0.3, 0.35, linewidth = 3, facecolor = '#FF0000',
                           edgecolor = 'black' ) )
    ax.add_patch(Rectangle((0.1, 0.55), 0.3, 0.35, linewidth = 3, facecolor = '#00FF00',
                           edgecolor = 'black' ) )
    ax.text( 0.45, 0.275, 'MISSING', fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
             verticalalignment = 'center', horizontalalignment = 'left' )
    ax.text( 0.45, 0.725, 'EXISTS', fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
             verticalalignment = 'center', horizontalalignment = 'left' )
    
    for mon in xrange(1, 13):
        cal = numpy.array( calendar.monthcalendar( year, mon ),
                           dtype = int )
        nweeks = cal.shape[0]
        iidx = max( numpy.where( matr == mon )[0] ) + 1
        ax = fig.add_subplot(5, 3, mon + 3 )
        ax.set_xlim([0,1])
        ax.set_ylim([0,1])
        pylab.axis('off')
        act_days = find_occupied_days( mon, year )
        for jdx in xrange(7):
            ax.text( 0.01 + 0.14 * (jdx + 0.5), 0.93, days[jdx],
                     fontdict = { 'fontsize' : 14, 'fontweight' : 'bold' },
                     horizontalalignment = 'center',
                     verticalalignment = 'center' )
        for idx in xrange(nweeks):
            for jdx in xrange(7):
                if cal[idx, jdx] == 0:
                    continue
                if jdx == 0 or jdx == 6:
                    color = '#E8E8E8'
                else:
                    if cal[idx, jdx] in act_days:
                        color = '#00FF00'
                    else:
                        color = '#FF0000'
                ax.add_patch( Rectangle( ( 0.01 + 0.14 * jdx,
                                           0.99 - 0.14 - 0.14 * (idx + 1) ),
                                         0.14, 0.14, linewidth = 2,
                                         facecolor = color, edgecolor = 'black' ) )
                ax.text( 0.01 + 0.14 * ( jdx + 0.5 ),
                         0.99 - 0.14 - 0.14 * ( idx + 0.5 ), '%d' % cal[idx, jdx],
                         fontdict = { 'fontsize' : 14, 'fontweight' : 'bold' },
                         horizontalalignment = 'center',
                         verticalalignment = 'center' )
        monname = datetime.datetime.strptime('%02d.%d' % ( mon, year ),
                                             '%m.%Y' ).strftime('%B').upper( )
        ax.set_title( monname, fontsize = 14, fontweight = 'bold' )
    fig.savefig( 'freshair.%d.svg' % year, bbox_inches = 'tight' )
    pylab.close( )
                                         
def create_plot_month( mon, year ):
    calendar.setfirstweekday( 6 )
    cal = numpy.array( calendar.monthcalendar( year, mon ),
                       dtype = int )
    nweeks = cal.shape[0]
    fig = pylab.figure( figsize = (8, 6) )
    ax = fig.add_subplot(111)
    pylab.axis('off')
    act_days = find_occupied_days( mon, year )
    days = [ 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT' ]
    for jdx in xrange(7):
        ax.text( 0.01 + 0.14 * (jdx + 0.5), 0.90, days[jdx],
                 fontdict = { 'fontsize' : 14, 'fontweight' : 'bold' },
                 horizontalalignment = 'center',
                 verticalalignment = 'center' )
    for idx in xrange(nweeks):
        for jdx in xrange(7):
            if cal[idx, jdx] == 0:
                continue
            if jdx == 0 or jdx == 6:
                color = '#E8E8E8'
            else:
                if cal[idx, jdx] in act_days:
                    color = '#00FF00'
                else:
                    color = '#FF0000'
            ax.add_patch(Rectangle( ( 0.01 + 0.14 * jdx,
                                      0.98 - 0.16 - 0.16 * (idx + 1) ),
                                    0.14, 0.16, linewidth = 2,
                                    facecolor = color, edgecolor = 'black' ) )
            ax.text( 0.01 + 0.14 * ( jdx + 0.5 ),
                     0.98 - 0.16 - 0.16 * (idx + 0.5 ),
                     '%d' % cal[idx, jdx],
                     fontdict = { 'fontsize' : 14, 'fontweight' : 'bold' },
                     horizontalalignment = 'center',
                     verticalalignment = 'center' )
    monname = datetime.datetime.strptime('%02d.%d' % ( mon, year ),
                                         '%m.%Y').strftime('%B').upper( )
    ax.set_title( monname, fontsize = 14, fontweight = 'bold')
    fig.savefig( '%02d.%d.svg' % ( mon, year ),
                 bbox_inches = 'tight' )
    pylab.close( )
                                    
