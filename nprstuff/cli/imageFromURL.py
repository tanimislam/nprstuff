import requests, os
from PIL import Image
from io import BytesIO
from argparse import ArgumentParser

def _image_from_url_to_png( url, filename = 'default.png' ):
  assert( os.path.basename( filename ).endswith( '.png' ) )
  img = Image.open( BytesIO( requests.get( url ).content ) )
  img.save( filename )

def _main( ):
  parser = ArgumentParser( )
  parser.add_argument('--url', dest='url', action='store', type=str,
                      help = 'URL where the image is located.', required = True )
  parser.add_argument('--filename', dest='filename', action='store', type=str, default = 'default.png',
                      help = ' '.join([ 'The name of the PNG file to save the online image.',
                                        'The image name must end in .png.',
                                        'The default name is default.png.' ] ) )
  args = parser.parse_args( )
  assert( args.url is not None )    
  _image_from_url_to_png( args.url, filename = args.filename )
