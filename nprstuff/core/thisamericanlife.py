import os, sys, datetime, titlecase, requests
import codecs, feedparser, glob, time, logging
from mutagen.id3 import APIC, TDRC, TALB, COMM, TRCK, TPE2, TPE1, TIT2, TCON, ID3
from bs4 import BeautifulSoup
from urllib.parse import urljoin

_talPICURL = 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Thisamericanlife-wbez.png'
_talurl = 'http://feed.thisamericanlife.org/talpodcast'
_default_inputdir = '/mnt/media/thisamericanlife'

def get_americanlife_info(
    epno, throwException = True, extraStuff = None, verify = True, dump = False,
    directory = '.' ):
    """
    Returns a tuple of title, year given the episode number for `This American Life`_.
    
    :param int epno: the episode number of `This American Life`_.
    :param bool throwException: optional argument, whether to throw a :py:class:`ValueError` exception if *cannot* find the title of this candidate `This American Life`_ episode. Default is ``True``.
    :param str extraStuff: additional stuff to put into the candidate URL for `This American Life`_ episodes. Default is ``None``.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param bool dump: optional argument, if ``True`` then instead of downloading first `This American Life`_, downloads the XML info as a file, named ``PRI.ThisAmericanLife.<NUM>.xml``. Default is ``False``.
    :param str directory: the directory into which to download a `This American Life`_ episode. Default is the current working directory.
    :returns: a :py:class:`tuple` of ``title``, ``year``, and ``html`` in which this episode was aired. Otherwise, if ``throwException`` is ``False`` and title is not found, returns ``None``. ``html`` is the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` tree of the XML data for this `This American Life`_ episode.
    :rtype: tuple

    .. seealso:: :py:meth:`get_american_life <nprstuff.core.thisamericanlife.get_american_life>`.
    """
    
    # the see if this episode of this american life exists...
    if extraStuff is None:
        resp = requests.get( 'https://www.thisamericanlife.org/radio-archives/episode/%d' % epno, verify = verify )
    else:
        resp = requests.get( 'https://www.thisamericanlife.org/radio-archives/episode/%d/%s' % ( epno, extraStuff ),
                            verify = verify )
    if resp.status_code != 200:
        raise ValueError("Error, could not find This American Life episode %d, because could not open webpage." % epno)
    #
    enc = resp.headers['content-type'].split(';')[-1].split('=')[-1].strip().upper()
    if enc not in ( 'UTF-8', ):
        html = BeautifulSoup( resp.text.encode(encoding=enc ), 'lxml' )
    else:
        html = BeautifulSoup( resp.text, 'lxml' )
    if dump:
        assert( os.path.isdir( directory ) )
        with open( os.path.join( directory, 'PRI.ThisAmericanLife.%03d.xml' % epno ), 'w') as openfile:
            openfile.write('%s\n' % html.prettify( ) )
        return
    #
    def get_date( date_s ):
        try:
            return datetime.datetime.strptime( date_s, '%B %d, %Y' ).date( )
        except:
            return datetime.datetime.strptime( date_s, '%b %d, %Y' ).date( )
    date_act = max(map(lambda elem: get_date( elem.text.strip( ).replace('.', '')),
                       [ html.find_all('span', { 'class' : 'date-display-single' })[0], ]))
    year = date_act.year
    #
    title_elem_list = html.find_all('div', { 'class' : 'episode-title' } )
    if len(title_elem_list) != 1:
        logging.info("Error, cannot find date and title for This American Life episode #%d." % epno)
        if throwException:
            raise ValueError("Error, cannot find date and title for This American Life episode #%d." % epno)
        else: return None
    title = max(title_elem_list).text.strip()
    title = title.replace('Promo', '').strip( )
    return title, year, html

#
## see if I can find the URL for TAL by searching through the ALL page
def get_TAL_URL( epno, verify = True ):
    """
    returns the MP3 URL of the `This American Life`_ episode.
    
    :param int epno: the episode number of `This American Life`_.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :returns: the URL for `This American Life`_ episode. If URL could not be found, returns ``None``.
    :rtype: str
    """
    url_epelem = 'https://www.thisamericanlife.org/radio-archives/episode/%d' % epno
    response = requests.get( url_epelem, verify = verify )
    if not response.ok:
        logging.info( 'ERROR, %s not accessible' % url_epelem )
        return None
    html = BeautifulSoup( response.content, 'lxml' )
    #
    ## now find podcast URL from the enclosing A element whose class has text Download
    def is_download_href( href_elem ):
        if 'href' not in href_elem.attrs: return False
        valid_label_elems = list(
            filter(lambda elem: 'class' in elem.attrs and elem['class'] == [ 'label' ], href_elem.find_all('span' ) ) )
        if len( valid_label_elems ) != 1: return False
        valid_label_elem = valid_label_elems[ 0 ]
        return valid_label_elem.text.strip( ) == 'Download'
    #
    podcast_URL_elems = list(filter(is_download_href, html.find_all('a')))
    if len( podcast_URL_elems ) != 1:
        logging.info( 'ERROR, could not find MP3 podcast URL for episode %d, with page %s.' % (
            epno, url_epelem ) )
        return None
    podcast_URL_elem = podcast_URL_elems[ 0 ]
    podcast_URL = podcast_URL_elem['href']
    return podcast_URL
  
def get_american_life(
    epno, directory = '/mnt/media/thisamericanlife', extraStuff = None, verify = True,
    dump = False ):
    """
    Downloads an episode of `This American Life`_ into a given directory.

    :param int epno: the episode number of `This American Life`_.
    :param str directory: the directory into which to download a `This American Life`_ episode. Default is ``/mnt/media/thisamericanlife``.
    :param str extraStuff: additional stuff to put into the candidate URL for `This American Life`_ episodes. Default is ``None``.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param bool dump: optional argument, if ``True`` then instead of downloading first `This American Life`_, downloads the XML info as a file, named ``PRI.ThisAmericanLife.<NUM>.xml``. Default is ``False``.

    
    .. seealso:: :py:meth:`get_americanlife_info <nprstuff.core.thisamericanlife.get_americanlife_info>`.
    """
    
    try:
        tup = get_americanlife_info(epno, extraStuff = extraStuff, verify = verify, dump = dump,
                                    directory = directory )
        if dump: return
        title, year, html = tup
    except ValueError as e:
        print(e)
        print('Cannot find date and title for This American Life episode #%d.' % epno)
        return
  
    def get_resp( html ):
        stupid_search_urls_because_python = list(
            filter(lambda item: 'href' in item.attrs and 'podtrac' in item['href'] and 'mp3' in item['href'],
                   html.find_all('a')))
        if len( stupid_search_urls_because_python ) == 0:
            logging.info( "ERROR, ambiguous URL for MP3 file. Exiting..." )
            logging.info( "NUM URLS: %d." % len( stupid_search_urls_because_python ) )
            logging.info( "URLS: %s." % '\n'.join(map(lambda item: item['href'], stupid_search_urls_because_python)))
            return None
        urlopn = stupid_search_urls_because_python[0]['href']
        resp = requests.get( urlopn, stream = True, verify = verify )
        if resp.ok: return resp
        logging.info( "TAL episode %d URL = %s not work." % (
            epno, urlopn ) )
        return None
    #
    if not os.path.isdir(directory):
        logging.info( "Error, %s is not a directory." % directory )
        raise ValueError("Error, %s is not a directory." % directory)
    outfile = os.path.join(directory, 'PRI.ThisAmericanLife.%03d.mp3' % epno)
    #
    resp = get_resp( html )
    if resp is None:
        logging.info( 'Error, 1st and 2nd choice URL for TAL podcasts for episode %d not working.' % epno )
        urlopn = 'http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/%d.mp3' % epno
        resp = requests.get( urlopn, stream = True, verify = verify )
        if not resp.ok:
            print("Error, could not download This American Life episode #%d. Exiting..." % epno)
            return
    with open( outfile, 'wb') as openfile:
        for chunk in resp.iter_content( 1 << 16 ):
            openfile.write( chunk )
    #
    mp3tags = ID3( )
    mp3tags['TDRC'] = TDRC(encoding = 0, text = [ u'%d' % year ])
    mp3tags['TALB'] = TALB(encoding = 0, text = [ u'This American Life' ])
    mp3tags['TRCK'] = TRCK(encoding = 0, text = [ u'%d' % epno ])
    mp3tags['TPE2'] = TPE2(encoding = 0, text = [ u'Ira Glass'])
    mp3tags['TPE1'] = TPE1(encoding = 0, text = [ u'Ira Glass'])
    try: mp3tags['TIT2'] = TIT2(encoding = 3, text = [ '#%03d: %s' % ( epno, title ) ] )
    except: mp3tags['TIT2'] = TIT2(encoding = 3, text = [ codecs.encode('#%03d: %s' % ( epno, title ), 'utf8') ])
    mp3tags['TCON'] = TCON(encoding = 0, text = [ u'Podcast'])
    mp3tags['APIC'] = APIC( encoding = 0, mime = 'image/png', data = requests.get( _talPICURL ).content )
    mp3tags.save( outfile, v1=0 )
    os.chmod( outfile, 0o644 )
    
def thisamericanlife_crontab( ):
    """
    This python module downloads a `This American Life`_ episode every weekend. It uses the Feedparser_'s functionality using its RSS feed.

    .. _Feedparser: https://feedparser.readthedocs.io
    """
    def _get_track( filename ):
        assert( os.path.basename( filename ).endswith( '.mp3' ) ) 
        mp3tags = ID3( filename ) 
        if 'TRCK' not in mp3tags: return None 
        return int( mp3tags['TRCK'].text[0] )
    #
    def _get_epno( entry ):
        if 'title' not in entry: return -1
        title = entry['title']
        epno = int( title.split(':')[0].strip( ) )
        return epno
    #
    ## get all track numbers, and find what's left
    episodes_here = set(filter(None, map(
        _get_track, glob.glob( os.path.join(
        _default_inputdir, 'PRI.ThisAmericanLife.*mp3' ) ) ) ) )
    #episodes_left = set( range( 1, max( episodes_here ) + 1 ) ) - episodes_here
    
    #
    ## from RSS feed, find latest episode number
    d = feedparser.parse( 'http://feed.thisamericanlife.org/talpodcast' )
    epno = _get_epno( max(d['entries'], key = lambda ent: _get_epno( ent ) ) )
    if epno not in episodes_here:
        time0 = time.time( )
        logging.debug('downloading This American Life epsiode #%03d' % epno )
        try:
            thisamericanlife.get_american_life( epno )
            logging.debug("finished downloading This American Life episode #%03d in %0.3f seconds" % (
                epno, time.time( ) - time0 ) )
        except:
            print( "Could not download This American Life episode #%03d" % epno )
    else: print( "Already have This American Life episode #%03d" % epno )
