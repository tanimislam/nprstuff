import os, logging
from nprstuff import logging_dict, nprstuff_logger as logger
from nprstuff.core.thisamericanlife import get_american_life
from argparse import ArgumentParser

_default_inputdir = '/mnt/media/thisamericanlife'

def _main( ):
    parser = ArgumentParser( )
    parser.add_argument( '--episode', dest='episode', type=int, action='store', default = 150,
                        help = 'Episode number of This American Life to download. Default is 150.' )
    parser.add_argument( '--directory', dest='directory', type=str, action='store',
                        default = _default_inputdir,
                        help = 'Directory into which to download This American Life episodes. Default is %s.' %
                        _default_inputdir )
    parser.add_argument('--extra', dest='extraStuff', type=str, action='store',
                        help = 'If defined, some extra stuff in the URL to get a This American Life episode.')
    parser.add_argument('--noverify', dest = 'do_verify', action = 'store_false', default = True,
                        help = 'If chosen, then do not verify the SSL connection.')
    parser.add_argument('--dump', dest='do_dump', action = 'store_true', default = False,
                        help = 'If chosen, just download the TAL episode XML into a file into the specified directory.')
    parser.add_argument('--level', dest='level', action='store', type=str, default = 'NONE',
                        choices = sorted( logging_dict ),
                        help = 'choose the debug level for downloading NPR Fresh Air episodes or their XML representation of episode info. Can be one of %s. Default is NONE.' % sorted( logging_dict ) )
    parser.add_argument('--hardURL', dest='hardURL', action='store', type=str,
                        help = 'If you specify the episode AND IT DOESNT WORK, maybe giving the explicit URL will get you out of this jam.' )
    args = parser.parse_args( )
    logger.setLevel( logging_dict[ args.level ] )
    direct = os.path.expanduser( args.directory )
    get_american_life(
        args.episode, directory=direct, extraStuff = args.extraStuff,
        verify = args.do_verify, dump = args.do_dump, hardURL = args.hardURL )
