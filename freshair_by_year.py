#!/usr/bin/env python3

import signal, datetime
from core import signal_handler
signal.signal( signal.SIGINT, signal_handler )
from argparse import ArgumentParser
from core import freshair, freshair_by_year

_default_inputdir = '/mnt/media/freshair'

if __name__=='__main__':
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
