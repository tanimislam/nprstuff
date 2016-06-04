#!/usr/bin/env python

import requests, os
from PIL import Image
from cStringIO import StringIO
from optparse import OptionParser

def image_from_url_to_png( url, filename = 'default.png' ):
    assert( os.path.basename( filename ).endswith( '.png' ) )
    img = Image.open( StringIO( requests.get( url ).content ) )
    img.save( filename )

if __name__=='__main__':
    parser = OptionParser( )
    parser.add_option('--url', dest='url', action='store', type=str,
                      help = 'URL where the image is located.')
    parser.add_option('--filename', dest='filename', action='store', type=str, default = 'default.png',
                      help = ' '.join([ 'The name of the PNG file to save the online image.',
                                        'The image name must end in .png.',
                                        'The default name is default.png.' ] ) )
    opts, args = parser.parse_args( )
    assert( opts.url is not None )    
    image_from_url_to_png( opts.url, filename = opts.filename )
