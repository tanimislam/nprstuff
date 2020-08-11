import os, sys, signal
from nprstuff import signal_handler
signal.signal( signal.SIGINT, signal_handler )
import datetime, time, multiprocessing, glob, mutagen.mp4
from nprstuff.core import freshair, freshair_by_year, npr_utils
from argparse import ArgumentParser

_default_inputdir = '/mnt/media/freshair'

def _freshair_crontab( ):
    """
    This python module downloads a Fresh Air episode on a particular weekday
    """
    # get current time
    current_date = datetime.date.fromtimestamp(time.time())
    if not npr_utils.is_weekday( current_date ):
        print("Error, today is not a weekday. Instead, today is %s." %
            current_date.strftime('%A') )
        return
  
    # now download the episode into the correct directory
    freshair.get_freshair(
        _default_inputdir, current_date,
        check_if_exist = True)

def _freshair( ):
    parser = ArgumentParser( )
    parser.add_argument('--dirname', dest='dirname', type=str,
                        action = 'store', default = _default_inputdir,
                        help = 'Name of the directory to store the file. Default is %s.' % _default_inputdir )
    parser.add_argument('--date', dest='date', type=str,
                        action = 'store', default = npr_utils.get_datestring( datetime.datetime.now()),
                        help = 'The date, in the form of "January 1, 2014." The default is today\'s date, %s.' %
                        npr_utils.get_datestring( datetime.datetime.now() ) )
    parser.add_argument('--mp3exist', dest='mp3_exist', action='store_true', default = False,
                        help = ' '.join([
                            'If chosen, then do not download the transitional mp3 files.',
                            'Use the ones that already exist.' ]) )
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help = 'If chosen, run freshair.py in debug mode. Useful for debugging :)',
                        default = False)
    args = parser.parse_args( )
    dirname = os.path.expanduser( args.dirname )
    fname = freshair.get_freshair(
        dirname, npr_utils.get_time_from_datestring( args.date ),
        debug = args.debug, mp3_exist = args.mp3_exist )

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
    parser.add_argument('--quiet', dest='is_quiet', action='store_true', default = False,
                        help = ' '.join([ 'If chosen, do not print verbose output from the action of this',
                                         'script. By default this is false.' ]) )
    parser.add_argument('--coverage', dest = 'get_coverage', action = 'store_true', default = False,
                        help = 'If chosen, just give the list of missing Fresh Air episodes and nothing else.')
    parser.add_argument('--audit', dest = 'do_audit', action = 'store_true', default = False,
                        help = 'If chosen, do the audit picture here.')
    args = parser.parse_args( )
    if not args.do_audit:
        verbose = not args.is_quiet
        freshair.process_all_freshairs_by_year(
            args.year, args.inputdir, verbose = verbose,
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
    filenames_to_process = glob.glob( os.path.join(
        _default_inputdir, 'NPR.FreshAir.*.m4a' ) )
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        return set(filter(None, pool.map(
        _find_NPR_files_to_modify_perproc, filenames_to_process ) ) )

def _process_dates(npr_dates_to_fix, verbose = False):
    if verbose and len(npr_dates_to_fix) > 0:
        print( 'GOT %d dates to fix' % len(npr_dates_to_fix) )
    time0 = time.time()
    for idx, mydate in enumerate(npr_dates_to_fix):
        freshair.get_freshair(_default_inputdir, mydate)
        if verbose:
            print( 'PROCESSED %d / %d DATES IN %0.3f SECONDS' % (
                idx + 1,
                len(npr_dates_to_fix), time.time() - time0) )
    if verbose and len(npr_dates_to_fix) > 0:
        print( 'PROCESSED ALL DATES IN %0.3f SECONDS' % ( time.time() - time0) )

def _freshair_fix_crontab( verbose = True ):
    npr_dates_to_fix = _find_NPR_dates_to_fix( )
    _process_dates( npr_dates_to_fix, verbose = verbose )
