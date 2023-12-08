import requests, os, gzip, magic, uuid, pathlib, glob, time
import subprocess, json, yt_dlp, logging, re, numpy
from PIL import Image
from io import BytesIO
from PyPDF2 import PdfFileReader
from ive_tanim.core.convert_image import mp4togif

def get_cloudconvert_api_key( ):
    """
    :returns: the CloudConvert_ API key, stored in ``~/.config/nprstuff/nprstuff.conf``, under the ``CLOUDCONVERT_DATA`` section and ``apikey`` key.
    
    .. _CloudConvert: https://cloudconvert.com
    """
    from configparser import ConfigParser, RawConfigParser
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

def get_youtube_file( youtube_URL, output_file, quality = 'highest', verify = True ):
    """
    Uses `yt-dlp`_ programmatically to download into an MP4_ or MKV_ file.

    :param str youtube_URL: a valid YouTube_ URL for the song clip.
    :param str output_file: the MP4_ or MKV_ video file name.
    :param str quality: the quality level of the MP4 video to download. Default is "highest." Can be one of "highest", "high", "medium", "low".
    :param bool verify: if ``False``, then do not verify the SSL connection to YouTube_. Default is ``True``.

    :returns: ``True`` if successful, otherwise ``False``.
    :rtype: bool

    .. _`yt-dlp`: https://github.com/yt-dlp/yt-dlp
    .. _YouTube: https://www.youtube.com
    .. _MP4: https://en.wikipedia.org/wiki/MPEG-4_Part_14
    .. _MKV: //en.wikipedia.org/wiki/Matroska
    """
    assert( any(map(lambda suffix: os.path.basename( output_file ).endswith( '.%s' % suffix ),
                    ( 'mkv', 'mp4' ) ) ) )
    assert( quality in ( 'highest', 'high', 'medium', 'low' ) )
    qualmap = { 'highest' : '18', 'high' : '134', 'medium' : '133', 'low' : '160' }
    logging.info( 'URL: %s, output_file: %s.' % (
        youtube_URL, output_file ) )
    try:
        ydl_opts = {
            'format' : qualmap[ quality ], # try highest quality MP4 OR MKV?? DOES IT WORK??
            'outtmpl' : output_file }
        if not verify: ydl_opts[ 'nocheckcertificate' ] = True
        with yt_dlp.YoutubeDL( ydl_opts ) as ydl:
            ydl.download([ youtube_URL ])
            return True
    except yt_dlp.DownloadError: # could not download the file to MP4 OR MKV format
        logging.info( "ERROR, CANNOT DOWNLOAD %s INTO MP4 OR MKV FILE. MY BAD (FOR NOW)." %
                     youtube_URL )
        return False

def youtube2gif( input_youtube_URL, gif_file, quality = 'highest', duration = None, scale = 1.0, verify = True ):
    """
    Converts a YouTube_ clip into an animated GIF_ file. First, downloads the YouTube_ clip into an intermediate MP4_ file; then converts the intermediate MP4_ file into the animated GIF_, and deletes the intermediate file.

    :param str input_youtube_URL: the input valid YouTube clip's URL.
    :param str gif_file: the output GIF_ file.
    :param str quality: optional argument for the quality of the YouTube clip. Default is "highest".
    :param float duration: duration, in seconds, of input clip to use to make the animated GIF_. If ``None`` is provided, use the full movie. If provided, then must be :math:`\ge 1` seconds.
    :param float scale: scaling of input width and height of MP4_ file. Default is 1.0. Must be :math:`\ge 0`.
    :param bool verify: if ``False``, then do not verify the SSL connection to YouTube_. Default is ``True``.

    .. seealso::

       * :py:meth:`mp4togif <ive_tanim.core.convert_image.mp4togif>`.
       * :py:meth:`get_youtube_file <nprstuff.core.convert_image_youtube.get_youtube_file>`.
    """
    intermediate_file = '%s.mp4' % str( uuid.uuid4( ) )
    status = get_youtube_file(
        input_youtube_URL, intermediate_file, quality = quality, verify = verify )
    if not status:
        intermediate_file = '%s.mkv' % str( uuid.uuid4( ) )
        status = get_youtube_file(
            input_youtube_URL, intermediate_file, quality = quality )
    if not status:
        logging.error( "ERROR, COULD NOT DOWNLOAD YOUTUBE URL: %s." % input_youtube_URL )
        try: os.remove( intermediate_mp4_file )
        except: pass
        return
    #
    ## now to gif
    mp4togif( intermediate_file, gif_file, duration = duration, scale = scale )
    try: os.remove( intermediate_file )
    except: pass

def _return_image_cc( width, height, inputFileName, form, files,
                      newWidth = None, verify = True ):
    assert( form in ( 'svg', 'png', 'pdf' ) )
    params = { 'apikey' : get_cloudconvert_api_key( ),
              'input' : 'upload',
              'inputformat' : form,
              'outputformat' : 'png',             
    }
    if newWidth is not None:
        assert( isinstance( newWidth, int ) )
        assert( newWidth > 10 )
        newHeight = int( height * 1.0 * newWidth / width )
        params['converteroptions[resize]'] = '%dx%d' % ( newWidth, newHeight )
    #
    ##    
    response = requests.post(
        "https://api.cloudconvert.com/convert", params = params,
        files = files, verify = verify )
    if response.status_code != 200:
        raise ValueError("Error, could not upload and convert file %s." % inputFileName )
    return Image.open( BytesIO( response.content ) )

def svg2png( input_svg_file, newWidth = None, verify = True ):
    """
    Returns an :py:class:`Image <PIL.Image.Image>` object of the PNG_ file produced when the CloudConvert_ server uploaded an input `SVG(Z) <svg_>`_ file. The PNG_ file has the same aspect ratio as the input file. Uses :py:class:`QSvgRenderer <PyQt5.QtSvg.QSvgRenderer>` to convert an `SVG(Z) <svg_>`_ into a PNG_.

    :param str input_svg_file: the input SVG or SVGZ file. Filename must end in ``.svg`` or ``.svgz``.
    :param int newWidth: optional argument. If specified, the pixel width of the output image.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    
    :returns: the :py:class:`Image <PIL.Image.Image>` object of the PNG_ file from the input SVG or SVGZ file.
    
    .. _PNG: https://en.wikipedia.org/wiki/Portable_Network_Graphics
    .. _svg: https://en.wikipedia.org/wiki/Scalable_Vector_Graphics

    
    .. seealso::
    
        * :py:meth:`png2png <nprstuff.core.convert_image_youtube.png2png>`.
        * :py:meth:`pdf2png <nprstuff.core.convert_image_youtube.pdf2png>`.
    """
    
    try:
        from PyQt5.QtSvg import QSvgRenderer
        from PyQt5.QtCore import QByteArray
    except:
        logging.error( "ERROR, MUST INSTALL PyQt5.QtSvg MODULE. IT DOES NOT EXIST ON PYPI RIGHT NOW. YOU CAN RUN THE COMMAND, 'sudo apt install python3-pyqt5.qtsvg', TO INSTALL MODULE." )
        sys.exit( 0 )
    
    assert(any(map(lambda suffix: os.path.basename( input_svg_file ).endswith( '.%s' % suffix ),
                   ( 'svg', 'svgz' ) ) ) )
    assert( os.path.isfile( input_svg_file ) )
    if os.path.basename( input_svg_file ).endswith( '.svgz' ):
        r = QSvgRenderer( QByteArray( gzip.open( input_svg_file, 'rb' ).read( ) ) )
        files = { 'file' : gzip.open( input_svg_file, 'rb' ).read( ) }
    else:
        r = QSvgRenderer( input_svg_file )
        files = { 'file' : open( input_svg_file, 'rb' ).read( ) }
    width = r.defaultSize().width()
    height = r.defaultSize().height()
    return _return_image_cc(
        width, height, input_svg_file, 'svg', files,
        newWidth = newWidth, verify = verify )

def png2png( input_png_file, newWidth = None, verify = True ):
    """
    Returns an :py:class:`Image <PIL.Image.Image>` object of the PNG_ file produced when the CloudConvert_ server uploaded an input PNG_ file. The output PNG_ file has the same aspect ratio as the input file.

    :param str input_png_file: the input PNG_ file. Filename must end in ``.png``.
    :param int newWidth: optional argument. If specified, the pixel width of the output image.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    
    :returns: the :py:class:`Image <PIL.Image.Image>` object of the PNG_ file from the input PNG_ file.

    
    .. seealso::

        * :py:meth:`svg2png <nprstuff.core.convert_image_youtube.svg2png>`.
        * :py:meth:`pdf2png <nprstuff.core.convert_image_youtube.pdf2png>`.
    """
    assert( os.path.basename( input_png_file ).endswith( '.png' ) )
    assert( os.path.isfile( input_png_file ) )
    width, height = Image.open( input_png_file ).size
    files = { 'file' : open( input_png_file, 'rb' ).read( ) }
    return _return_image_cc(
        width, height, input_png_file, 'png', files, params.copy( ),
        newWidth = newWidth, verify = verify )

def pdf2png( input_pdf_file, newWidth = None, verify = True ):
    """
    Returns an :py:class:`Image <PIL.Image.Image>` object of the PNG_ file produced when the CloudConvert_ server uploaded an input PDF_ image file. The output PNG_ file has the same aspect ratio as the input file.

    :param str input_png_file: the input PNG_ file. Filename must end in ``.png``.
    :param int newWidth: optional argument. If specified, the pixel width of the output image.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    
    :returns: the :py:class:`Image <PIL.Image.Image>` object of the PNG_ file from the input PNG_ file.

    .. _PDF: https://en.wikipedia.org/wiki/PDF

    .. seealso::

        * :py:meth:`svg2png <nprstuff.core.convert_image_youtube.svg2png>`.
        * :py:meth:`png2png <nprstuff.core.convert_image_youtube.png2png>`.
    """
    assert( os.path.basename( input_pdf_file ).endswith( '.pdf' ) )
    assert( os.path.isfile( input_pdf_file ) )
    ipdf = PdfFileReader( open( input_pdf_file, 'rb' ) )
    assert( ipdf.getNumPages() == 1 )
    mbox = ipdf.getPage( 0 ).mediaBox
    files = { 'file' : open( input_pdf_file, 'rb' ).read( ) }
    width = int( mbox.getWidth( ) )
    height = int( mbox.getHeight( ) )
    return _return_image_cc(
        width, height, input_pdf_file, 'pdf', files,
        newWidth = newWidth, verify = verify )
