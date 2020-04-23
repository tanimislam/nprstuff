import requests, os, gzip, magic
from PIL import Image
from io import BytesIO
from PyQt4.QtSvg import QSvgRenderer
from PyQt4.QtCore import QByteArray
from PyPDF2 import PdfFileReader
from configparser import ConfigParser, RawConfigParser

def get_cloudconvert_api_key():
    resource = 'nprstuff'
    filename = '%s.conf' % resource
    baseConfDir = os.path.abspath(
      os.path.expanduser( '~/.config/%s' % resource ) )
    absPath = os.path.join( baseConfDir, filename )
    if not os.path.isfile( absPath ):
        raise ValueError("Error, default configuration file = %s does not exist." % absPath )
    cparser = ConfigParser( )
    cparser.read( absPath )
    if not cparser.has_section( 'CLOUDCONVERT_DATA' ):
        raise ValueError("Error, configuration file has not defined CLOUDCONVERT_DATA section.")
    if not cparser.has_option( 'CLOUDCONVERT_DATA', 'apikey' ):
        raise ValueError("Error, configuration file has not defined an apikey.")
    cloudconvert_api_key = cparser.get( "CLOUDCONVERT_DATA", "apikey" )
    return cloudconvert_api_key
        
def store_api_key(npr_API_key):
    resource = 'nprstuff'
    filename = '%s.conf' % resource
    baseConfDir = os.path.abspath(
      os.path.expanduser( '~/.config/%s' % resource ) )
    absPath = os.path.join( baseConfDir, filename )
    if os.path.isdir( absPath ):
        shutil.rmtree( absPath )
    if not os.path.isfile( absPath ):
        cparser = RawConfigParser( )
    else:
        cparser = ConfigParser( )
        cparser.read( absPath )
    #
    cparser.remove_section( 'NPR_DATA' )
    cparser.add_section('NPR_DATA')
    cparser.set('NPR_DATA', 'apikey', npr_API_key)
    with open( absPath, 'wb') as openfile:
        cparser.write( openfile )
    os.chmod( absPath, 0o600 )

def get_gif_video( input_mp4_file, verify = True ):
  assert( os.path.basename( input_mp4_file ).endswith( '.mp4' ) )
  assert( os.path.isfile( input_mp4_file ) )
  #
  ## assert this is an MP4 file
  assert( 'ISO Media, MPEG v4 system' in magic.from_file( input_mp4_file ) )
  #
  ## now convert MP4 into GIF, put into file
  apiKey = get_cloudconvert_api_key( )
  params = { 'apikey' : apiKey,
             'inputformat' : 'mp4',
             'outputformat': 'gif' }
  files = { 'file' : open( input_mp4_file, 'rb' ) }
  #
  response = requests.post( "https://api.cloudconvert.com/convert", params = params,
                            files = files, verify = verify )
  if response.status_code != 200:
    raise ValueError("Error, could not upload and convert MP4 file %s into animated GIF." % input_mp4_file )
  return Image.open( BytesIO( response.content ) )

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
    img = Image.open( BytesIO( response.content ) )
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
    img = Image.open( BytesIO( response.content ) )
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
    img = Image.open( BytesIO( response.content ) )
    return img
