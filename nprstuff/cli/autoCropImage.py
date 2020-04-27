import os, datetime, signal
from nprstuff import signal_handler
signal.signal( signal.SIGINT, signal_handler )
from nprstuff.core import autocrop_image
from argparse import ArgumentParser
from core import autocrop_image

def _main( ):
  parser = ArgumentParser( )
  parser.add_argument('--input', dest='input', action='store', type=str,
                      help = 'Name of the input file.', required = True )
  parser.add_argument('--output', dest='output', action='store', type=str,
                      help = 'Name of the output file. Optional.')
  parser.add_argument('--color', dest='color', action='store', type=str,
                      help = 'Name of the color over which to autocrop. Default is white.',
                      default = 'white' )
  parser.add_argument('--trans', dest='do_trans', action='store_true', default = False,
                      help = ' '.join([
                        'If chosen, also remove the transparency wrapping around the image.',
                        'Works only for non-PDF images.'  ]) )
  parser.add_argument('--newwidth', dest='newwidth', action='store', type=int,
                      help = 'New width of the image.' )
  parser.add_argument('--show', dest='do_show', action='store_true', default = False,
                      help = 'If chosen, then show the final image after cropped.' )
  args = parser.parse_args( )
  if args.input is None:
    raise ValueError("Error, input file path must be defined.")
  if not os.path.isfile(os.path.expanduser(args.input)):
    raise ValueError("Error, candidate file = %s is not a file." % os.path.expanduser(args.input))
  if not os.path.basename( args.input ).endswith('.pdf'):
    autocrop_image.autocrop_image( os.path.expanduser(args.input), outputfilename = args.output, color = args.color,
                                   newWidth = args.newwidth, doShow = args.do_show, trans = args.do_trans )
  else:
    if args.output is not None: assert( os.path.basename( args.output ).endswith('.pdf' ) )
    autocrop_image.crop_pdf_singlepage( os.path.expanduser( args.input ), outputfile = args.output )
