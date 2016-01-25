#!/usr/bin/env python

import freshair, os, glob, sys, npr_utils
import calendar, pylab, numpy, datetime
from matplotlib.patches import Rectangle
from mutagen.easymp4 import EasyMP4
from PyQt4.QtGui import QColor
from optparse import OptionParser

_default_inputdir = '/mnt/media/freshair'
_default_year = 2010

def suncal( mon, year = _default_year ):
    cal0 = numpy.array( calendar.monthcalendar( year, mon ), dtype=int )
    cal = numpy.zeros( cal0.shape, dtype=int )
    cal[:,[1,2,3,4,5,6]] = cal0[:,[0,1,2,3,4,5]]
    cal[1:,0] = cal0[:,-1][:-1]
    if max( cal[0,:] ) == 0:
        cal = cal[1:,:]
    if max( cal[-1,:] ) == 0:
        cal = cal[:-1,:]
    return cal

def get_color( discrep ):
    assert( discrep <= 1.0 )
    assert( discrep >= 0.0 )
    s_color = QColor("#00FF00")
    e_color = QColor("orange")
    hsv_start = numpy.array( s_color.getHsvF()[:-1] )
    hsv_end = numpy.array( e_color.getHsvF()[:-1] )
    hsv_mid = hsv_start * (1.0 - discrep) + hsv_end * discrep
    cmid = QColor.fromHsvF( hsv_mid[0], hsv_mid[1], hsv_mid[2], 1.0 )
    return str( cmid.name( ) ).upper( )

def find_occupied_days( mon, year = _default_year ):
    days = set([ int( os.path.basename( fname ).split('.')[2] ) for fname in
                 glob.glob( os.path.join( _default_inputdir,
                                          'NPR.FreshAir.*.%02d.%d.m4a' % ( mon, year ) ) ) ])
    return days

def find_underoccupied_dates( mon, year = _default_year ):
    newdict = {}
    days = find_occupied_days( mon, year = year )
    daydict = { day : os.path.join( _default_inputdir, 'NPR.FreshAir.%02d.%02d.%d.m4a' % ( day, mon, year ) ) for day in days }
    actdict = { day : EasyMP4( daydict[day] ).info.length for day in
                filter(lambda day: os.stat(daydict[day]).st_size <= 4e7, daydict) }
    # now get tree for each of these files
    for day in actdict:
        dt_s = datetime.datetime.strptime('%02d.%02d.%04d' % ( day, mon, year ),
                                          '%d.%m.%Y' ).date( )
        tree = freshair.get_freshair( os.path.expanduser('~'), dt_s, debug = True, to_file_debug = False )
        expectdur = 0
        for elem in tree.iter('story'):
            durs = list( elem.iter('duration'))
            if len(durs) == 0:
                continue
            expectdur += int( max(elem.iter('duration')).text )
        totlength = actdict[ day ]
        if expectdur == 0:
            newdict[day] = ( totlength, 1.0, get_color( 1.0 ) )
            continue
        discrep = max(0.0, expectdur * 0.985 - totlength ) / ( 0.985 * expectdur )
        if discrep <= 1e-6:
            continue
        newdict[day] = ( totlength, discrep, get_color( discrep ) )
    return newdict

def create_plot_year( year = _default_year ):
    # calendar.setfirstweekday( 6 )
    fig = pylab.figure( figsize = ( 8 * 3, 6 * 5 ) )
    days = [ 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT' ]
    matr = numpy.array([ [-2,-1,0],
                         [1, 2, 3],
                         [4, 5, 6],
                         [7, 8, 9],
                         [10, 11, 12] ],
                       dtype=int ).flatten()
    data = {}
    nwkdays = 0
    nunder = 0
    nmiss = 0
    for mon in xrange(1, 13):
        cal = suncal( mon, year )
        act_days = find_occupied_days( mon, year )
        newdict = find_underoccupied_dates( mon, year )
        data[mon] = (cal, act_days, newdict)
        wkdays = set( cal[:,1:-1].flatten() ) - set([ 0, ])
        nwkdays += len( wkdays )
        nmiss += len( wkdays - act_days )
        nunder += len( newdict )
        
    #
    ## these are the legend plots
    ax = fig.add_subplot(5,3,3)
    pylab.axis('off')
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    ax.text(0.15, 0.8, '\n'.join([ '%d / %d' % (nmiss, nwkdays),
                                   '%0.2f%% missing' % ( 100.0 * nmiss / nwkdays ) ]),
            fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
            horizontalalignment = 'left', verticalalignment = 'center',
            color = 'red' )
    ax.text(0.15, 0.5, '\n'.join([ '%d / %d' % (nunder, nwkdays),
                                   '%0.2f%% underocc' % ( 100.0 * nunder / nwkdays ) ]),
            fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
            horizontalalignment = 'left', verticalalignment = 'center',
            color = 'orange' )
    ax.text(0.15, 0.2, '%0.2f%% coverage' % ( 100.0 - 100.0 * nmiss / nwkdays ),
            fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
            horizontalalignment = 'left', verticalalignment = 'center' )
    #
    ax = fig.add_subplot(5,3,2)
    pylab.axis('off')
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    ax.text(0.5,0.5, '\n'.join([ '%d' % year, 'FRESH AIR', 'EPISODES' ]),
            fontdict = { 'fontsize' : 64, 'fontweight' : 'bold' },
            horizontalalignment = 'center', verticalalignment = 'center' )
    #
    ax = fig.add_subplot(5,3,1)
    pylab.axis('off')
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    ax.add_patch(Rectangle((0.1, 0.1), 0.2, 0.25, linewidth = 3, facecolor = '#FF0000',
                           edgecolor = 'black' ) )
    for idx in xrange(100):
        ax.add_patch(Rectangle((0.1 + 0.002 * idx, 0.4), 0.002, 0.25, linewidth = 0,
                               facecolor = get_color( 0.005 + 0.01 * idx ), edgecolor = 'none' ) )
    ax.add_patch(Rectangle((0.1, 0.4), 0.2, 0.25, linewidth = 3, facecolor = 'none',
                           edgecolor = 'black' ) )
    ax.add_patch(Rectangle((0.1, 0.7), 0.2, 0.25, linewidth = 3, facecolor = '#00FF00',
                           edgecolor = 'black' ) )
    ax.text( 0.35, 0.2, 'MISSING', fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
             verticalalignment = 'center', horizontalalignment = 'left' )
    ax.text( 0.35, 0.5, 'UNDEROCCUPIED', fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
             verticalalignment = 'center', horizontalalignment = 'left' )
    ax.text( 0.35, 0.8, 'EXISTS', fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
             verticalalignment = 'center', horizontalalignment = 'left' )
    
    for mon in xrange(1, 13):
        cal, act_days, newdict = data[ mon ]
        nweeks = cal.shape[0]
        ax = fig.add_subplot(5, 3, mon + 3 )
        ax.set_xlim([0,1])
        ax.set_ylim([0,1])
        pylab.axis('off')
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
                        if cal[idx, jdx] not in newdict:
                            color = '#00FF00'
                        else:
                            dur, discrep, color = newdict[ cal[idx, jdx] ]
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
    fig.savefig( 'freshair.%d.svgz' % year, bbox_inches = 'tight' )
    pylab.close( )

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--year', dest='year', action='store', type=int, default = _default_year,
                      help = 'Year in which to write out all Fresh Air episodes. Default is %d.' %
                      _default_year )
    parser.add_option('--inputdir', dest = 'inputdir', action='store', type = str,
                      default = _default_inputdir, help = 'Directory into which ' +
                      'to store the NPR Fresh Air episodes. Default is %s.' %
                      _default_inputdir)
    parser.add_option('--quiet', dest='is_quiet', action='store_true', default = False,
                      help = ' '.join([ 'If chosen, do not print verbose output from the action of this',
                                        'script. By default this is false.' ]) )
    parser.add_option('--coverage', dest = 'get_coverage', action = 'store_true', default = False,
                      help = 'If chosen, just give the list of missing Fresh Air episodes and nothing else.')
    parser.add_option('--audit', dest = 'do_audit', action = 'store_true', default = False,
                      help = 'If chosen, do the audit picture here.')
    opts, args = parser.parse_args()
    if not opts.do_audit:
        verbose = not opts.is_quiet
        freshair.process_all_freshairs_by_year( opts.year,
                                                opts.inputdir,
                                                verbose = verbose,
                                                justCoverage = opts.get_coverage )
    else:
        create_plot_year( opts.year )
