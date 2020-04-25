import requests, os, gzip, magic, uuid
from PIL import Image
from io import BytesIO
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QByteArray
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

def get_gif_video( input_mp4_file ):
  """
  This consists of voodoo FFmpeg_ magic that converts MP4 to animated GIF_ reasonably well. Don't ask me how most of it works, just be on-your-knees-kissing-the-dirt grateful that MILLIONS of people hack onto and into FFmpeg_ so that this information is available, and the workflow works.

  This requires a working ``ffmpeg`` and ``ffplay`` executable to work. If the input file is named ``<input>.mp4``, the output animated GIF file is named ``<input>.gif``.

  Here are resources that I used to get this working.

  * `Tutorial on high quality movie to animated GIF conversion <movie_2_gif_>`_. I hope this doesn't go away!

  * `Using FFPROBE to output JSON format <ffprobe_json_>`_
  
  :param str input_mp4_file: the name of the valid MP4 file.
  
  .. _FFmpeg: https://ffmpeg.org
  .. _GIF: https://en.wikipedia.org/wiki/GIF
  .. _movie_2_gif: http://blog.pkh.me/p/21-high-quality-gif-with-ffmpeg.html
  .. _ffprobe_json: https://tanimislamblog.wordpress.com/2018/09/12/ffprobe-to-get-output-in-json-format/
  """
  from distutils.spawn import find_executable
  ffmpeg_exec = find_executable( 'ffmpeg' )
  ffprobe_exec = find_executable( 'ffprobe' )
  assert(all(map(lambda tok: tok is not None, ( ffmpeg_exec, ffprobe_exec ))))
  assert( os.path.basename( input_mp4_file ).endswith( '.mp4' ) )
  assert( os.path.isfile( input_mp4_file ) )
  #
  ## assert this is an MP4 file
  assert( 'ISO Media,' in magic.from_file( input_mp4_file ) )
  #
  ## GIF output and PALETTE file
  giffile = args.mp4file.replace('.mp4', '.gif' )
  palettefile = '%s.png' % str( uuid.uuid4( ) )
  #
  ## get info JSON to get width, fps
  proc = subprocess.Popen(
    [ ffprobe_exec, '-v', 'quiet', '-show_streams',
      '-show_format', '-print_format', 'json', args.mp4file ],
    stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
  stdout_val, stderr_val = proc.communicate( )
  mp4file_info = json.loads( stdout_val )
  # from dictionary, get width
  width_of_mp4 = int( mp4file_info[ 'streams' ][ 0 ][ 'width' ] )
  fps_string = mp4file_info[ 'streams' ][ 0 ][ 'avg_frame_rate' ]
  fps = int( float( fps_string.split('/')[0] ) * 1.0 /
             float( fps_string.split('/')[1] ) )
  #
## now do the voodoo magic from resource #1
## step #1: create palette, run at fps
cmd = [
  ffmpeg_exec, '-y', '-v', 'warning', '-i', args.mp4file,
  '-vf', 'fps=%d,scale=%d:-1:flags=lanczos,palettegen' % ( fps, width_of_mp4 ),
  palettefile ]
proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
stdout_val, stderr_val = proc.communicate( )
assert( os.path.isfile( palettefile ) )
#
## step #2: take palette file, MP4 file, create animated GIF
cmd = [
  ffmpeg_exec, '-y', '-v', 'warning', '-i', args.mp4file,
  '-i', palettefile, '-lavfi', 'fps=%d,scale=%d:-1:flags=lanczos[x];[x][1:v]paletteuse' % (
    fps, width_of_mp4 ), giffile ]
proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
stdout_val, stderr_val = proc.communicate( )
#
## now batting cleanup
try: os.remove( palettefile )
except: pass

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
