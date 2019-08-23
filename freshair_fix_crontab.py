#!/usr/bin/env python3

"""
This python program tries to re-download those NPR Fresh Air programs
that are shorter than 30 minutes, and which have a modification time
more than 90 days before the current time
"""
import os, sys, signal
from nprstuff.core import signal_handler, freshair, npr_utils
signal.signal( signal.SIGINT, signal_handler )
import glob, multiprocessing, mutagen.mp4, time, datetime

def _process_freshair_perproc( mydate ):
    try:
        fname = freshair.get_freshair( '/mnt/media/freshair', mydate )
        if fname is None: return None
        return mydate
    except Exception as e:
        print(e)
        return None

def find_missing_dates( mon, year = datetime.datetime.now( ).date( ).year ):
    assert( mon in range(1, 13))
    weekdays_of_month = npr_utils.weekdays_of_month_of_year( year, mon )
    valid_filenames = set(map( lambda day:
                               os.path.join( '/mnt/media/freshair',
                                             'NPR.FreshAir.%02d.%02d.%04d.m4a' % ( day, mon, year ) ),
                               npr_utils.weekdays_of_month_of_year( year, mon ) ) )
    filenames_act = set(glob.glob(
        os.path.join( '/mnt/media/freshair/NPR.FreshAir.*.%02d.%04d.m4a' % ( mon, year ) ) ) )
    filenames_remain = list(valid_filenames - filenames_act)
    if len( filenames_remain ) == 0: return
    print( 'NUMBER OF CANDIDATE EPS REMAIN FOR %d/%d: %d' % (
        mon, year, len( filenames_remain ) ) )
    days_remain = list( map(lambda filename: int(
        os.path.basename( filename ).split('.')[2] ), filenames_remain ) )
    input_tuples = list( map(lambda day: datetime.datetime.strptime(
        '%02d.%02d.%04d' % ( day, mon, year ),
        '%d.%m.%Y').date( ), days_remain ) )
    # pool = multiprocessing.Pool( processes = multiprocessing.cpu_count( ) )
    successes = list(
        filter(None, map( _process_freshair_perproc, input_tuples ) ) )
    print( 'successes (%d/%d): %s' % ( len(successes), len(input_tuples), successes ) )

"""
This checks to see whether to modify this file
"""
def find_NPR_files_to_modify_perproc( filename ):
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
        
def find_NPR_dates_to_fix( ):
    filenames_to_process = glob.glob('/mnt/media/freshair/NPR.FreshAir.*.m4a')
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        return set(filter(None, pool.map(
            find_NPR_files_to_modify_perproc, filenames_to_process ) ) )

def process_dates(npr_dates_to_fix, verbose = False):
    if verbose and len(npr_dates_to_fix) > 0:
        print( 'GOT %d dates to fix' % len(npr_dates_to_fix) )
    time0 = time.time()
    for idx, mydate in enumerate(npr_dates_to_fix):
        freshair.get_freshair('/mnt/media/freshair', mydate)
        if verbose:
            print( 'PROCESSED %d / %d DATES IN %0.3f SECONDS' % (
                idx+1,
                len(npr_dates_to_fix), time.time() - time0) )
    if verbose and len(npr_dates_to_fix) > 0:
        print( 'PROCESSED ALL DATES IN %0.3f SECONDS' % ( time.time() - time0) )

def freshair_fix_crontab( verbose = True ):
    npr_dates_to_fix = find_NPR_dates_to_fix( )
    process_dates( npr_dates_to_fix, verbose = verbose )

if __name__=='__main__':
    freshair_fix_crontab( )

