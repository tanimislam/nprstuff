import os, glob, sys, calendar, numpy, datetime
import uuid, requests, json, subprocess
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.patches import Rectangle
from mutagen.easymp4 import EasyMP4
from PyQt5.QtGui import QColor
from optparse import OptionParser
from nprstuff.core import freshair, npr_utils

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
  e_color = QColor("#1f77b4")
  s_color = QColor("#ff7f0e")
  hsv_start = numpy.array( s_color.getHsvF()[:-1] )
  hsv_end = numpy.array( e_color.getHsvF()[:-1] )
  hsv_mid = hsv_start * (1.0 - discrep * 0.9) + hsv_end * discrep * 0.9
  cmid = QColor.fromHsvF( hsv_mid[0], hsv_mid[1], hsv_mid[2], 1.0 )
  return str( cmid.name( ) ).upper( )

def find_occupied_days( mon, year = _default_year ):
  days = set([ int( os.path.basename( fname ).split('.')[2] ) for fname in
               glob.glob( os.path.join( _default_inputdir,
                                        'NPR.FreshAir.*.%02d.%d.m4a' % ( mon, year ) ) ) ])
  return days

def find_underoccupied_dates( mon, year = _default_year ):
  newdict = {}
  ffprobe_exec = find_executable( 'ffprobe' )
  if ffprobe_exec is None:
    raise ValueError("Error, cannot do work without visible FFPROBE" )
  days = find_occupied_days( mon, year = year )
  daydict = dict(map(lambda day: (
    day, os.path.join( _default_inputdir,
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
    expectdur = sum(map(_get_story_dur, html.find_all( 'story' ) ) )
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
    for mon in range(1,13 ):
      cal = suncal( mon, year )
      act_days = find_occupied_days( mon, year )
      newdict = find_underoccupied_dates( mon, year )
      data[ mon ] = (cal, act_days, newdict)
      for idx in range(cal.shape[0]):
        for jdx in range(1,6):
          if cal[ idx, jdx ] == 0: continue
          day = cal[ idx, jdx ]
          caldate = datetime.date( year, mon, day )
          if caldate > nowdate: continue
          nwkdays += 1
          if day not in act_days: nmiss += 1
          nunder += len( newdict ) 
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

  nowdate = datetime.datetime.now( ).date( )
  #
  def _get_day_color( idx, jdx, cal, ndict, adays ):
    if cal[ idx, jdx ] == 0: return None
    if jdx == 0 or jdx == 6: return '#E8E8E8'
    else:
      if cal[ idx, jdx ] in adays:
        if cal[ idx, jdx ] not in ndict: return exist_color
        dur, discrep, color = ndict[ cal[idx, jdx] ]
        return color
      else:
        color = not_exist_color
        actdate = datetime.date( year, mon, cal[ idx, jdx ] )
        if year >= nowdate.year and jdx not in (0, 6 ):
          if actdate > nowdate: color = 'yellow'
        return color
  
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
