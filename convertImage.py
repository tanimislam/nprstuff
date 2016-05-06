#!/usr/bin/env python

import requests, os, gzip
from npr_utils import get_cloudconvert_api_key
from PIL import Image
from cStringIO import StringIO
from optparse import OptionParser
from PyQt4.QtSvg import QSvgRenderer
from PyQt4.QtCore import QByteArray
from PyPDF2 import PdfFileReader

def get_png_image( input_svg_file, newWidth = None ):
    assert( os.path.basename( input_svg_file ).endswith( '.svg' ) or
            os.path.basename( input_svg_file ).endswith( '.svgz') )
    assert( os.path.isfile( input_svg_file ) )
    if os.path.basename( input_svg_file ).endswith( '.svgz' ):
        r = QSvgRenderer( QByteArray( gzip.open( input_svg_file, 'rb' ).read( ) ) )
        files = { 'file' : gzip.open( input_svg_file, 'rb' ) }
    else:
        r = QSvgRenderer( input_svg_file )
        files = { 'file' : open( input_svg_file, 'rb' ) }
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
                              files = files, verify = False )
    if response.status_code != 200:
        raise ValueError("Error, could not upload and convert SVG file %s." % input_svg_file )
    img = Image.open( StringIO( response.content ) )
    return img

def get_png_image_frompdf( input_pdf_file, newWidth = None ):
    assert( os.path.basename( input_pdf_file ).endswith( '.pdf' ) )
    assert( os.path.isfile( input_pdf_file ) )
    ipdf = PdfFileReader( open( input_pdf_file, 'rb' ) )
    assert( ipdf.getNumPages() == 1 )
    mbox = ipdf.getPage( 0 ).mediaBox
    files = { 'file' : open( input_pdf_file, 'rb' ) }
    width = int( mbox.getWidth( ) )
    height = int( mbox.getHeight( ) )
    apiKey = get_cloudconvert_api_key( )
    params = { 'apikey' : apiKey,
               'input' : 'upload',
               'inputformat' : 'pdf',
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
                              files = files, verify = False )
    if response.status_code != 200:
        raise ValueError("Error, could not upload and convert PDF file %s." % input_pdf_file )
    img = Image.open( StringIO( response.content ) )
    return img
    
if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--filename', dest='filename', type=str, action='store',
                      help = 'Name of the input SVG file.')
    parser.add_option('--width', dest='width', type=int, action='store',
                      help = 'If defined, new width of the file. Optional')
    parser.add_option('--pdf', dest='do_pdf', action='store_true', default = False,
                      help = 'If chosen, convert a PDF, instead of SVG(Z), file into PNG.')
    opts, args = parser.parse_args()
    assert( opts.filename is not None )
    #
    ##
    if not opts.do_pdf:
        img = get_png_image( opts.filename, newWidth = opts.width )        
        imgFile = os.path.basename( opts.filename ).replace('.svgz', '.png' ).replace('.svg', '.png')
    else:
        img = get_png_image_frompdf( opts.filename, newWidth = opts.width )
        imgFile = os.path.basename( opts.filename ).replace('.pdf', '.png' )
    dirName = os.path.dirname( os.path.abspath( opts.filename ) )  
    img.save( os.path.join( dirName, imgFile ) )
