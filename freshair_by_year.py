#!/usr/bin/env python

import freshair, os, glob, sys
import calendar, pylab, numpy, datetime
from matplotlib.patches import Rectangle
from optparse import OptionParser

_default_inputdir = '/mnt/media/freshair'
_default_year = 2010

def find_occupied_days( mon, year = _default_year ):
    days = set([ int( os.path.basename( fname ).split('.')[2] ) for fname in
                 glob.glob( os.path.join( _default_inputdir,
                                          'NPR.FreshAir.*.%02d.%d.m4a' % ( mon, year ) ) ) ])
    return days

def create_plot_year( year = _default_year ):
    calendar.setfirstweekday( 6 )
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
    nmiss = 0
    for mon in xrange(1, 13):
        cal = numpy.array( calendar.monthcalendar( year, mon ),
                           dtype = int )
        act_days = find_occupied_days( mon, year )
        data[mon] = (cal, act_days)
        wkdays = set( cal[:,1:-1].flatten() ) - set([ 0, ])
        nwkdays += len( wkdays )
        nmiss += len( wkdays - act_days )        
        
    #
    ## these are empty plots
    ax = fig.add_subplot(5,3,3)
    pylab.axis('off')
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    ax.text(0.15, 0.725, '\n'.join([ '%d / %d' % (nmiss, nwkdays),
                                     '%0.2f%% missing' % ( 100.0 * nmiss / nwkdays ) ]),
            fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
            horizontalalignment = 'left', verticalalignment = 'center',
            color = 'red' )
    ax.text(0.15, 0.275, '%0.2f%% coverage' % ( 100.0 - 100.0 * nmiss / nwkdays ),
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
    ax.add_patch(Rectangle((0.1, 0.1), 0.3, 0.35, linewidth = 3, facecolor = '#FF0000',
                           edgecolor = 'black' ) )
    ax.add_patch(Rectangle((0.1, 0.55), 0.3, 0.35, linewidth = 3, facecolor = '#00FF00',
                           edgecolor = 'black' ) )
    ax.text( 0.45, 0.275, 'MISSING', fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
             verticalalignment = 'center', horizontalalignment = 'left' )
    ax.text( 0.45, 0.725, 'EXISTS', fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
             verticalalignment = 'center', horizontalalignment = 'left' )
    
    for mon in xrange(1, 13):
        cal, act_days = data[ mon ]
        nweeks = cal.shape[0]
        iidx = max( numpy.where( matr == mon )[0] ) + 1
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
