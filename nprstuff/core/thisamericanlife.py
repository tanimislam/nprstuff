import os, sys, datetime, titlecase, requests
import codecs, feedparser, glob, time
from mutagen.id3 import APIC, TDRC, TALB, COMM, TRCK, TPE2, TPE1, TIT2, TCON, ID3
from nprstuff import nprstuff_logger as logger, logging_dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathos.multiprocessing import ThreadPool, cpu_count
from argparse import ArgumentParser

_talPICURL = 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Thisamericanlife-wbez.png'
_talurl = 'http://feed.thisamericanlife.org/talpodcast'
_default_inputdir = '/mnt/media/thisamericanlife'

def _get_tal_track( filename ):
    assert( os.path.basename( filename ).endswith( '.mp3' ) ) 
    mp3tags = ID3( filename ) 
    if 'TRCK' not in mp3tags: return None 
    return int( mp3tags['TRCK'].text[0] )

def _get_tal_epno( entry ):
    if 'title' not in entry: return -1
    title = entry['title']
    epno = int( title.split(':')[0].strip( ) )
    return epno

def give_up_ytdlp_thisamericanlife( epno ):
    """
    This is one of those, "I completely give up on trying to figure out why the ``This American Life`` website is barfing out with 403 error messages", kinds of messages. *Instead*, I use the ``This American Life`` InfoExtractor from yt-dlp to get at the TAL episode's URL-that-works.

    :param int epno: the episode number of `This American Life`_.
    :returns: the URL as a :py:class:`str` that :py:meth:`get_americanlife_info <nprstuff.core.thisamericanlife.get_americanlife_info>` uses.
    :rtype: str
    """
    from yt_dlp import YoutubeDL
    from yt_dlp.extractor.thisamericanlife import ThisAmericanLifeIE

    tale = ThisAmericanLifeIE( YoutubeDL( ) )
    webpage = tale._download_webpage(
        'http://www.thisamericanlife.org/radio-archives/episode/%03d' % epno, '%03d' % epno )
    html = BeautifulSoup( webpage, 'html.parser' )
    return html
    # elems = list(filter(lambda elem: 'href' in elem.attrs and '757' in elem['href'],
    #                     html.find_all('link', { 'rel' : 'canonical'})))
    # if len( elems ) == 0:
    #     print( 'NUMBER OF ELEMS = 0' )
    #     return None
    # elem = elems[ 0 ]
    # print( elem['href'] )
    # return elem['href']

    
def get_americanlife_info(
    epno, throwException = True, extraStuff = None, verify = True, dump = False,
    directory = '.', hardURL = None ):
    """
    Returns a tuple of title, year given the episode number for `This American Life`_. Sometimes `This American Life`_ is extremely uncooperative; for example, on 25 OCTOBER 2020, `This American Life`_ said episode 721 implied that it was "Small Worlds", but in actuality it was `The Moment After This Moment`_. An extra optional argument, ``hardURL``, is used to hard-encode this URL if the standard method of supplying an episode number through ``epno`` does not work.
    
    :param int epno: the episode number of `This American Life`_.
    :param bool throwException: optional argument, whether to throw a :py:class:`ValueError` exception if *cannot* find the title of this candidate `This American Life`_ episode. Default is ``True``.
    :param str extraStuff: additional stuff to put into the candidate URL for `This American Life`_ episodes. Default is ``None``.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param bool dump: optional argument, if ``True`` then instead of downloading first `This American Life`_, downloads the XML info as a file, named ``PRI.ThisAmericanLife.<NUM>.xml``. Default is ``False``.
    :param str directory: the directory into which to download a `This American Life`_ episode. Default is the current working directory.
    :returns: a :py:class:`tuple` of ``title``, ``year``, and ``html`` in which this episode was aired. Otherwise, if ``throwException`` is ``False`` and title is not found, returns ``None``. ``html`` is the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` tree of the XML data for this `This American Life`_ episode.
    :rtype: tuple

    .. seealso:: :py:meth:`get_american_life <nprstuff.core.thisamericanlife.get_american_life>`.

    .. _`The Moment After This Moment`: https://www.thisamericanlife.org/720/the-moment-after-this-moment
    """
    
    # the see if this episode of this american life exists...
    def _get_response( ):
        if hardURL is not None:
            logger.info('GOING TO %s.' % hardURL )
            return requests.get( hardURL, verify = verify )
        if extraStuff is None:
            logger.info('GOING TO https://www.thisamericanlife.org/radio-archives/episode/%d.' % epno )
            html = give_up_ytdlp_thisamericanlife( epno )
            elems = list(filter(lambda elem: 'href' in elem.attrs and '%03d' % epno in elem['href'],
                            html.find_all('link', { 'rel' : 'canonical'})))
            if len( elems ) == 0: give_up_ytdlp_thisamericanlife( epno )

    html = give_up_ytdlp_thisamericanlife( epno )
    
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
        logger.info("Error, cannot find date and title for This American Life episode #%d." % epno)
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
        logger.info( 'ERROR, %s not accessible' % url_epelem )
        return None
    html = BeautifulSoup( response.content, 'html.parser' )
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
        logger.info( 'ERROR, could not find MP3 podcast URL for episode %d, with page %s.' % (
            epno, url_epelem ) )
        return None
    podcast_URL_elem = podcast_URL_elems[ 0 ]
    podcast_URL = podcast_URL_elem['href']
    return podcast_URL

def get_american_life_remaining( ):
    """
    This downloads *remaining* `This American Life`_ episodes. To determine missing episodes, it first finds the maximum episode number that we have downloaded. It subtracts the episodes we have downloaded from the integer list that runs from 1 to the maximum episode number. Then it downloads these remaining episodes *in parallel*.
    """
    #
    ## get all track numbers, and find what's left
    episodes_here = set(filter(None, map(
        _get_tal_track, glob.glob( os.path.join(
        _default_inputdir, 'PRI.ThisAmericanLife.*.mp3' ) ) ) ) )
    def _get_last_episode( ):
        try:
            html = BeautifulSoup( requests.get( "https://thisamericanlife.org" ).content, 'html.parser' )
            elem = list(filter(lambda elem: "this week" in elem.text.lower(), html.find_all("a")))[0]
            
        except Exception as e:
            logger.info("ERROR WHEN TRYING TO LOOK FOR LAST TAL EPISODE: %s." % str( e ) )
            return max( episodes_here )
    episodes_remaining = set(range(1, max( episodes_here ) + 1 ) ) - episodes_here
    if len( episodes_remaining ) == 0:
        return
    with ThreadPool( processes = max(1, cpu_count( ) // 2 ) ) as pool:
        time0 = time.perf_counter( )
        _ = list( pool.map( get_american_life, episodes_remaining ) )
        logger.info( 'was able to download %d missing TAL episodes (%s) in %0.3f seconds.' % (
            len( episodes_remaining ), ', '.join(sorted(episodes_remaining)),
            time.perf_counter( ) - time0 ) )
    
def get_american_life(
    epno, directory = '/mnt/media/thisamericanlife', extraStuff = None, verify = True,
    dump = False, hardURL = None ):
    """
    Downloads an episode of `This American Life`_ into a given directory.

    :param int epno: the episode number of `This American Life`_.
    :param str directory: the directory into which to download a `This American Life`_ episode. Default is ``/mnt/media/thisamericanlife``.
    :param str extraStuff: additional stuff to put into the candidate URL for `This American Life`_ episodes. Default is ``None``.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param bool dump: optional argument, if ``True`` then instead of downloading first `This American Life`_, downloads the XML info as a file, named ``PRI.ThisAmericanLife.<NUM>.xml``. Default is ``False``.
    :param str hardURL: optional argument, the hard-coded URL for a given TAL episode, if ``epno`` does not work.
    
    .. seealso:: :py:meth:`get_americanlife_info <nprstuff.core.thisamericanlife.get_americanlife_info>`.
    """
    
    try:
        tup = get_americanlife_info(epno, extraStuff = extraStuff, verify = verify, dump = dump,
                                    directory = directory, hardURL = hardURL )
        if dump: return
        title, year, html = tup
        logger.info('TITLE = %s, YEAR = %d.' % ( title, year ) )
    except ValueError as e:
        print(e)
        print('Cannot find date and title for This American Life episode #%d.' % epno)
        return
  
    def get_resp( html ):
        stupid_search_urls_because_python = list(
            filter(lambda item: 'href' in item.attrs and 'podtrac' in item['href'] and 'mp3' in item['href'],
                   html.find_all('a')))
        if len( stupid_search_urls_because_python ) == 0: # update 20240609
            stupid_search_urls_because_python = list(
                filter(lambda elem: 'href' in elem.attrs and 'download' in elem.attrs, html.find_all('a')))
        if len( stupid_search_urls_because_python ) == 0:
            logger.info( "ERROR, ambiguous URL for MP3 file. Exiting..." )
            logger.info( "NUM URLS: %d." % len( stupid_search_urls_because_python ) )
            logger.info( "URLS: %s." % '\n'.join(map(lambda item: item['href'], stupid_search_urls_because_python)))
            return None
        urlopn = stupid_search_urls_because_python[0]['href']
        resp = requests.get( urlopn, stream = True, verify = verify )
        if resp.ok: return resp
        logger.info( "TAL episode %d URL = %s not work." % (
            epno, urlopn ) )
        return None
    #
    if not os.path.isdir(directory):
        logger.info( "Error, %s is not a directory." % directory )
        raise ValueError("Error, %s is not a directory." % directory)
    outfile = os.path.join(directory, 'PRI.ThisAmericanLife.%03d.mp3' % epno)
    #
    resp = get_resp( html )
    if resp is None:
        logger.info( 'Error, 1st and 2nd choice URL for TAL podcasts for episode %d not working.' % epno )
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
    Downloads a `This American Life`_ episode every weekend. It looks at the `This American Life`_ website to determine the latest episode.

    .. warning::

       UPDATE 10 JANUARY 2021, it *no longer* uses the Feedparser_'s functionality using its RSS feed.

    .. _Feedparser: https://feedparser.readthedocs.io
    """
    parser = ArgumentParser( )
    parser.add_argument( '-i', '--info', dest = 'do_info', action = 'store_true', default = False,
                        help = 'If chosen, then turn on INFO logging.' )
    args = parser.parse_args( )
    if args.do_info: nprstuff_logger.setLevel( logging_dict[ 'INFO' ] )

    def _get_latest_epno_from_website( ):
        response = requests.get( 'https://www.thisamericanlife.org' )
        if response.status_code != 200:
            return 'ERROR, could not reach www.thisamericanlife.org. Status code = %d.' % response.status_code, None
        html = BeautifulSoup( response.content, 'html.parser' )
        episode_elements = list(filter(lambda elem: 'data-episode' in elem.attrs and 'class' in elem.attrs, html.find_all('a', { 'data-type' : 'episode' } ) ) )
        if len( episode_elements ) == 0:
            return 'Error, could not determine latest episode number from www.thisamericanlife.org.', None
        epno_latest = int( episode_elements[ 0 ].attrs['data-episode'] )
        return 'SUCCESS', epno_latest
        
    
    #
    ## get all track numbers, and find what's left
    episodes_here = set(filter(None, map(
        _get_tal_track, glob.glob( os.path.join(
        _default_inputdir, 'PRI.ThisAmericanLife.*mp3' ) ) ) ) )
    
    #
    ## from website, find latest episode number  
    status, epno = _get_latest_epno_from_website( )
    if status != 'SUCCESS':
        print( status )
        return
    if epno in episodes_here:
        print( "Already have This American Life episode #%03d" % epno )
        return
    #
    time0 = time.perf_counter( )
    logger.info('downloading This American Life episode #%03d' % epno )
    try:
        thisamericanlife.get_american_life( epno )
        logger.info( "finished downloading This American Life episode #%03d in %0.3f seconds" % (
            epno, time.time( ) - time0 ) )
    except:
        print( "Could not download This American Life episode #%03d" % epno )
