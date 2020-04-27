import os, logging
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
  parser.add_argument('--info', dest='do_info', action = 'store_true', default = False,
                      help = 'If chosen, then do INFO logging.' )
  args = parser.parse_args( )
  logger = logging.getLogger( )
  if args.do_info: logger.setLevel( logging.INFO )
  direct = os.path.expanduser( args.directory )
  get_american_life(
    args.episode, directory=direct, extraStuff = args.extraStuff,
    verify = args.do_verify, dump = args.do_dump )
