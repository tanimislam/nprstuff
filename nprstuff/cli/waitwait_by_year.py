#!/usr/bin/env python3

import signal
from core import signal_handler
signal.signal( signal.SIGINT, signal_handler )
from argparse import ArgumentParser
from core.waitwait import get_all_waitwaits_year

_default_inputdir = '/mnt/media/waitwait'
_default_year = 2010

if __name__=='__main__':
    parser = ArgumentParser( )
    parser.add_argument('--year', dest='year', action='store', type=int, default = _default_year,
                        help = 'Year in which to write out all Fresh Air episodes. Default is %d.' %
                        _default_year )
    parser.add_argument('--inputdir', dest = 'inputdir', action='store', type = str,
                        default = _default_inputdir, help = 'Directory into which ' +
                        'to store the NPR Fresh Air episodes. Default is %s.' %
                        _default_inputdir)
    parser.add_argument('--quiet', dest='is_quiet', action='store_true', default = False,
                        help = 'If chosen, do not print verbose output from the action of this ' +
                        'script. By default this is false.')
    args = parser.parse_args( )
    verbose = not args.is_quiet
    get_all_waitwaits_year( args.year, args.inputdir, verbose = verbose )                            