import requests, os, gzip, magic, uuid, pathlib, glob, time
import subprocess, json, youtube_dl, logging, re, numpy
from pathos.multiprocessing import Pool, cpu_count
from distutils.spawn import find_executable
from PIL import Image
from io import BytesIO
from PyPDF2 import PdfFileReader
from configparser import ConfigParser, RawConfigParser
from PyQt5.QtCore import QByteArray
from nprstuff.core import autocrop_image

def mp4frompngs( png2mp4dict ):
    """
    Creates an MP4_ file from the low-level input specification :py:class:`dict` that :py:meth:`create_png2mp4dict <nprstuff.core.convert_image.create_png2mp4dict>` creates. Requires the existence of the ``ffmpeg`` executable, and ``status`` value in the :py:class:`dict` *must* be ``"SUCCESS"``. Otherwise, this method does not create a movie file.

    If ``dirname`` is the directory in which the PNG_ files live, and ``PREFIX`` is the prefix of all the PNG_ files, the MP4_ file is named ``dirname/PREFIX.mp4``.

    :param dict png2mp4dict: the dictionary specification for creating a specific MP4_ file from a collection of PNG_ files as frames.

    .. seealso:: :py:meth:`create_png2mp4dict <nprstuff.core.convert_image.create_png2mp4dict>`.
    """
    #
    ## barf out if cannot find ffmpeg
    ffmpeg_exec = find_executable( 'ffmpeg' )
    if ffmpeg_exec is None:
        raise ValueError("Error, ffmpeg could not be found." )
    assert( png2mp4dict['status'] == 'SUCCESS' )
    def _resize_image( fname ):
        im = Image.open( fname )
        sizeChanged = False
        newWidth, newHeight = im.size
        if newWidth % 2 != 0:
            newWidth += 1
            sizeChanged = True
        if newHeight % 2 != 0:
            newHeight += 1
            sizeChanged = True
        if sizeChanged:
            im = im.resize(( newWidth, newHeight ))
            im.save( fname )
    #
    ## now ensure that these files are of even-width-and-height
    with Pool( processes = cpu_count( ) ) as pool:
        time0 = time.time( )
        autocrop = png2mp4dict[ 'autocrop' ]
        if not autocrop:
            _ = list(pool.map(_resize_image, png2mp4dict['files'] ) )
        else:
            _ = list(pool.map(lambda fname: autocrop_image.autocrop_image( fname, fixEven = True ),
                              png2mp4dict['files']))
        logging.info('fixed widths and heights of %d images in %0.3f seconds.' % (
            len( png2mp4dict['files'] ), time.time( ) - time0 ) )
    #
    ## now create the FFMPEG movie file
    ## thank instructions from https://hamelot.io/visualization/using-ffmpeg-to-convert-a-set-of-images-into-a-video/
    ## make MP4 movie, 5 fps, quality = 25
    time0 = time.time( )
    num_dots = len( png2mp4dict['prefix'].split('.')[:-1] ) - 1
    if num_dots == 0:
        movie_name = '%s.mp4' % png2mp4dict['prefix']
    else:
        movie_name = '%s.mp4' % '.'.join(png2mp4dict['prefix'].split('.')[:-1])
    stdout_val = subprocess.check_output(
        [ ffmpeg_exec, '-y', '-r', '%d' % png2mp4dict['fps'], '-f', 'image2',
         '-i', png2mp4dict['actual prefix'],
         '-vcodec', 'libx264', '-crf', '25', '-pix_fmt', 'yuv420p', movie_name ],
        stderr = subprocess.STDOUT )        
    logging.info('created movie = %s from %d PNG frame images in %0.3f seconds.' % (
        movie_name, len( png2mp4dict['files'] ), time.time( ) - time0 ) )
    
def create_png2mp4dict( prefix, dirname = os.getcwd( ), fps = 5, autocrop = False ):
    """
    This method creates a complicated and low-level :py:class:`dict` of set up, when creating an MP4_ file from a collection of PNG_\ s. Here are things needed to make this work. :py:meth:`mp4frompngs <nprstuff.core.convert_image.mp4frompngs>` uses this :py:class:`dict` to create the MP4_ file.

    #. The collection of PNG_ files exist in a directory named ``dirname``.

    #. The format of the PNG_ files as frames of a movie must have a name like ``PREFIX0000.png`` to ``PREFIX0401.png``.

    #. The first PNG_ file must have a zero-padded value of zero. There must also be *no* number gaps in the sequence of PNG_ files as frames. For example, if there are PNG_ files ``PREFIX0200.png`` and ``PREFIX0202.png`` but *no* ``PREFIX0201.png``, this process will fail.
    
    In case of success, this method returns a :py:class:`dict` with these five keys and values.

    * ``status``: the :py:class:`string <str>` ``"SUCCESS"``.
    * ``files``: the sorted :py:class:`list` of PNG_ file names as movie frames.
    * ``autocrop``: :py:class:`bool` on whether to autocrop the PNG_ files.
    * ``fps``: the :py:class:`int` number of frames per second in the MP4_ file.
    * ``actual prefix``: the input (``ffmpeg -i <arg>``) argument that goes into FFmpeg_ when creating the MP4_ from a collection of PNG_ files as frames.

    In case of failure, the ``status`` key contains the reason for the failure. :py:meth:`mp4frompngs <nprstuff.core.convert_image.mp4frompngs>` returns this failure message and does nothing.

    :param str prefix: the base name of each PNG_ file as frame, before the integer frame number and ``.png`` suffix.
    :param str dirname: the directory in which these PNG_ files live. Default is the current working directory.
    :param int fps: the number of frames per seconds for the movie. Must be :math:`\ge 1`.
    :param bool autocrop: whether to automatically crop out white space in the PNG_ files as frames. Default is ``False``.
    :returns: the :py:class:`dict` described above.
    :rtype: dict

    .. seealso:: :py:meth:`mp4frompngs <nprstuff.core.convert_image.mp4frompngs>`.

    .. FFmpeg_: https://ffmpeg.org
    """
    png2mp4dict = { }
    if fps < 1:
        png2mp4dict['status'] = 'Error, fps = %d is less than 1.' % fps
        return png2mp4dict
    png2mp4dict['fps'] = fps
    png2mp4dict['autocrop'] = autocrop
    #
    ## check that it is a dirname
    if not os.path.isdir( dirname ):
        png2mp4dict['status'] = 'Error, %s is not a directory.' % dirname
        return png2mp4dict
    #
    ## now see if PNG files with prefix
    collection_of_png_files = list(filter(os.path.isfile, glob.glob( os.path.join( dirname, '%s*.png' % prefix ) ) ) )
    if not collection_of_png_files:
        png2mp4dict['status'] = 'Error, no PNG files with prefix = %s found in %s.' % (
            prefix, dirname )
        return mpg2mp4dict
    #
    ## now only those collection of png files that have number suffix
    def _is_numbered_prop( fname ):
        bname = os.path.basename( fname )
        bname = bname.replace( prefix, '' ).strip( )
        bname = re.sub('\.png$', '', bname ).strip( )
        try:
            val = int( bname )
            return True, val, bname
        except:
            return False, None, bname
    collection_files_valid = sorted(filter(lambda fname: _is_numbered_prop(fname)[0], collection_of_png_files ) )
    sorted_numbers_dict = dict(map(lambda fname: ( _is_numbered_prop( fname )[1], fname ), collection_files_valid ) )
    zero_padded_nums = set(map(lambda fname: _is_numbered_prop( fname )[2], collection_files_valid))
    min_zero_padding = min(map(lambda zpn: len(zpn) - len(zpn.lstrip('0')), zero_padded_nums))
    if not sorted_numbers_dict:
        png2mp4dict['status'] = 'Error, no PNG files with prefix = %s AND PROPER NUMBERING found in %s.' % (
            prefix, dirname )
        return png2mp4dict
    #
    ## now check that the numbers are all ordered from 0 to SOME MAX NUMBER
    set_numbers = set(sorted_numbers_dict)
    should_be_sorted = set(range(len(sorted_numbers_dict)))
    if should_be_sorted != set_numbers:
        numbers_missing = sorted((set_numbers - should_be_sorted) | (should_be_sorted - set_numbers))
        png2mp4dict['status'] = 'Error, XOR operations found these %d numbers mismatched between what SHOULD be there, and what is: %s.' % ( len( numbers_missing ), numbers_missing )
        return png2mp4dict
    #
    ## success?
    png2mp4dict['prefix'] = prefix
    png2mp4dict['files'] = sorted( sorted_numbers_dict.values( ) )
    num_digits = int(numpy.log10(len(set_numbers)-1)) + 1 + min_zero_padding
    png2mp4dict['actual prefix'] = os.path.join( dirname, '%s%%0%dd.png' % ( prefix, num_digits ) ) # prefix to ffmpeg for images
    png2mp4dict['status'] = 'SUCCESS'
    return png2mp4dict

def get_cloudconvert_api_key( ):
    """
    :returns: the CloudConvert_ API key, stored in ``~/.config/nprstuff/nprstuff.conf``, under the ``CLOUDCONVERT_DATA`` section and ``apikey`` key.
    
    .. _CloudConvert: https://cloudconvert.com
    """
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

def make_square_mp4video( input_mp4_file, output_mp4_file ):
    """
    More FFmpeg_ voodoo, this time to create a square MP4_ file for upload into Instagram_.

    This requires a working ``ffmpeg`` and ``ffprobe`` executable to work. The input file must be MP4_.

    Here are resources that I used to get this working.

    * `Padding movie file with FFmpeg <padding_movie_>`_.

    * `Using FFPROBE to output JSON format <ffprobe_json_>`_.

    :param str input_mp4_file: the name of the valid input MP4_ file.
    :param str output_mp4_file: the name of the valid output MP4_ file.

    .. seealso:: :py:meth:`get_gif_video <nprstuff.core.convert_image.get_gif_video>`.

    .. _FFmpeg: https://ffmpeg.org
    .. _MP4: https://en.wikipedia.org/wiki/MPEG-4_Part_14
    .. _MKV: https://en.wikipedia.org/wiki/Matroska
    .. _Instagram: https://www.instagram.com
    .. _padding_movie: https://superuser.com/questions/1212106/add-border-to-video-ffmpeg
    .. _ffprobe_json: https://tanimislam.github.io/blog/ffprobe-to-get-output-in-json-format.html
    """
    from distutils.spawn import find_executable
    import shutil
    ffmpeg_exec = find_executable( 'ffmpeg' )
    ffprobe_exec = find_executable( 'ffprobe' )
    assert(all(map(lambda tok: tok is not None, ( ffmpeg_exec, ffprobe_exec ))))
    assert( os.path.basename( input_mp4_file ).endswith( '.mp4' ) )
    assert( os.path.isfile( input_mp4_file ) )
    #
    ## assert this is an MP4 file, and output ends in .mp4
    assert( 'ISO Media,' in magic.from_file( input_mp4_file ) )
    assert( os.path.basename( output_mp4_file ).endswith( '.mp4' ) )
    ## get info JSON to get width, fps
    proc = subprocess.Popen(
        [ ffprobe_exec, '-v', 'quiet', '-show_streams',
         '-show_format', '-print_format', 'json', input_mp4_file ],
        stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    stdout_val, stderr_val = proc.communicate( )
    mp4file_info = json.loads( stdout_val )
    # from dictionary, get width and height
    width_of_mp4 = int( mp4file_info[ 'streams' ][ 0 ][ 'width' ] )
    height_of_mp4 = int( mp4file_info[ 'streams' ][ 0 ][ 'height' ] )
    #
    ## if input video already square, copy to output mp4 file
    if width_of_mp4 == height_of_mp4:
        shutil.copyfile( input_mp4_file, output_mp4_file )
        return
    #
    ## case #1: height_of_mp4 > width_of_mp4, pad width
    filter_string = 'pad=w=%d:h=0:x=%d:y=0:color=white' % (
        height_of_mp4, ( height_of_mp4 - width_of_mp4 ) // 2 )
    #
    ## case #2: height_of_mp4 < width_of_mp4, pad height
    filter_string = 'pad=w=0:h=%d:x=0:y=%d:color=white' % (
        width_of_mp4, ( width_of_mp4 - height_of_mp4 ) // 2 )
    #
    ## now voodoo magic do do
    exec_cmd = [
        ffmpeg_exec, '-y', '-v', 'warning', '-i', input_mp4_file,
        '-vf', filter_string, output_mp4_file ]
    proc = subprocess.Popen(
        exec_cmd, stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT )
    stdout_val, stderr = proc.communicate( )

def get_youtube_file( youtube_URL, output_file, quality = 'highest' ):
    """
    Uses youtube-dl_ programmatically to download into an MP4_ or MKV_ file.

    :param str youtube_URL: a valid YouTube_ URL for the song clip.
    :param str output_file: the MP4_ or MKV_ video file name.
    :param str quality: the quality level of the MP4 video to download. Default is "highest." Can be one of "highest", "high", "medium", "low".

    :returns: ``True`` if successful, otherwise ``False``.
    :rtype: str

    .. _youtube-dl: https://ytdl-org.github.io/youtube-dl/index.html
    .. _YouTube: https://www.youtube.com
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
        with youtube_dl.YoutubeDL( ydl_opts ) as ydl:
            ydl.download([ youtube_URL ])
            return True
    except youtube_dl.DownloadError: # could not download the file to MP4 OR MKV format
        logging.info( "ERROR, CANNOT DOWNLOAD %s INTO MP4 OR MKV FILE. MY BAD (FOR NOW)." %
                     youtube_URL )
        return False

def youtube2gif( input_youtube_URL, gif_file, quality = 'highest', duration = None, scale = 1.0 ):
    """
    Converts a YouTube_ clip into an animated GIF_ file. First, downloads the YouTube_ clip into an intermediate MP4_ file; then converts the intermediate MP4_ file into the animated GIF_, and deletes the intermediate file.

    :param str input_youtube_URL: the input valid YouTube clip's URL.
    :param str gif_file: the output GIF_ file.
    :param str quality: optional argument for the quality of the YouTube clip. Default is "highest".
    :param float duration: duration, in seconds, of input clip to use to make the animated GIF_. If ``None`` is provided, use the full movie. If provided, then must be :math:`\ge 1` seconds.
    :param float scale: scaling of input width and height of MP4_ file. Default is 1.0. Must be :math:`\ge 0`.

    .. seealso::

       * :py:meth:`mp4togif <nprstuff.core.convert_image.mp4togif>`.
       * :py:meth:`get_youtube_file <nprstuff.core.convert_image.get_youtube_file>`.
    """
    intermediate_file = '%s.mp4' % str( uuid.uuid4( ) )
    status = get_youtube_file(
        input_youtube_URL, intermediate_file, quality = quality )
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
    
def mp4togif( input_mp4_file, gif_file = None, duration = None, scale = 1.0 ):
    """
    This consists of voodoo FFmpeg_ magic that converts MP4_ to animated GIF_ reasonably well. Don't ask me how most of it works, just be on-your-knees-kissing-the-dirt grateful that MILLIONS of people hack onto and into FFmpeg_ so that this information is available, and the workflow works.
    
    This requires a working ``ffmpeg`` and ``ffprobe`` executable to work. If the input file is named ``<input>.mp4``, the output animated GIF file is named ``<input>.gif``.
    
    Here are resources that I used to get this working.
    
    * `Tutorial on high quality movie to animated GIF conversion <movie_2_gif_>`_. I hope this doesn't go away!
    
    * `Using FFPROBE to output JSON format <ffprobe_json_>`_.
    
    :param str input_mp4_file: the name of the valid MP4_ file.
    :param str gif_file: the (optional) name of the animated GIF_ file. If not provided, then creates a GIF file of some default name.
    :param float duration: duration, in seconds, of MP4_ file to use to make the animated GIF_. If ``None`` is provided, use the full movie. If provided, then must be :math:`\ge 1` seconds.
    :param float scale: scaling of input width and height of MP4_ file. Default is 1.0. Must be :math:`\ge 0`.
  
    .. seealso:: :py:meth:`make_square_mp4video <nprstuff.core.convert_image.make_square_mp4video>`.
    
    .. _GIF: https://en.wikipedia.org/wiki/GIF
    .. _movie_2_gif: http://blog.pkh.me/p/21-high-quality-gif-with-ffmpeg.html
    """
    from distutils.spawn import find_executable
    ffmpeg_exec = find_executable( 'ffmpeg' )
    ffprobe_exec = find_executable( 'ffprobe' )
    assert(all(map(lambda tok: tok is not None, ( ffmpeg_exec, ffprobe_exec ))))
    assert( os.path.basename( input_mp4_file ).endswith( '.mp4' ) )
    assert( os.path.isfile( input_mp4_file ) )
    if duration is not None: assert( duration >= 1.0 )
    assert( scale > 0.0 )
    #
    ## assert this is an MP4 file
    assert( 'ISO Media,' in magic.from_file( input_mp4_file ) )
    #
    ## GIF output and PALETTE file
    if gif_file is None: gif_file = input_mp4_file.replace('.mp4', '.gif' )
    else: assert( os.path.basename( gif_file ).endswith( '.gif' ) )
    palettefile = '%s.png' % str( uuid.uuid4( ) )
    #
    ## step #0: first scale the image if not X1
    newmp4file = input_mp4_file
    if scale != 1.0:
        newmp4file = '%s.mp4' % str( uuid.uuid4( ) )
        #
        ## motherfucker
        ## thought experiment: you want to scale a (divisible-by-two) MP4 file by some multiplier
        ## the OUTPUT file itself must have width AND height divisible by two
        ## the corporate knowledge is embedded in 'scale=ceil(iw*%0.2f)*2:ceil(ih*%0.2f)*2' % ( scale * 0.5, scale * 0.5 )
        ## intent of that video filter: scale width and height by HALF of scale, round-up width + height, multiple by 2.
        ## by definition this will create a final (scaled) width and height that are divisible by two
        ## solution to impossib-error: https://stackoverflow.com/questions/20847674/ffmpeg-libx264-height-not-divisible-by-2
        ## motherfucker
        cmd = [
            ffmpeg_exec, '-y', '-v', 'warning', '-i', input_mp4_file,
            '-vf', 'scale=ceil(iw*%0.2f)*2:ceil(ih*%0.2f)*2' % ( scale * 0.5, scale * 0.5 ),
            newmp4file ]
        logging.debug('COMMAND TO SCALE = %s.' % ' '.join( cmd ) )
        stdout_val = subprocess.check_output(
            cmd, stderr = subprocess.STDOUT )
        logging.debug( 'OUTPUT FFMPEG SCALE = %s.' % stdout_val )
    
    #
    ## get info JSON to get width, fps
    stdout_val = subprocess.check_output(
        [ ffprobe_exec, '-v', 'quiet', '-show_streams',
         '-show_format', '-print_format', 'json', newmp4file ],
        stderr = subprocess.STDOUT )
    mp4file_info = json.loads( stdout_val )
    logging.debug( 'mp4file_info = %s.' % mp4file_info )
    # from dictionary, get width
    width_of_mp4 = int( mp4file_info[ 'streams' ][ 0 ][ 'width' ] )
    fps_string = mp4file_info[ 'streams' ][ 0 ][ 'avg_frame_rate' ]
    fps = int( float( fps_string.split('/')[0] ) * 1.0 /
              float( fps_string.split('/')[1] ) )
    
    #
    ## now do the voodoo magic from resource #1
    ## step #1: create palette, run at fps
    args_mov_before = [ ]
    if duration is not None: args_mov_before = [ '-t', '%0.3f' % duration ]
    cmd = [
        ffmpeg_exec, '-y', '-v', 'warning', ] + args_mov_before + [
            '-i', newmp4file,
            '-vf', 'fps=%d,scale=%d:-1:flags=lanczos,palettegen' % ( fps, width_of_mp4 ),
            palettefile ]
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    stdout_val, stderr_val = proc.communicate( )
    assert( os.path.isfile( palettefile ) )
    #
    ## step #2: take palette file, MP4 file, create animated GIF
    cmd = [
        ffmpeg_exec, '-y', '-v', 'warning' ] + args_mov_before + [
            '-i', newmp4file,
            '-i', palettefile, '-lavfi', 'fps=%d,scale=%d:-1:flags=lanczos[x];[x][1:v]paletteuse' % (
            fps, width_of_mp4 ), gif_file ]
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT )
    stdout_val, stderr_val = proc.communicate( )
    #
    ## now batting cleanup
    try:
        if newmp4file != input_mp4_file: os.remove( newmp4file )
        os.remove( palettefile )
    except Exception as e:
        print( 'REASON FAILURE WHY:', e )
        pass

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
    
        * :py:meth:`png2png <nprstuff.core.convert_image.png2png>`.
        * :py:meth:`pdf2png <nprstuff.core.convert_image.pdf2png>`.
    """
    
    try:
        from PyQt5.QtSvg import QSvgRenderer
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

        * :py:meth:`svg2png <nprstuff.core.convert_image.svg2png>`.
        * :py:meth:`pdf2png <nprstuff.core.convert_image.pdf2png>`.
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

        * :py:meth:`svg2png <nprstuff.core.convert_image.svg2png>`.
        * :py:meth:`png2png <nprstuff.core.convert_image.png2png>`.
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
