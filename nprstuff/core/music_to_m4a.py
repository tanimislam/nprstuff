import os, magic, subprocess, filecmp, requests, titlecase
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image
from mutagen.mp4 import MP4Cover, MP4, MP4Cover
from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis
from distutils.spawn import find_executable

_files_to_convert_from = (
    'application/x-flac',
    'audio/x-flac',
    'application/ogg',
    'audio/mpeg' )

def _can_convert_file( filename ):
    if not os.path.isfile(filename): return False
    #if magic.from_file(filename, mime=True).strip() in \
    #   _files_to_convert_from:
    #    return True
    return any(map(lambda tok: os.path.basename(filename).endswith('.%s' % tok),
                   ( 'mp3', 'ogg', 'flac' ) ) )

def _get_file_data( album_path ):
    if bool( urlparse(album_path).netloc):
        return requests.get( album_path).content
    else: return open( album_path, 'rb' )

def _get_file_type(file_data):
    valid_file_types_image = { 'JPEG' : MP4Cover.FORMAT_JPEG, 
                              'PNG' : MP4Cover.FORMAT_PNG }
    try:
        with BytesIO( file_data ) as csio:
            im = Image.open(csio)
            if im.format.upper() in valid_file_types_image.keys():
                return valid_file_types_image[im.format.upper() ]
            else:
                return None
    except IOError:
        return None

def rename_m4a( m4afilename ):
    """
    Renames an M4A_ music file to ``<artist>.<song>.m4a``, where ``<artist>`` is the artist name and ``<song>`` is the song title.
    
    :param str m4filename: the input M4A_ file name.
    """
    assert( os.path.isfile( m4afilename ) )
    assert( m4afilename.endswith( '.m4a' ) )
    #if magic.from_file(m4afilename, mime = True).strip() != 'audio/mp4':
    #    return
    mp4tags = MP4(m4afilename)
    curdir = os.path.dirname( os.path.abspath( m4afilename ) )
    if len(set([ '\xa9nam', '\xa9ART' ]) - set(mp4tags.keys())) != 0:
        return
    song_title = titlecase.titlecase( max(mp4tags.tags['\xa9nam']) )
    song_artist = max(mp4tags.tags['\xa9ART'])
    newfile = os.path.join(curdir, '%s.%s.m4a' % ( song_artist, song_title ) )
    if os.path.isfile(newfile) and filecmp.cmp(newfile, m4afilename):
        return
    os.rename(m4afilename, newfile)

def get_defaultname( m4afilename, showalbum = False ):
    """
    Returns a candidate default file name for an M4A_ file, given its metadata.
    
    :param str m4afilename: the input M4A_ file name.
    :param bool showalbum: optional argument. If ``True``, then file name will include the song's album. If ``False``, only the artist and song title.
    :returns: the candidate file name for the M4A_ file. If ``showalbum`` is ``True``, name is ``<artist>.<album>.<song>.m4a``. If ``False``, name is  ``<artist>.<song>.m4a``.
    :rtype: str
    """
    mp4tags = MP4(m4afilename)
    curdir = os.path.dirname( os.path.abspath( m4afilename ) )
    if len(set([ '\xa9nam', '\xa9ART' ]) - set(mp4tags.keys())) != 0:
        return
    song_title = titlecase.titlecase( max(mp4tags.tags['\xa9nam']) )
    song_artist = max(mp4tags.tags['\xa9ART'])
    song_title = song_title.replace('/', '-')
    song_artist = song_artist.replace('/', '-')
    if not showalbum:
        return '%s.%s.m4a' % ( song_artist, song_title )
    else:
        song_album = titlecase.titlecase( max( mp4tags.tags['\xa9alb'] ) )
        song_album = song_album.replace('/', '-')
        return '%s.%s.%s.m4a' % ( song_artist, song_album, song_title )

def music_to_m4a(filename, tottracks = None,
                 album_path = None, outfile = None,
                 verbose = True, toUpper = True):
    """
    Converts a non M4A_ file (MP3_, OGG_, or FLAC_) into an M4A_ file.

    :param str filename: the input filename.
    :param int tottracks: optional argument, the total number of tracks for the song in its album. If ``None``, then the total number of tracks won't explicitly be defined. Must be :math:`\ge 1`.
    :param str album_path: optional argument, the file path to the album cover (must be a PNG_ or JPEG_ file). If ``None``, then no album cover will be added to the M4A_ song's metadata.
    :param str outfile: optional argument, the name of the output M4A_ file. If ``None``, then file's name is ``<artist>.<song>.m4a``.
    :param bool verbose: optional argument. If ``True``, the print out more debugging output.
    :param bool toUpper: optional argument. If ``True``, then run titlecase_ on the song title.
    
    .. _titlecase: https://github.com/ppannuto/python-titlecase
    """
    ffmpeg_exec = find_executable( 'ffmpeg' )
    if ffmpeg_exec is None:
        raise ValueError("Error, cannot find ffmpeg executable." )
    if not _can_convert_file(filename):
        raise ValueError("Error, cannot convert %s to m4a." % filename)
    #
    if os.path.basename( filename ).lower( ).endswith( '.mp3' ):
        tags = MP3( filename ).tags
        artist = tags[ 'TPE1' ].text[ 0 ]
        title = tags[ 'TIT2' ].text[ 0 ]
        trackno = int( tags[ 'TRCK' ].text[0].split('/')[0] )
    elif os.path.basename( filename ).lower( ).endswith( '.ogg' ):
        tags = OggVorbis( filename ).tags
        artist = max( tags[ 'artist' ] )
        title = max( tags[ 'title' ] )
        trackno = int( max( tags[ 'tracknumber' ] ) )
    elif os.path.basename( filename ).lower( ).endswith( '.flac' ):
        tags = FLAC( filename ).tags
        artist = max( tags[ 'artist' ] )
        title = max( tags[ 'title' ] )
        trackno = int( max( tags[ 'TRACKNUMBER' ] ) )
    #
    if toUpper: title = titlecase.titlecase( title )
  
    #
    if outfile is None:
        outfile = '%s.%s.m4a' % ( artist, title )
    
    exec_path = [ ffmpeg_exec, '-y', '-i', filename, '-map', '0:0', 
                 '-strict', 'experimental', '-aq', '400', outfile ]
    proc = subprocess.Popen(
        exec_path, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout_val, stderr_val = proc.communicate()
    if verbose: print( stdout_val )
    #
    mp4tags = MP4(outfile)
    mp4tags['\xa9nam'] = [ title, ]
    if tottracks is not None:
        if 'trkn' not in mp4tags.tags.keys():
            mp4tags.tags['trkn'] = [ ( trackno, tottracks), ]
        else:
            _, tottrks = max( mp4tags.tags['trkn'] )
        mp4tags.tags['trkn'] = [ ( trackno, tottracks), ]
    else:
        if 'trkn' not in mp4tags.tags.keys():
            mp4tags.tags['trkn'] = [ ( trackno, 0), ]

    fmttype = None
    if album_path is not None:
        file_data = _get_file_data( album_path )
        fmttype = _get_file_type( file_data)
    if fmttype is not None:
        mp4tags.tags['covr'] = [ MP4Cover( file_data, fmttype ), ]
  
    mp4tags.save()
