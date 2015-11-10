#!/usr/bin/env python

import requests, os
from npr_utils import get_cloudconvert_api_key
from PIL import Image
from cStringIO import StringIO
from optparse import OptionParser
from PyQt4.QtSvg import QSvgRenderer

def get_png_image( input_svg_file, newWidth = None ):
    assert( os.path.basename( input_svg_file ).endswith( '.svg' ) )
    assert( os.path.isfile( input_svg_file ) )
    r = QSvgRenderer( input_svg_file )
    width = r.defaultSize().width()
    height = r.defaultSize().height()
    apiKey = get_cloudconvert_api_key( )
    params = { 'apikey' : apiKey,
               'input' : 'upload',
               'inputformat' : 'svg',
               'outputformat' : 'png',
               }
    
    if newWidth is not None:
        assert( isinstance( newWidth, int ) )
        assert( newWidth > 10 )
        newHeight = int( height * 1.0 * newWidth / width )
        params['converteroptions[resize]'] = '%dx%d' % ( newWidth, newHeight )
    #
    ##
    response = requests.post( "https://api.cloudconvert.com/convert", params = params,
                              files = { 'file' : open( input_svg_file, 'rb' ) } )
    if response.status_code != 200:
        raise ValueError("Error, could not upload and convert SVG file %s." % input_svg_file )
    img = Image.open( StringIO( response.content ) )
    return img

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--filename', dest='filename', type=str, action='store',
                      help = 'Name of the input SVG file.')
    parser.add_option('--width', dest='width', type=int, action='store',
                      help = 'If defined, new width of the file. Optional')
    opts, args = parser.parse_args()
    assert( opts.filename is not None )
    #
    ##
    img = get_png_image( opts.filename, newWidth = opts.width )
    dirName = os.path.dirname( os.path.abspath( opts.filename ) )
    pngFile = os.path.basename( opts.filename ).replace('.svg', '.png' )
    img.save( os.path.join( dirName, pngFile ) )
