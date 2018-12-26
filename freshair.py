#!/usr/bin/env python3

from core import signal_handler
import os, datetime, signal
signal.signal( signal.SIGINT, signal_handler )
from optparse import OptionParser
from core.freshair import get_freshair
from core.npr_utils import get_datestring, get_time_from_datestring

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--dirname', dest='dirname', type=str,
                      action = 'store', default = '/mnt/media/freshair',
                      help = 'Name of the directory to store the file. Default is %s.' %
                      '/mnt/media/freshair')
    parser.add_option('--date', dest='date', type=str,
                      action = 'store', default = get_datestring( datetime.datetime.now()),
                      help = 'The date, in the form of "January 1, 2014." The default is today\'s date, %s.' %
                      get_datestring( datetime.datetime.now() ) )
    parser.add_option('--mp3exist', dest='mp3_exist', action='store_true', default = False,
                      help = 'If chosen, then do not download the transitional mp3 files. Use the ones that'+
                      ' already exist.')
    parser.add_option('--debug', dest='debug', action='store_true',
                      help = 'If chosen, run freshair.py in debug mode. Useful for debugging :)',
                      default = False)
    opts, args = parser.parse_args()
    dirname = os.path.expanduser( opts.dirname )
    fname = get_freshair( dirname, get_time_from_datestring( opts.date ),
                          debug = opts.debug, mp3_exist = opts.mp3_exist )
