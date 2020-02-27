#!/usr/bin/env python3

import requests, os, gzip
from PIL import Image
from io import StringIO
from argparse import ArgumentParser
from PyQt4.QtSvg import QSvgRenderer
from PyQt4.QtCore import QByteArray
from PyPDF2 import PdfFileReader
from core.npr_utils import get_cloudconvert_api_key

def get_png_image( input_svg_file, newWidth = None, verify = True ):
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
                              files = files, verify = verify )
    if response.status_code != 200:
        raise ValueError("Error, could not upload and convert SVG file %s." % input_svg_file )
    img = Image.open( StringIO( response.content ) )
    return img

def get_png_image_frompng( input_png_file, newWidth = None, verify = True ):
    assert( os.path.basename( input_png_file ).endswith( '.png' ) )
    assert( os.path.isfile( input_png_file ) )
    img = Image.open( input_png_file )
    width, height = img.size
    files = { 'file' : open( input_png_file, 'rb' ) }
    apiKey = get_cloudconvert_api_key( )
    params = { 'apikey' : apiKey,
               'input' : 'upload',
               'inputformat' : 'png',
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
                              files = files, verify = verify )
    if response.status_code != 200:
        raise ValueError("Error, could not upload and convert SVG file %s." % input_svg_file )
    img = Image.open( StringIO( response.content ) )
    return img

def get_png_image_frompdf( input_pdf_file, newWidth = None, verify = True ):
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
                              files = files, verify = verify )
    if response.status_code != 200:
        raise ValueError("Error, could not upload and convert PDF file %s." % input_pdf_file )
    img = Image.open( StringIO( response.content ) )
    return img
    
if __name__=='__main__':
    parser = ArgumentParser( )
    parser.add_argument('--filename', dest='filename', type=str, action='store',
                        help = 'Name of the input SVG file.', required = True )
    parser.add_argument('--width', dest='width', type=int, action='store',
                        help = 'If defined, new width of the file. Optional')
    parser.add_argument('--pdf', dest='do_pdf', action='store_true', default = False,
                        help = 'If chosen, convert a PDF, instead of SVG(Z), file into PNG.')
    parser.add_argument('--png', dest='do_png', action='store_true', default = False,
                        help = 'If chosen, convert a PNG, instead of SVG(Z), file into a new PNG.')
    parser.add_argument('--noverify', dest='do_noverify', action='store_true', default = False,
                        help = 'If chosen, do not verify the SSL connection.')
    args = parser.parse_args( )
    assert( args.filename is not None )
    assert(len(filter(lambda tok: tok is True, ( args.do_png, args.do_pdf ) ) ) <= 1 )
    #
    ##
    if args.do_pdf:
        img = get_png_image_frompdf( args.filename, newWidth = args.width, verify = not args.do_noverify )
        imgFile = os.path.basename( args.filename ).replace('.pdf', '.png' )
    elif args.do_png:
        img = get_png_image_frompng( args.filename, newWidth = args.width, verify = not args.do_noverify )
        imgFile = os.path.basename( args.filename ).replace( '.png', '_new.png' )
    else:
        img = get_png_image( args.filename, newWidth = args.width, verify = not args.do_noverify )        
        imgFile = os.path.basename( args.filename ).replace('.svgz', '.png' ).replace('.svg', '.png')
    dirName = os.path.dirname( os.path.abspath( args.filename ) )  
    img.save( os.path.join( dirName, imgFile ) )
