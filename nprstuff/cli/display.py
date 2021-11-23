from PIL import Image
import sys

def _main( ):
  if len( sys.argv ) < 2:
    print( 'Error, syntax is display.py <imagefile>' )
    sys.exit(0)
  try:
    img = Image.open( sys.argv[1] )
    img.show( )
  except:
    print( 'Error, could not open %s' % sys.argv[1] )
    sys.exit( 0 )
