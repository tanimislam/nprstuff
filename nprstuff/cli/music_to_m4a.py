from argparse import ArgumentParser
from nprstuff.core.music_to_m4a import music_to_m4a, rename_m4a

def _main( ):
  parser = ArgumentParser( )
  parser.add_argument('--inputfile', dest='inputfile', type=str, action='store',
                      help = 'Name of the input audio file to convert.', required = True )
  parser.add_argument('--outfile', dest='outfile', type=str, action='store',
                      help = 'Optional name of the output file.')
  parser.add_argument('--tottracks', dest='tottracks', type=int, action='store',
                      help = 'Optional total number of tracks in album of which song is a part.')
  parser.add_argument('--albumloc', dest='albumloc', type=str, action='store',
                      help = 'Optional path to location of the album cover image file. Must be in JPEG or PNG.')
  parser.add_argument('--quiet', dest='quiet', action='store_true', default = False,
                      help = 'If chosen, then verbosely print output of processing.')
  parser.add_argument('--rename', dest='do_rename', action='store_true', default = False,
                      help = 'If chosen, simply rename the m4a file to the form <artist>.<song title>.m4a')
  parser.add_argument('--notitle', dest='do_notitle', action='store_true', default = False,
                      help = 'If chosen, do not use titlecase functionality to fix the titles of songs.')
  args = parser.parse_args()
  if args.inputfile is None:
    raise ValueError("Error, input file must be defined.")
  if args.outfile is not None and args.outfile.endswith('.m4a'):
    raise ValueError("Error, given output file = %s does not end in .m4a." % args.outfile)
  if args.tottracks is not None and args.tottracks <= 0:
    raise ValueError("Error, given total number of tracks = %d <= 0." % args.tottracks)
  verbose = not args.quiet
  
  if not args.do_rename:
    music_to_m4a( args.inputfile,
                  tottracks = args.tottracks,
                  album_path = args.albumloc,
                  outfile = args.outfile,
                  verbose = verbose,
                  toUpper = not args.do_notitle )
  else: rename_m4a( args.inputfile )
                  
