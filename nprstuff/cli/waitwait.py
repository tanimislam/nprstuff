from nprstuff import signal_handler
import logging, datetime, signal
signal.signal( signal.SIGINT, signal_handler )
from argparse import ArgumentParser
from nprstuff.core.waitwait import get_waitwait, get_all_waitwaits_year
from nprstuff.core.npr_utils import get_datestring, get_time_from_datestring

_default_inputdir = '/mnt/media/waitwait'
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
    parser.add_argument('--debug', dest='do_debug', action='store_true', default = False,
                        help = 'If chosen, download the NPR XML data sheet for this Wait Wait episode.')
    parser.add_argument('--justfix', dest='do_justfix', action='store_true', default = False,
                        help = "If chosen, just fix the title of an existing NPR Wait Wait episode's file.")
    args = parser.parse_args( )
    logger = logging.getLogger( )
    if args.do_debug: logger.basicConfig( level = logging.DEBUG )
    fname = get_waitwait(
        args.dirname, get_time_from_datestring( args.date ),
        debug = args.do_debug, justFix = args.do_justfix )

def _waitwait_by_year( ):
    parser = ArgumentParser( )
    parser.add_argument('--year', dest='year', action='store', type=int, default = _default_year,
                        help = 'Year in which to write out all Fresh Air episodes. Default is %d.' %
                        _default_year )
    parser.add_argument('--inputdir', dest = 'inputdir', action='store', type = str,
                        default = _default_inputdir, help = 'Directory into which ' +
                        'to store the NPR Fresh Air episodes. Default is %s.' %
                        _default_inputdir)
    parser.add_argument('--quiet', dest='do_verbose', action='store_false', default = True,
                        help = 'If chosen, do not print verbose output from the action of this ' +
                        'script. By default this is false.')
    args = parser.parse_args( )
    get_all_waitwaits_year( args.year, args.inputdir, verbose = args.do_verbose )
  
