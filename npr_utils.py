#!/usr/bin/env python

import calendar, numpy, time, datetime
import multiprocessing, multiprocessing.pool

def get_decdate(date_s):
    return date_s.strftime('%d.%m.%Y')

def get_NPR_URL(date_s, program_id, NPR_API_key):
    """
    get the NPR API tag for this Fresh Air episode 
    """
    nprApiDate = date_s.strftime('%Y-%m-%d')
    return 'http://api.npr.org/query?id=%d&date=%s&dateType=story&output=NPRML&apiKey=%s' % \
        ( program_id, nprApiDate, NPR_API_key )
    
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
def get_datestring(dtime):
    return time.strftime('%B %d, %Y', dtime)

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
