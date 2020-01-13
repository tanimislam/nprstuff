#!/usr/bin/env python3

import os, logging
from optparse import OptionParser
from core.thisamericanlife import get_american_life

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--episode', dest='episode', type=int, action='store', default = 150,
                      help = 'Episode number of This American Life to download. Default is 150.')
    parser.add_option('--directory', dest='directory', type=str, action='store',
                      default = '/mnt/media/thisamericanlife',
                      help = 'Directory into which to download This American Life episodes. Default is %s.' %
                      '/mnt/media/thisamericanlife')
    parser.add_option('--extra', dest='extraStuff', type=str, action='store',
                      help = 'If defined, some extra stuff in the URL to get a This American Life episode.')
    parser.add_option('--noverify', dest = 'do_verify', action = 'store_false', default = True,
                      help = 'If chosen, then do not verify the SSL connection.')
    parser.add_option('--dump', dest='do_dump', action = 'store_true', default = False,
                      help = 'If chosen, just download the TAL episode XML into a file into the specified directory.')
    parser.add_option('--info', dest='do_info', action = 'store_true', default = False,
                      help = 'If chosen, then do INFO logging.' )
    options, args = parser.parse_args()
    logger = logging.getLogger( )
    if options.do_info: logger.setLevel( logging.INFO )
    direct = os.path.expanduser( options.directory )
    get_american_life(options.episode, directory=direct, extraStuff = options.extraStuff,
                      verify = options.do_verify, dump = options.do_dump )
