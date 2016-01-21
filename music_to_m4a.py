#!/usr/bin/env python

import os, magic, tagpy, subprocess, filecmp
import mutagen.mp4, urlparse, urllib2, titlecase
from cStringIO import StringIO
from PIL import Image
from optparse import OptionParser
_files_to_convert_from = ( 'application/x-flac',
                           'audio/x-flac',
                           'application/ogg',
                           'audio/mpeg' )

def _can_convert_file(filename):
    if not os.path.isfile(filename):
        return False
    #if magic.from_file(filename, mime=True).strip() in \
    #   _files_to_convert_from:
    #    return True
    if any([ os.path.basename(filename).endswith('.%s' % tok) for
             tok in ( 'mp3', 'ogg', 'flac' ) ]):
        return True
    return False

def _get_file_data(album_path):
    if bool( urlparse.urlparse(album_path).netloc):
        return urllib2.urlopen( album_path).read()
    else:
        return open( album_path, 'rb' )

def _get_file_type(file_data):
    valid_file_types_image = { 'JPEG' : mutagen.mp4.MP4Cover.FORMAT_JPEG, 
                               'PNG' : mutagen.mp4.MP4Cover.FORMAT_PNG }
    csio = StringIO( file_data )
    try:
        im = Image.open(csio)
        if im.format.upper() in valid_file_types_image.keys():
            return valid_file_types_image[im.format.upper() ]
        else:
            return None
    except IOError:
        return None
           

def rename_m4a(m4afilename):
    if not os.path.isfile(m4afilename):
        return
    if not m4afilename.endswith('.m4a'):
        return
    if magic.from_file(m4afilename, mime = True).strip() != 'audio/mp4':
        return
    mp4tags = mutagen.mp4.MP4(m4afilename)
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
    mp4tags = mutagen.mp4.MP4(m4afilename)
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
                 verbose = True):
    if not _can_convert_file(filename):
        raise ValueError("Error, cannot convert %s to m4a." % filename)
    
    tags = tagpy.FileRef(filename).tag()
    artist = tags.artist
    title = titlecase.titlecase( tags.title )
    trackno = tags.track
    #
    if outfile is None:
        outfile = '%s.%s.m4a' % ( artist, title )
    
    exec_path = [ '/usr/bin/avconv', '-y', '-i', filename, '-map', '0:0', 
                  '-strict', 'experimental', '-aq', '400', outfile ]
    proc = subprocess.Popen( exec_path, stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE)
    stdout_val, stderr_val = proc.communicate()
    if verbose:
        print stdout_val

    mp4tags = mutagen.mp4.MP4(outfile)
    mp4tags['\xa9nam'] = [ title, ]
    if tottracks is not None:
        if 'trkn' not in mp4tags.tags.keys():
            mp4tags.tags['trkn'] = [ ( trackno, tottracks), ]
        else:
            trkno, tottrks = max( mp4tags.tags['trkn'] )
            if tottrks == 0:
                mp4tags.tags['trkn'] = [ ( trackno, tottracks), ]
    else:
        if 'trkn' not in mp4tags.tags.keys():
            mp4tags.tags['trkn'] = [ ( trackno, 0), ]
            
    if album_path is not None:
        file_data = _get_file_data( album_path )
        fmttype = _get_file_type( file_data)
        if fmttype is not None:
            mp4tags.tags['covr'] = [ mutagen.mp4.MP4Cover( file_data, fmttype ), ]
                                                           
    mp4tags.save()

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--inputfile', dest='inputfile', type=str, action='store',
                      help = 'Name of the input audio file to convert.')
    parser.add_option('--outfile', dest='outfile', type=str, action='store',
                      help = 'Optional name of the output file.')
    parser.add_option('--tottracks', dest='tottracks', type=int, action='store',
                      help = 'Optional total number of tracks in album of which song is a part.')
    parser.add_option('--albumloc', dest='albumloc', type=str, action='store',
                      help = 'Optional path to location of the album cover image file. Must be in JPEG or PNG.')
    parser.add_option('--quiet', dest='quiet', action='store_true', default = False,
                      help = 'If chosen, then verbosely print output of processing.')
    parser.add_option('--rename', dest='do_rename', action='store_true', default = False,
                      help = 'If chosen, simply rename the m4a file to the form <artist>.<song title>.m4a') 
    opts, args = parser.parse_args()
    if opts.inputfile is None:
        raise ValueError("Error, input file must be defined.")
    if opts.outfile is not None and opts.outfile.endswith('.m4a'):
        raise ValueError("Error, given output file = %s does not end in .m4a." % opts.outfile)
    if opts.tottracks is not None and opts.tottracks <= 0:
        raise ValueError("Error, given total number of tracks = %d <= 0." % opts.tottracks)
    verbose = not opts.quiet
    
    if not opts.do_rename:
        music_to_m4a( opts.inputfile,
                      tottracks = opts.tottracks,
                      album_path = opts.albumloc,
                      outfile = opts.outfile,
                      verbose = verbose)
    else:
        rename_m4a( opts.inputfile )
                  
