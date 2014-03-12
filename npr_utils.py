#!/usr/bin/env python

import calendar, numpy, time

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
    return time.strptime(datestring, '%B %d, %Y') 

# given a struct_time object, returns the date formatted in the form, January 1, 2014  
def get_datestring(dtime):
    return time.strftime('%B %d, %Y', dtime)

def get_sanitized_time(dtime):
    return get_time_from_datestring( get_datestring( dtime ) )

def is_weekday(dtime):
    return dtime.tm_wday in xrange(5)

def is_saturday(dtime):
    return dtime.tm_wday == 5

def is_sunday(dtime):
    return dtime.tm_wday == 6

def get_order_number_weekday_in_year(dtime):
    dtime_s = get_sanitized_time(dtime)
    if not is_weekday(dtime_s):
        raise ValueError("Error, day = %s is not a weekday" % get_datestring(dtime_s) )
    year_of_dtime = dtime_s.tm_year
    all_wkdays_sorted = get_weekday_times_in_year( year_of_dtime )
    num, tm = max(filter( lambda tup: tup[1] == dtime_s,
                          enumerate( all_wkdays_sorted ) ) )
    return (num+1), len( all_wkdays_sorted )

def get_order_number_saturday_in_year(dtime):
    dtime_s = get_sanitized_time(dtime)
    if not is_saturday(dtime_s):
        raise ValueError("Error, day = %s is not a Saturday." % get_datestring(dtime_s) )
    year_of_dtime = dtime_s.tm_year
    all_saturdays_sorted = get_saturday_times_in_year( year_of_dtime )
    num, tm = max(filter( lambda tup: tup[1] == dtime_s,
                          enumerate( all_saturdays_sorted) ) )
    return (num+1), len( all_saturdays_sorted )

def get_saturday_times_in_year(year):
    return sorted([ time.strptime('%d-%d-%04d' % ( day, month, year), '%d-%m-%Y') for
                    month in xrange(1, 13) for day in saturdays_of_month_of_year(year, month) ])
    
def get_weekday_times_in_year(year):
    return sorted([ time.strptime('%d-%d-%04d' % ( day, month, year), '%d-%m-%Y') for
                    month in xrange(1, 13) for day in weekdays_of_month_of_year(year, month) ])


    
    
