import os, glob, sys, calendar, numpy, datetime
import uuid, requests, json, subprocess
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Rectangle
from mutagen.easymp4 import EasyMP4
from distutils.spawn import find_executable
from PyQt5.QtGui import QColor
from nprstuff.core import freshair, npr_utils

_default_inputdir = '/mnt/media/freshair'
_default_year = 2010

def suncal( mon, year = _default_year ):
    """
    returns the calendar of day numbers for a given month and year, as numpy integer array of 7 columns (Sunday is the column 0, and Saturday is column 6). For example, for December 2019, here is the output.

    .. code-block:: python

       >> suncal( 12, 2019 )
       >> array([[ 1,  2,  3,  4,  5,  6,  7],
       [ 8,  9, 10, 11, 12, 13, 14],
       [15, 16, 17, 18, 19, 20, 21],
       [22, 23, 24, 25, 26, 27, 28],
       [29, 30, 31,  0,  0,  0,  0]])

    Here, December 1, 2019, is a Sunday, and December 7, 2019, is a Saturday. Zero array values are *not* in December 2019 (December 31, 2019, is a Tuesday).

    :param int mon: the calendar month. ``January`` is 1, ``December`` is 12.
    :param int year: the calendar year.
    :returns: an integer :py:class:`numpy array <numpy.ndarray>` of calendar days for that month and year.
    :rtype: :py:class:`numpy array <numpy.ndarray>`

    .. seealso:: :py:meth:`create_plot_year <nprstuff.core.freshair_by_year.create_plot_year>`.
    """
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
    """
    returns a hex color linearly interpolated between "#1f77b4" (value of 0.0) and "#ff7f0e" (value of 1.0) for a value :math:`0 \le v \le 1`.

    :param float discrep: the value over which to interpolate to return a hex color.
    :returns: a hex color linearly interpolated between "#1f77b4" (value of 0.0) and "#ff7f0e" (value of 1.0).
    :rtype: str
    """
    assert( discrep <= 1.0 )
    assert( discrep >= 0.0 )
    e_color = QColor("#1f77b4")
    s_color = QColor("#ff7f0e")
    hsv_start = numpy.array( s_color.getHsvF()[:-1] )
    hsv_end = numpy.array( e_color.getHsvF()[:-1] )
    hsv_mid = hsv_start * (1.0 - discrep * 0.9) + hsv_end * discrep * 0.9
    cmid = QColor.fromHsvF( hsv_mid[0], hsv_mid[1], hsv_mid[2], 1.0 )
    return str( cmid.name( ) ).upper( )

def find_occupied_days( mon, year = _default_year ):
    """
    :param int mon: the calendar month. ``January`` is 1, ``December`` is 12.
    :param int year: the calendar year.
    :returns: a :py:class:`set` of calendar weekdays of `NPR Fresh Air`_ episodes for that calendar month and year.
    :rtype: set
    """
    days = set(map(lambda fname: int( os.path.basename( fname ).split('.')[2] ),
                   glob.glob( os.path.join(
                    _default_inputdir,
                    'NPR.FreshAir.*.%02d.%d.m4a' % ( mon, year ) ) ) ) )
    return days

def find_underoccupied_dates( mon, year = _default_year ):
    """
    :param int mon: the calendar month. ``January`` is 1, ``December`` is 12.
    :param int year: the calendar year.
    :returns: a :py:class:`dict`: key is the day of the month and year, and value is the (candidate, too short) length of the `NPR Fresh Air`_ episode on file, in seconds.
    :rtype: dict
    """
    newdict = {}
    ffprobe_exec = find_executable( 'ffprobe' )
    if ffprobe_exec is None:
        raise ValueError("Error, cannot do work without visible FFPROBE" )
    days = find_occupied_days( mon, year = year )
    daydict = dict(map(lambda day: (
        day, os.path.join(
            _default_inputdir,
            'NPR.FreshAir.%02d.%02d.%d.m4a' % ( day, mon, year ) ) ),
        find_occupied_days( mon, year = year ) ) )
    actdict = dict(map(lambda day: ( day, EasyMP4( daydict[day] ).info.length ),
                       filter(lambda day: os.stat(daydict[day]).st_size <= 4e7 and
                              EasyMP4( daydict[day] ).info.length <= 35*60, daydict ) ) )
    def _get_story_dur( story_elem ):
        m3u_elems = story_elem.find_all('mp3')
        if len(m3u_elems) == 0: return 0.0
        mp3_url = requests.get( m3u_elems[0].text ).text.strip( )
        tmpfile = '%s.mp3' % ''.join(map(lambda idx: str(uuid.uuid4( )).split('-')[0], range(2)))
        duration = 0.0
        with open( tmpfile, 'wb' ) as openfile:
            openfile.write( requests.get( mp3_url ).content )
            proc = subprocess.Popen([ ffprobe_exec, '-v', 'quiet', '-show_streams',
                                     '-show_format', '-print_format', 'json', tmpfile ],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
            stdout_val, stderr_val = proc.communicate( )
            data = json.loads( stdout_val )
            duration = float( data['format']['duration'] )
        os.remove( tmpfile )
        return duration
    #
    def _process_discrepancy( day, mon, year, actdict ):
        dt_s = datetime.datetime.strptime('%02d.%02d.%04d' % ( day, mon, year ),
                                          '%d.%m.%Y' ).date( )
        html = freshair.get_freshair(
            os.path.expanduser('~'), dt_s,
            debug = True, to_file_debug = False )
        expectdur = sum(list(map(_get_story_dur, html.find_all( 'story' ) ) ) )
        totlength = actdict[ day ]
        if expectdur == 0:
            return ( day, ( totlength, 1.0, get_color( 1.0 ) ) )
        discrep = max( 0.0, expectdur * 0.985 - totlength ) / ( 0.985 * expectdur )
        if discrep <= 1e-6: return None
        return ( day, ( totlength, discrep, get_color( discrep ) ) )
    #
    newdict = dict(filter(None, map(lambda day: _process_discrepancy(
        day, mon, year, actdict ), actdict ) ) )
    return newdict

def create_plot_year( year = _default_year ):
    """
    Creates an SVGZ (GZIP_ compressed SVG_) calendar plot that summarizes the `NPR Fresh Air`_ episodes in a specified year. It is easier to show the figure with description than to describe without a figure, here for 2020 (created on 13 AUGUST 2020).

    .. image:: _static/freshair.2020.svg
       :width: 100%
       :align: center
       
    The dark blue boxes are for ``existing`` episodes. The light yellow boxes are for episodes that have not yet aired. The light orange boxes are for ``missing`` episodes. And those boxes colored from light orange on the left to turquoise on the right are ``underoccupied`` episodes: I have downloaded them, but they are shorter than the published duration of that `NPR Fresh Air`_ episode.

    :param int year: the calendar year.

    .. seealso:: :py:meth:`suncal <nprstuff.core.freshair_by_year.suncal>`.

    .. _SVG: https://en.wikipedia.org/wiki/Scalable_Vector_Graphics
    .. _GZIP: https://en.wikipedia.org/wiki/Gzip
    """
    # calendar.setfirstweekday( 6 )
    fig = Figure( figsize = ( 8 * 3, 6 * 5 ) )
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
    nowdate = datetime.datetime.now( ).date( )
    if year < nowdate.year:
        for mon in range(1, 13):
            cal = suncal( mon, year )
            act_days = find_occupied_days( mon, year )
            newdict = find_underoccupied_dates( mon, year )
            data[mon] = (cal, act_days, newdict)
            wkdays = set( cal[:,1:-1].flatten() ) - set([ 0, ])
            nwkdays += len( wkdays )
            nmiss += len( wkdays - act_days )
            nunder += len( newdict )
    else:
        for mon in range(1, 13):
            cal = suncal( mon, year )
            act_days = find_occupied_days( mon, year )
            newdict = find_underoccupied_dates( mon, year )
            data[ mon ] = (cal, act_days, newdict)
            nunder += len( newdict )
            for idx in range(cal.shape[0]):
                for jdx in range(1,6):
                    if cal[ idx, jdx ] == 0: continue
                    day = cal[ idx, jdx ]
                    caldate = datetime.date( year, mon, day )
                    if caldate > nowdate: continue
                    nwkdays += 1
                    if day not in act_days: nmiss += 1
    #
    ## these are the legend plots
    ax = fig.add_subplot(5,3,3)
    ax.axis('off')
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
    ax.axis('off')
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    ax.text(0.5,0.5, '\n'.join([ '%d' % year, 'FRESH AIR', 'EPISODES' ]),
            fontdict = { 'fontsize' : 64, 'fontweight' : 'bold' },
            horizontalalignment = 'center', verticalalignment = 'center' )
    #
    ax = fig.add_subplot(5,3,1)
    ax.axis('off')
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    #not_exist_color = '#FF0000'
    #exist_color = '#00FF00'
    not_exist_color = '#ff7f0e'
    exist_color = '#1f77b4'
    ax.add_patch(Rectangle((0.1, 0.1), 0.2, 0.25, linewidth = 3, facecolor = not_exist_color,
                           edgecolor = 'black', alpha = 0.5 ) )
    for idx in range(100):
        ax.add_patch(Rectangle((0.1 + 0.002 * idx, 0.4), 0.002, 0.25, linewidth = 0,
                            facecolor = get_color( 0.005 + 0.01 * idx ), edgecolor = 'none',
                            alpha = 0.5 ) )
        ax.add_patch(Rectangle((0.1, 0.4), 0.2, 0.25, linewidth = 3, facecolor = 'none',
                            edgecolor = 'black' ) )
        ax.add_patch(Rectangle((0.1, 0.7), 0.2, 0.25, linewidth = 3, facecolor = exist_color,
                               edgecolor = 'black', alpha = 0.5 ) )
        ax.text( 0.35, 0.2, 'MISSING', fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
            verticalalignment = 'center', horizontalalignment = 'left' )
        ax.text( 0.35, 0.5, 'UNDEROCCUPIED', fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
                verticalalignment = 'center', horizontalalignment = 'left' )
        ax.text( 0.35, 0.8, 'EXISTS', fontdict = { 'fontsize' : 32, 'fontweight' : 'bold' },
                verticalalignment = 'center', horizontalalignment = 'left' )
    #
    nowdate = datetime.datetime.now( ).date( )
    #
    def _get_day_color( idx, jdx, cal, ndict, adays ):
        if cal[ idx, jdx ] == 0: return None
        if jdx == 0 or jdx == 6: return '#E8E8E8'
        #
        ## if in adays
        if cal[ idx, jdx ] in adays:
            if cal[ idx, jdx ] not in ndict: return exist_color
            dur, discrep, color = ndict[ cal[idx, jdx] ]
            return color
        #
        ## otherwise
        color = not_exist_color
        actdate = datetime.date( year, mon, cal[ idx, jdx ] )
        if year >= nowdate.year and jdx not in (0, 6 ):
            if actdate > nowdate: color = 'yellow'
        return color
    #
    def _process_axes( ax, mon, data ):
        ax.set_xlim([0,1])
        ax.set_ylim([0,1])
        ax.axis( 'off' )
        cal, act_days, newdict = data[ mon ]
        nweeks = cal.shape[0]
        for jdx in range(7):
            ax.text( 0.01 + 0.14 * (jdx + 0.5), 0.93, days[jdx],
                    fontdict = { 'fontsize' : 14, 'fontweight' : 'bold' },
                    horizontalalignment = 'center',
                    verticalalignment = 'center' )
        #
        for idx in range(nweeks):
            for jdx in range(7):
                color = _get_day_color( idx, jdx, cal, newdict, act_days )
                if color is None: continue
                #
                ax.add_patch( Rectangle( ( 0.01 + 0.14 * jdx,
                                        0.99 - 0.14 - 0.14 * (idx + 1) ),
                                        0.14, 0.14, linewidth = 2,
                                        facecolor = color, edgecolor = 'black', alpha = 0.5 ) )
                ax.text( 0.01 + 0.14 * ( jdx + 0.5 ),
                        0.99 - 0.14 - 0.14 * ( idx + 0.5 ), '%d' % cal[idx, jdx],
                        fontdict = { 'fontsize' : 14, 'fontweight' : 'bold' },
                        horizontalalignment = 'center',
                        verticalalignment = 'center' )
        monname = datetime.datetime.strptime(
            '%02d.%d' % ( mon, year ),
            '%m.%Y' ).strftime('%B').upper( )
        ax.set_title( monname, fontsize = 14, fontweight = 'bold' )
    #
    list(map(lambda mon: _process_axes( fig.add_subplot(5, 3, mon + 3 ), mon, data ),
           range(1, 13) ) )
    canvas = FigureCanvasAgg(fig)
    canvas.print_figure( 'freshair.%d.svgz' % year, bbox_inches = 'tight' )
