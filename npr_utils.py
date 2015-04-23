#!/usr/bin/env python

import calendar, numpy, time, datetime, os
import xdg.BaseDirectory, ConfigParser
import multiprocessing, multiprocessing.pool
from distutils.spawn import find_executable
import urlparse, urllib

def find_necessary_executables():
    ffmpeg_exec = None
    for ffmpeg_exc in ('avconv', 'ffmpeg'):
        ffmpeg_exec = find_executable(ffmpeg_exc)
        if ffmpeg_exec is not None: break
    if ffmpeg_exec is None: return None
    #
    return { 'avconv' : ffmpeg_exec }
        
def store_api_key(npr_API_key):
    resource = 'nprstuff'
    filename = '%s.conf' % resource
    baseConfDir = xdg.BaseDirectory.save_config_path( resource )
    absPath = os.path.join( baseConfDir, filename )
    if os.path.isdir( absPath ):
        shutil.rmtree( absPath )
    elif os.path.isfile( absPath ):
        os.remove( absPath )
    #
    cparser = ConfigParser.RawConfigParser()
    cparser.add_section('NPR_DATA')
    cparser.set('NPR_DATA', 'apikey', npr_API_key)
    with open( absPath, 'wb') as openfile:
        cparser.write( openfile )
    os.chmod( absPath, 0600 )

def get_api_key():
    resource = 'nprstuff'
    filename = '%s.conf' % resource
    baseConfDir = xdg.BaseDirectory.save_config_path( resource )
    absPath = os.path.join( baseConfDir, filename )
    if not os.path.isfile( absPath ):
        raise ValueError("Error, default configuration file = %s does not exist." % absPath )
    cparser = ConfigParser.ConfigParser()
    cparser.read( absPath )
    if not cparser.has_section('NPR_DATA'):
        raise ValueError("Error, configuration file has not defined NPR_DATA section.")
    if not cparser.has_option('NPR_DATA', 'apikey'):
        raise ValueError("Error, configuration files has not defined an apikey.")
    npr_api_key = cparser.get('NPR_DATA', 'apikey')
    return npr_api_key

def get_decdate(date_s):
    return date_s.strftime('%d.%m.%Y')

def get_NPR_URL(date_s, program_id, NPR_API_key):
    """
    get the NPR API tag for a specific NPR program 
    """
    nprApiDate = date_s.strftime('%Y-%m-%d')
    result = urlparse.ParseResult(scheme = 'http', netloc = 'api.npr.org', path='/query', params='',
                                  query = urllib.urlencode({
                                      'id' : program_id,
                                      'date' : nprApiDate,
                                      'dateType' : 'story',
                                      'output' : 'NPRML',
                                      'apiKey' : NPR_API_key }), fragment = '')
    return result.geturl()
    #return 'http://api.npr.org/query?id=%d&date=%s&dateType=story&output=NPRML&apiKey=%s' % \
    #    ( program_id, nprApiDate, NPR_API_key )
    
def weekdays_of_month_of_year(year, month):
    days = filter(lambda day: day != 0,
                  numpy.array( calendar.monthcalendar(year, month), dtype=int)[:,0:5].flatten() )
    return sorted(days)

def saturdays_of_month_of_year(year, month):
    days = filter(lambda day: day != 0,
                  numpy.array( calendar.monthcalendar(year, month), dtype=int)[:,5].flatten() )
    return sorted(days)

# must be formatted in the form of a string of the form January 1, 2014
def get_time_from_datestring(datestring):
    dt = datetime.datetime.strptime(datestring, '%B %d, %Y')
    return datetime.date( dt.year, dt.month, dt.day )

# given a struct_time object, returns the date formatted in the form, January 1, 2014  
def get_datestring(date_s):
    return date_s.strftime('%B %d, %Y')

def is_weekday(date_s):
    return date_s.weekday() in xrange(5)

def is_saturday(date_s):
    return date_s.weekday() == 5

def is_sunday(dtime):
    return date_s.weekday() == 6

def get_order_number_weekday_in_year(date_s):
    assert( is_weekday(date_s ) )
    year_of_dtime = date_s.year
    all_wkdays_sorted = get_weekday_times_in_year( year_of_dtime )
    num = all_wkdays_sorted.index( date_s )
    return (num+1), len( all_wkdays_sorted )

def get_order_number_saturday_in_year(date_s):
    assert( is_saturday(date_s ) )
    year_of_dtime = date_s.year
    all_saturdays_sorted = get_saturday_times_in_year( year_of_dtime )
    num = all_saturdays_sorted.index( date_s )
    return (num+1), len( all_saturdays_sorted )

def get_saturday_times_in_year(year, getAll = True):
    datenow = datetime.datetime.now()
    nowd = datetime.date( datenow.year, datenow.month, datenow.day )
    initsats = sorted([ datetime.date(year, month, day) for
                        month in xrange(1, 13) for day in saturdays_of_month_of_year(year, month) ])
    if not getAll:
        initsats = filter(lambda actd: actd < nowd, initSats) 
    return initsats
    
def get_weekday_times_in_year(year, getAll = True):
    inittimes = sorted([ datetime.date(year, month, day) for 
                         month in xrange(1, 13) for day in weekdays_of_month_of_year(year, month) ])
    if not getAll:
        datenow = datetime.datetime.now()
        nowd = datetime.date( datenow.year, datenow.month, datenow.day )    
        inittimes = filter(lambda actd: actd < nowd, inittimes )
        
    return inittimes


class NoDaemonProcess(multiprocessing.Process):
    """
    magic to get multiprocessing to get processes to be able to start daemons
    I copied the code from http://stackoverflow.com/a/8963618/3362358, without
    any real understanding EXCEPT that I am extending a Pool using a
    NoDaemonProcess that always returns False, allowing me to create a pool of
    workers that can spawn other processes (by default, multiprocessing does not
    allow this)
    """
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess
