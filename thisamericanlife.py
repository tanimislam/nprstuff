#!/usr/bin/env python3

import os
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
    parser.add_option('--noverify', dest = 'do_noverify', action = 'store_true', default = False,
                      help = 'If chosen, then do not verify the SSL connection.')
    options, args = parser.parse_args()
    direct = os.path.expanduser( options.directory )
    get_american_life(options.episode, directory=direct, extraStuff = options.extraStuff,
                      verify = not options.do_noverify )
