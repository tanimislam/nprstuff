#!/usr/bin/env python3

import logging, datetime
from optparse import OptionParser
from core.waitwait import get_waitwait
from core.npr_utils import get_datestring, get_time_from_datestring

def _get_last_saturday(datetime_s):
    date_s = datetime_s.date( )

    # first find today's date
    tm_wday = date_s.weekday()
    if tm_wday < 5:
        tm_wday = tm_wday + 7
    days_go_back = tm_wday - 5
    date_sat = date_s - datetime.timedelta(days_go_back, 0, 0)
    return date_sat

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--dirname', dest='dirname', type=str,
                      action = 'store', default = '/mnt/media/waitwait',
                      help = 'Name of the directory to store the file. Default is %s.' %
                      '/mnt/media/waitwait')
    parser.add_option('--date', dest='date', type=str,
                      action = 'store', default = get_datestring(_get_last_saturday( datetime.datetime.now())),
                      help = 'The date, in the form of "January 1, 2014." The default is last Saturday, %s.' %
                      get_datestring( _get_last_saturday( datetime.datetime.now() ) ) )
    parser.add_option('--debugonly', dest='debugonly', action='store_true', default = False,
                      help = 'If chosen, download the NPR XML data sheet for this Wait Wait episode.')
    parser.add_option('--noverify', dest='do_noverify', action='store_true', default = False,
                      help = 'If chosen, Do not verify the SSL connection.')
    parser.add_option('--justfix', dest='do_justfix', action='store_true', default = False,
                      help = "If chosen, just fix the title of an existing NPR Wait Wait episode's file.")
    opts, args = parser.parse_args()
    if opts.debugonly: logging.basicConfig( level = logging.DEBUG )
    fname = get_waitwait( opts.dirname, get_time_from_datestring( opts.date ),
                          debugonly = opts.debugonly, verify = not opts.do_noverify,
                          justFix = opts.do_justfix )
