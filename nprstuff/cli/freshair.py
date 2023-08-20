import os, sys, signal
from nprstuff import signal_handler
signal.signal( signal.SIGINT, signal_handler )
import datetime, time, glob, mutagen.mp4
from multiprocessing import Pool, cpu_count
from nprstuff import logging_dict, nprstuff_logger as logger
from nprstuff.core import freshair, freshair_by_year, npr_utils
from argparse import ArgumentParser

_default_inputdir = os.getcwd( )
try:
    _default_inputdir = npr_utils.get_freshair_downloaddir( )
except: pass

def _freshair_crontab( ):
    """
    This python method downloads a Fresh Air episode on a particular weekday.
    """
    logger.setLevel( logging_dict[ 'INFO' ] )
    #
    ## get current time
    current_date = datetime.datetime.now( ).date( )
    if not npr_utils.is_weekday( current_date ):    
      logger.error( 
        "Error, today is not a weekday. Instead, today is %s." %
        current_date.strftime('%A') )
      return
    #
    ## now download the episode into the correct directory
    dirname = os.path.join( _default_inputdir, '%04d' % current_date.year )
    try:
      if not os.path.isdir( dirname ): os.mkdir( dirname )
      freshair.get_freshair(
        dirname, current_date,
        check_if_exist = True)
    except: pass

def _freshair( ):
    parser = ArgumentParser( )
    parser.add_argument('-X', '--dirname', dest='dirname', type=str,
                        action = 'store', default = _default_inputdir,
                        help = 'Name of the directory to store the file. Default is %s.' % _default_inputdir )
    parser.add_argument('-d', '--date', dest='date', type=str,
                        action = 'store', default = npr_utils.get_datestring( datetime.datetime.now()),
                        help = 'The date, in the form of "January 1, 2014." The default is today\'s date, %s.' %
                        npr_utils.get_datestring( datetime.datetime.now() ) )
    parser.add_argument('--mp3exist', dest='mp3_exist', action='store_true', default = False,
                        help = ' '.join([
                            'If chosen, then do not download the transitional mp3 files.',
                            'Use the ones that already exist.' ]) )
    parser.add_argument('-D', '--debug', dest='debug', action='store_true',
                        help = 'If chosen, dump out NPR Freshair webpage as XML.',
                        default = False)
    parser.add_argument('-L', '--level', dest='level', action='store', type=str, default = 'NONE',
                        choices = sorted( logging_dict ),
                        help = 'choose the debug level for downloading NPR Fresh Air episodes or their XML representation of episode info. Can be one of %s. Default is NONE.' % sorted( logging_dict ) )
    parser.add_argument('-r', '--relax', dest='relax_date_check', action='store_true', default = False,
                        help = 'If chosen, then do NOT do a date check validation of NPR URL articles.' )
    parser.add_argument('-A', '--addyear', dest = 'do_add_year', action = 'store_true', default = False,
                        help = 'If chosen, then ADD the year to the directory name in which to store.' )
    args = parser.parse_args( )
    date_s = npr_utils.get_time_from_datestring( args.date )
    dirname = os.path.expanduser( args.dirname )
    if args.do_add_year: dirname = os.path.join( dirname, '%04d' % date_s.year )
    #
    logger.setLevel( logging_dict[ args.level ] )
    fname = freshair.get_freshair(
        dirname, date_s,
        debug = args.debug, mp3_exist = args.mp3_exist,
        relax_date_check = args.relax_date_check )

def _freshair_by_year( ):
    default_year = datetime.datetime.now( ).year
    parser = ArgumentParser()
    parser.add_argument('--year', dest='year', action='store', type=int, default = default_year,
                        help = 'Year in which to write out all Fresh Air episodes. Default is %d.' %
                        default_year )
    parser.add_argument( '--inputdir', dest = 'inputdir', action='store', type = str,
                        default = _default_inputdir, help =
                        ' '.join([ 'Directory into which',
                                  'to store the NPR Fresh Air episodes.',
                                  'Default is %s.' % _default_inputdir ]) )
    parser.add_argument('--quiet', dest='is_verbose', action='store_false', default = True,
                        help = ' '.join([ 'If chosen, do not print verbose output from the action of this',
                                         'script. By default this is false.' ]) )
    parser.add_argument('--coverage', dest = 'get_coverage', action = 'store_true', default = False,
                        help = 'If chosen, just give the list of missing Fresh Air episodes and nothing else.')
    parser.add_argument('--audit', dest = 'do_audit', action = 'store_true', default = False,
                        help = 'If chosen, do the audit picture here.')
    parser.add_argument('--level', dest='level', action='store', type=str, default = 'NONE',
                        choices = sorted( logging_dict ),
                        help = 'choose the debug level for downloading NPR Fresh Air episodes or their XML representation of episode info. Can be one of %s. Default is NONE.' % sorted( logging_dict ) )
    args = parser.parse_args( )
    logger.setLevel( logging_dict[ args.level ] )
    if not args.do_audit:
        freshair.process_all_freshairs_by_year(
            args.year, args.inputdir, verbose = args.is_verbose,
            justCoverage = args.get_coverage )
    else: freshair_by_year.create_plot_year( args.year )

#
##
def _find_NPR_files_to_modify_perproc( filename ):
    """
    This checks to see whether to modify this file
    """
    atoms = mutagen.mp4.Atoms(open(filename, 'rb'))
    info = mutagen.mp4.MP4Info(atoms, open(filename, 'rb'))
    if info.length > 1800: return None
    #
    ## check modification time
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
    ltime = datetime.datetime.fromtimestamp(time.time())
    tdelta = ltime - mtime
    if tdelta.days < 90: return None
    #
    ## matches conditions, return filename and date associated with this time
    strdate = '.'.join(os.path.basename(filename).split('.')[2:5])
    mydate = datetime.datetime.strptime(strdate, '%d.%m.%Y').date( )
    return mydate
        
def _find_NPR_dates_to_fix( ):
  time0 = time.perf_counter( )
  filenames_to_process = glob.glob( os.path.join(
    _default_inputdir, '*', 'NPR.FreshAir.*.m4a' ) )
  logger.info( 'found %02d file names to process.' % len( filenames_to_process ) )
  with Pool(processes = cpu_count( ) ) as pool:
    missing_dates = set(filter(None, pool.map(
      _find_NPR_files_to_modify_perproc, filenames_to_process ) ) )
    logger.info( 'found %02d dates to fix in %0.3f seconds.' % (
      len( missing_dates ), time.perf_counter( ) - time0 ) )
    return missing_dates

def _process_dates( npr_dates_to_fix ):
  time0 = time.perf_counter( )
  if len(npr_dates_to_fix) > 0:
    logger.info( 'GOT %d dates to fix' % len(npr_dates_to_fix) )
  for idx, mydate in enumerate(npr_dates_to_fix):
    dirname = os.path.join( _default_inputdir, '%04d' % mydate.year )
    freshair.get_freshair( dirname, mydate)
    logger.info(
      'PROCESSED %d / %d DATES IN %0.3f SECONDS' % (
        idx + 1,
        len( npr_dates_to_fix ), time.perf_counter( ) - time0 ) )
    if len( npr_dates_to_fix ) > 0:
      logger.info(
        'PROCESSED ALL DATES IN %0.3f SECONDS' % ( time.perf_counter( ) - time0) )

def _freshair_fix_crontab( verbose = True ):
  npr_dates_to_fix = _find_NPR_dates_to_fix( )
  _process_dates( npr_dates_to_fix, verbose = verbose )
