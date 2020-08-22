import os, sys, lxml.html, subprocess
from urllib.request import urlopen
from distutils.spawn import find_executable
from nprstuff.core import npr_utils

def rm_get_main_url(date_s):
    """
    :param date_s: the :py:class:`date <datetime.date>` for this episode, which must be a Saturday.
    :returns: the full RealMedia_ URL for this older `NPR Wait Wait <waitwait_>`_ episode.
    :rtype: str

    .. _RealMedia: https://en.wikipedia.org/wiki/RealMedia
    """
    if not npr_utils.is_saturday(date_s):
        raise ValueError("Error, this date given by '%s' is not a Saturday." %
                         npr_utils.get_datestring(date_s) )
    #
    mon_lower = date_s.strftime('%b').lower()
    year = date_s.year
    dsub = date_s.strftime('%y%m%d')
    full_rm_url = 'http://www.npr.org/programs/waitwait/archrndwn/%04d/%s/%s.waitwait.html' % (
        year, mon_lower, dsub )
    return full_rm_url

def rm_get_title_from_url( date_s ):
    """
    :param date_s: the :py:class:`date <datetime.date>` for this episode, which must be a Saturday.
    :returns: a full title for the `NPR Wait Wait <waitwait_>`_ RealMedia_ episode.
    :rtype: str
    """
    full_rm_url = rm_get_main_url( date_s )
    tree = lxml.html.fromstring( urlopen( full_rm_url ).read() )
    cand_elems = list(
        filter(lambda elem: len(list(elem.iter('a'))) != 0 and
            elem.text is not None, tree.iter('b')))
    subtites = [ elem.text.split('\n')[0].strip() for elem in cand_elems ]
    title = date_s.strftime('%B %d, %Y')
    title = '%s: %s' % (
        title, '; '.join([ '%d) %s' % ( num + 1, subtite ) for
                          (num, subtite) in enumerate(subtites) ]) )
    return title

def rm_download_file( date_s, outdir = os.getcwd() ):
    """
    downloads the RealMedia_ `NPR Wait Wait <waitwait_>`_ episode into a specified directory.
    
    :param date_s: the :py:class:`date <datetime.date>` for this episode, which must be a Saturday.
    :param str outdir: the directory into which one downloads the `NPR Fresh Air`_ episodes.
    :returns: the RealMedia_ output file.
    :rtype: str
    """
    decdate = npr_utils.get_decdate( date_s )
    outfile = os.path.join( outdir, 'NPR.WaitWait.%s.rm' % decdate )
    try:
        dsub = date_s.strftime('%Y%m%d')
        rm_url = 'http://download.npr.org/real.npr.na-central/waitwait/%s_waitwait.rm' % dsub
        req = urlopen( rm_url )
        with open( outfile, 'w' ) as openfile:
            openfile.write( req.read() )
        return outfile
    except Exception as e:
        if os.path.isfile( outfile ):
            os.remove( outfile )
        raise ValueError("Error, could not download Wait Wait RM file for '%s' into %s." % (
            npr_utils.get_datestring(date_s), outdir ) )        
  
def rm_create_wav_file( date_s, rm_file, outdir = os.getcwd() ):
    """
    Uses MPlayer_ to convert the RealMedia_ `NPR Wait Wait <waitwait_>`_ file into WAV_ format.

    .. _WAV: https://en.wikipedia.org/wiki/WAV
    .. _MPlayer: https://en.wikipedia.org/wiki/MPlayer
    """
    mplayer_exec = find_executable( 'mplayer' )
    if mplayer_exec is None:
        raise ValueError("Error, could not find visible MPLAYER." )
    wgdate = date_s.strftime('%d-%b-%Y')
    wavfile = os.path.join( outdir, 'waitwait%s.wav' % wgdate )
    split_cmd = [ mplayer_exec, '-vo', 'null', '-ao', 'pcm:file=%s' % 
                 wavfile, rm_file ]
    proc = subprocess.Popen( split_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    stdout_val, stderr_val = proc.communicate()
    return wavfile
