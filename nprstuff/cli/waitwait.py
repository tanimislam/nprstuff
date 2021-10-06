from nprstuff import signal_handler
import logging, datetime, signal, os, time
signal.signal( signal.SIGINT, signal_handler )
from dateutil.relativedelta import relativedelta
from argparse import ArgumentParser
from nprstuff import logging_dict, nprstuff_logger as logger
from nprstuff.core.waitwait import get_waitwait, get_all_waitwaits_year
from nprstuff.core.npr_utils import get_datestring, get_time_from_datestring, get_waitwait_downloaddir, is_saturday

_default_inputdir = os.getcwd( )
try:
    _default_inputdir = get_waitwait_downloaddir( )
except Exception as e: pass
_default_year = 2010

def _get_last_saturday(datetime_s):
    date_s = datetime_s.date( )
    #
    ## first find today's date
    tm_wday = date_s.weekday()
    if tm_wday < 5: tm_wday = tm_wday + 7
    days_go_back = tm_wday - 5
    date_sat = date_s - datetime.timedelta(days_go_back, 0, 0)
    return date_sat

def _waitwait( ):
    parser = ArgumentParser( )
    parser.add_argument('--dirname', dest='dirname', type=str,
                        action = 'store', default = _default_inputdir,
                        help = 'Name of the directory to store the file. Default is %s.' %
                        _default_inputdir )
    parser.add_argument('--date', dest='date', type=str,
                        action = 'store', default =
                        get_datestring(_get_last_saturday( datetime.datetime.now())),
                        help = 'The date, in the form of "January 1, 2014." The default is last Saturday, %s.' %
                        get_datestring( _get_last_saturday( datetime.datetime.now() ) ) )
    parser.add_argument('--dump', dest='do_dump', action='store_true', default = False,
                        help = 'If chosen, download the NPR XML data sheet for this Wait Wait episode.')
    parser.add_argument('--level', dest='level', action='store', type=str, default = 'NONE',
                        choices = sorted( logging_dict ),
                        help = 'choose the debug level for downloading NPR Wait Wait episodes or their XML representation of episode info. Can be one of %s. Default is NONE.' % sorted( logging_dict ) )
    parser.add_argument('--justfix', dest='do_justfix', action='store_true', default = False,
                        help = "If chosen, just fix the title of an existing NPR Wait Wait episode's file.")
    args = parser.parse_args( )
    logger.setLevel( logging_dict[ args.level ] )
    fname = get_waitwait(
        args.dirname, get_time_from_datestring( args.date ),
        dump = args.do_dump, justFix = args.do_justfix )

def _waitwait_by_year( ):
    parser = ArgumentParser( )
    parser.add_argument('--year', dest='year', action='store', type=int, default = _default_year,
                        help = 'Year in which to write out all Wait Wait episodes. Default is %d.' %
                        _default_year )
    parser.add_argument('--inputdir', dest = 'inputdir', action='store', type = str,
                        default = _default_inputdir, help = 'Directory into which ' +
                        'to store the NPR Wait Wait episodes. Default is %s.' %
                        _default_inputdir)
    parser.add_argument('--level', dest='level', action='store', type=str, default = 'NONE',
                        choices = sorted( logging_dict ),
                        help = 'choose the debug level for downloading NPR Wait Wait episodes or their XML representation of episode info. Can be one of %s. Default is NONE.' % sorted( logging_dict ) )
    args = parser.parse_args( )
    logger.setLevel( logging_dict[ args.level ] )
    get_all_waitwaits_year( args.year, args.inputdir )

def _waitwait_crontab( ):
    parser = ArgumentParser( )
    parser.add_argument(
        '--level', dest='level', action='store', type=str, default = 'NONE',
        choices = sorted( logging_dict ),
        help = 'choose the debug level for downloading NPR Wait Wait episodes or their XML representation of episode info. Can be one of %s. Default is NONE.' % sorted( logging_dict ) )
    args = parser.parse_args( )
    logger.setLevel( logging_dict[ args.level ] )
    
    #
    ## get current date
    current_date = datetime.date.fromtimestamp( time.time() )
    current_year = current_date.year
    #
    ## if not on a saturday, go first saturday back
    if not is_saturday( current_date ):
        day_of_week = current_date.weekday( )
        if day_of_week >= 5: days_back = day_of_week - 5
        else: days_back = days_back = day_of_week + 2
        days_back = relativedelta( days = days_back )
        current_date = current_date - days_back
        if current_date.year != current_year: return
    
    #
    ## now download the episode into the correct directory
    get_waitwait(_default_inputdir, current_date)
