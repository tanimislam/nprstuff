import os, sys, glob, re, requests, mutagen.mp4, json
import subprocess, logging, datetime, time, titlecase, tempfile, shutil
import pathos.multiprocessing as multiprocessing
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from urllib.parse import parse_qs
from nprstuff.core import npr_utils, waitwait_realmedia
from nprstuff import resourceDir

_npr_waitwait_progid = 35
_default_inputdir = os.getcwd( )
try:
    _default_inputdir = npr_utils.get_waitwait_downloaddir( )
except: pass

def get_waitwait_image( verify = True ):
    """
    Get the `NPR Wait Wait <waitwait_>`_ logo as binary data.
    
    :returns: the `NPR Wait Wait logo`_ as binary data, see below.
    
    .. image:: /_static/waitwaitnew.png
       :width: 100%
       :align: center

    .. _`NPR Wait Wait logo`: https://mediaapi.whro.org/images/59d53b5ec76ad8.94499837.jpg
    """
    fname = os.path.join( resourceDir, 'waitwaitnew.png' )
    assert( os.path.isfile( fname ) )
    return open( fname, 'rb' ).read( )
    
def _download_file( input_tuple ):
    mp3URL, filename = input_tuple
    resp = requests.get( mp3URL, stream = True )
    with open(filename, 'wb') as openfile:
        for chunk in resp.iter_content( 65536 ):
            openfile.write( chunk )
    return filename

def get_waitwait_date_from_name(candidateNPRWaitWaitFile):
    """
    :param str candidateNPRWaitWaitFile: the name of the `NPR Wait Wait <waitwait_>`_ episode file name.
    :returns: the :py:class:`date <datetime.date>` object from the `NPR Wait Wait <waitwait_>`_ episode file name.
    :rtype: :py:class:`date <datetime.date>`
    """
    if not os.path.isfile(candidateNPRWaitWaitFile):
        raise ValueError("Error, %s is not a file," % candidateNPRWaitWaitFile )
    if not os.path.basename(candidateNPRWaitWaitFile).endswith('.m4a'):
        raise ValueError("Error, %s does not end in .m4a" % candidateNPRWaitWaitFile )
    if not os.path.basename(candidateNPRWaitWaitFile).startswith('NPR.WaitWait.'):
        raise ValueError("Error, %s is not a valid file" % candidateNPRWaitWaitFile )
    day, mon, year = [ int(tok) for tok in os.path.basename(candidateNPRWaitWaitFile).split('.')[2:5] ]
    return datetime.date(year, mon, day)

def get_waitwait_valid_dates_remaining_tuples(yearnum, inputdir):
    """
    :param int yearnum: the year for which to search for missing `NPR Wait Wait <waitwait_>`_ episodes.
    :param str inputdir: the directory in which the `NPR Wait Wait <waitwait_>`_ episodes live.
    :returns: a sorted :py:class:`list` of :py:class:`tuple`, ordered by candidate track number of the `NPR Wait Wait <waitwait_>`_ episode. The :py:class:`tuple` has three elements: the track number of `NPR Wait Wait <waitwait_>`_ episodes that year, the total number of `NPR Wait Wait <waitwait_>`_ episodes that year, and the :py:class:`date <datetime.date>` for that episode.
    :rtype: list
    """
    waitwait_files_downloaded = glob.glob( os.path.join(inputdir, 'NPR.WaitWait.*.%04d.m4a' % yearnum ) )
    dates_downloaded = set([ get_waitwait_date_from_name(filename) for filename in
                            waitwait_files_downloaded ])
    all_order_saturdays = { date_s : (num+1) for (num, date_s) in
                           enumerate( npr_utils.get_saturday_times_in_year( yearnum ) ) }
    dtime_now = datetime.datetime.now()
    nowd = datetime.date(dtime_now.year, dtime_now.month, dtime_now.day)
    saturdays_left = filter(lambda date_s: date_s < nowd, set( all_order_saturdays.keys() ) - 
                            set( dates_downloaded ) )
    totnum = len( all_order_saturdays.keys() )
    order_dates_remain = sorted([ ( all_order_saturdays[date_s], totnum, date_s ) for
                                 date_s in saturdays_left ], key = lambda tup: tup[0] )
    return order_dates_remain

def _process_waitwaits_by_year_tuple( input_tuple ):
    outputdir, totnum, datetimes_order_tuples = input_tuple
    ww_image = get_waitwait_image()
    driver = npr_utils.get_chrome_driver( )
    for date_s, order in datetimes_order_tuples:
        time0 = time.time()
        try:
            fname = get_waitwait(
                outputdir, date_s, order_totnum = ( order, totnum),
                driver = driver )
            if verbose:
                print('Processed %s in %0.3f seconds.' % ( fname, time.time() - time0 ))
        except Exception as e:
            print('Could not create Wait Wait episode for date %s for some reason.' % (
                npr_utils.get_datestring( date_s ) ) )

def get_all_waitwaits_year( yearnum, inputdir ):
    """
    Looks for missing `NPR Wait Wait <waitwait_>`_ episodes in a given year, then downloads them.

    :param int yearnum: the year for which to search for missing `NPR Wait Wait <waitwait_>`_ episodes.
    :param str inputdir: the directory into which the `NPR Wait Wait <waitwait_>`_ episodes are downloaded.
    """
    order_dates_remain = get_waitwait_valid_dates_remaining_tuples( yearnum, inputdir )
    if len( order_dates_remain ) == 0: return
    totnum = order_dates_remain[0][1]
    nprocs = multiprocessing.cpu_count()
    input_tuples = [ ( inputdir, totnum, [
        ( date_s, order) for ( order, totnum, date_s ) in
        order_dates_remain if ( order - 1 ) % nprocs == procno ] ) for
                    procno in range( nprocs ) ]
    time0 = time.time()
    with multiprocessing.ThreadPool( processes = nprocs ) as pool:
        _ = list( pool.map(_process_waitwaits_by_year_tuple, input_tuples) )
    logging.info('processed all Wait Wait downloads for %04d in %0.3f seconds.' % ( yearnum, time.time() - time0 ) )

def _get_mp3_chapter_tuple_sorted( html, verify, npr_api_key ):
  story_elems = html.find_all('story')
  #
  ## now get the chapter names and mp3 URLs from each story elem
  chapter_names = [ ]
  mp3_urls = [ ]
  for idx_selem in enumerate( story_elems ):
    idx, selem = idx_selem
    num_m3u_elems = len( selem.find_all( 'mp3', { 'type' : 'm3u' } ) )
    if num_m3u_elems == 0: continue # error checking. If doesn't have this chapter, leave it out
    m3u_url = max( selem.find_all( 'mp3', { 'type' : 'm3u' } ) ).text.strip( )
    story_id = selem['id']
    resp = requests.get( 'https://api.npr.org/query', verify = verify,
                         params = { 'id' : story_id, 'apiKey' : npr_api_key } )
    if resp.status_code != 200:
      logging.debug('ERROR GETTING STORY ELEM %d' % idx )
      return None
    h2 = BeautifulSoup( resp.content, 'lxml' )
    img_elem = max( h2.find_all( 'img' ) )
    img_src_url = img_elem['src'].strip( )
    title_dict = parse_qs( img_src_url )
    if 'utmdt' not in title_dict:
      logging.debug('ERROR GETTING STORY ELEM %d, CANNOT FIND TITLE' % idx )
      return None
    chapter_name = titlecase.titlecase( max( title_dict[ 'utmdt' ] ) )
    chapter_names.append( chapter_name )
    #
    ## now get the mp3 URL
    resp = requests.get( m3u_url )
    if resp.status_code != 200:
      logging.debug('EROR GETTING STORY ELEM %d, CANNOT FIND MP3 URL' % idx )
      return None
    mp3_urls.append( resp.content.decode( ).strip( ) )
  #
  ## now sort tuple of (mp3 url, chapter name) by order of mp3 url, and return
  mp3_chapter_tuples = sorted(
    zip( mp3_urls, chapter_names ),
    key = lambda url_chap: int( re.sub('[a-zA-Z]', '', os.path.basename(
      url_chap[0] ).split('.')[0].split('_')[-1] ) ) )
  return mp3_chapter_tuples
    
def get_title_mp3_urls_working( outputdir, date_s, driver, dump = False ):
    """
    Using the new, non-API NPR functionality, get a :py:class:`list` of :py:class:`tuple` of stories for an `NPR Wait Wait <waitwait_>`_ episode. This uses a :py:class:`Webdriver <selenium.webdriver.remote.webdriver.WebDriver>` to get an episode. Here is an example operation,
    
    .. code-block:: python

       >> date_s = datetime.datetime.strptime('August 8, 2020', '%B %d, %Y' ).date( )
       >> title_list_mp3_urls = get_title_mp3_urls_working( '.', date_s, driver )
       >> title_list_mp3_urls
       >> [("Who's Bill This Time?",
         'https://ondemand.npr.org/anon.npr-mp3/npr/waitwait/2020/08/20200808_waitwait_01.mp3'),
        ('Panel Questions',
         'https://ondemand.npr.org/anon.npr-mp3/npr/waitwait/2020/08/20200808_waitwait_02.mp3'),
        ('Bluff the Listener',
         'https://ondemand.npr.org/anon.npr-mp3/npr/waitwait/2020/08/20200808_waitwait_03.mp3'),
        ("Bryan Cranston Plays 'Not My Job' on 'Wait Wait... Don't Tell Me!'",
         'https://ondemand.npr.org/anon.npr-mp3/npr/waitwait/2020/08/20200808_waitwait_04.mp3'),
        ('Panel Questions',
         'https://ondemand.npr.org/anon.npr-mp3/npr/waitwait/2020/08/20200808_waitwait_05.mp3'),
        ('Limericks',
         'https://ondemand.npr.org/anon.npr-mp3/npr/waitwait/2020/08/20200808_waitwait_06.mp3'),
        ('Lightning Fill in the Blank',
         'https://ondemand.npr.org/anon.npr-mp3/npr/waitwait/2020/08/20200808_waitwait_07.mp3'),
        ('Predictions',
         'https://ondemand.npr.org/anon.npr-mp3/npr/waitwait/2020/08/20200808_waitwait_08.mp3')]

    :param str outputdir: the directory into which one downloads the `NPR Wait Wait <waitwait_>`_ episodes.
    :param date_s: the :py:class:`date <datetime.date>` for this episode, which must be a Saturday.
    :param driver: the :py:class:`Webdriver <selenium.webdriver.remote.webdriver.WebDriver>` used for webscraping and querying (instead of using a functional API) for `NPR Wait Wait <waitwait_>`_ episodes.
    :param bool dump: optional argument, if ``True`` returns the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` XML tree for the `NPR Fresh Air`_ episode, or its file representation, and dumps the XML data into an XML file. Default is ``False``.
    
    :returns: the :py:class:`list` of stories, by order, for the `NPR Wait Wait <waitwait_>`_ episode. The first element of each :py:class:`tuple` is the story title, and th second is the MP3_ URL for the story. *However*, if ``debug`` is ``True``, returns the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` XML tree for this `NPR Wait Wait <waitwait_>`_ episode.
    
    .. seealso:: :py:meth:`get_waitwait <nprstuff.core.waitwait.get_waitwait>`.
    """
    #
    ## follow cargo cult code, https://stackoverflow.com/a/49823819/3362358
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    condition = EC.presence_of_element_located((By.ID, "some_element_id_present_after_JS_load"))
    condition = EC.title_contains( 'NPR' )
    #
    ## must be the end datetime
    time0 = time.time( )
    dt_end = datetime.datetime( date_s.year, date_s.month, date_s.day )
    t_end = int( datetime.datetime.timestamp( dt_end ) )
    #
    ## now get using the driver, go to the URL defined there
    mainURL =  "https://www.npr.org/search?query=*&page=1&refinementList[shows]=Wait Wait...Don't Tell Me!&range[lastModifiedDate][min]=%d&range[lastModifiedDate][max]=%d&sortType=byDateAsc" % ( t_end - 86400, t_end )
    logging.info("mainURL: %s." % mainURL )
    driver.get( mainURL )
    time.sleep( 1.5 ) # is 1.5 seconds enough?
    html = BeautifulSoup( driver.page_source, 'lxml' )
    #
    if dump:
        decdate = npr_utils.get_decdate( date_s )
        openfile = os.path.join(
            outputdir, 'NPR.WaitWait.%s.html' % decdate )
        with open( openfile, 'w') as outfile:
            outfile.write( '%s\n' % html.prettify( ) )
        return html

    episode_elems = html.find_all( 'h2', { 'class' : 'title' } )
    episode_urls = list(map(lambda elem: urljoin( 'https://www.npr.org', elem.find_all('a')[0]['href'] ),
                            episode_elems ) )
    logging.info( 'date_s = %s, episode_urls = %s.' % ( date_s, episode_urls ) )

    #
    ## getting the waitwait mp3_url default #1
    def _get_mp3_url_one( html_ep ):
        mp3_elems = list(filter(lambda elem: 'href' in elem.attrs and 'mp3' in elem['href'], html_ep.find_all('a')))
        if len( mp3_elems ) == 0: return None
        mp3_elem = mp3_elems[0]
        mp3_url_split = urlsplit( mp3_elem['href'] )
        mp3_url = urljoin( 'https://%s' % mp3_url_split.netloc, mp3_url_split.path )
        return mp3_url

    #
    ## getting the more complicated URL, option #2
    def _get_mp3_url_two( episode_URL, html_ep ):
        cand_story_elems = html_ep.find_all('div', { 'class' : 'program-block' } )
        if len( cand_story_elems ) != 1: return None
        cand_story_elem = cand_story_elems[0]
        #
        url_elems = list(filter(lambda elem: 'href' in elem.attrs, cand_story_elem.find_all('a')))
        if len( url_elems ) != 1: return None
        episode_URL2 = url_elems[0].attrs['href']
        if episode_URL == episode_URL2: return None
        #
        response = requests.get( episode_URL2 )
        if not response.ok: return None
        html_ep2 = BeautifulSoup( response.content, 'lxml' )
        full_show_elems = html_ep2.find_all('div', { 'id' : 'full-show' } )
        if len( full_show_elems ) != 1: return None
        full_show_elem = full_show_elems[0]
        mp3_elems = list(filter(lambda elem: 'data-play-all' in elem.attrs, full_show_elem.find_all('b')))
        if len( mp3_elems ) != 1: return None
        mp3_elem = mp3_elems[0]
        try:
            json_data = json.loads( mp3_elem.attrs['data-play-all'] )
        except: return None
        if 'audioData' not in json_data: return None
        if 'audioUrl' not in json_data['audioData'][0]: return None
        #
        ## bless me ultima finally (count the None's?) getting to an URL that I can use...
        audioURL = json_data[ 'audioData' ][0][ 'audioUrl' ]
        mp3_url_split = urlsplit( json_data[ 'audioData' ][0][ 'audioUrl' ] )
        mp3_url = urljoin( 'https://%s' % mp3_url_split.netloc, mp3_url_split.path )
        return mp3_url

    #
    ## now get the MP3 URL
    def get_mp3_url( episode_URL, html_ep ):
        mp3_url = _get_mp3_url_one( html_ep )
        if mp3_url is not None: return mp3_url
        #
        return _get_mp3_url_two( episode_URL, html_ep )
        
    
    def get_npr_waitwait_story( episode_URL, date_s ):
        response = requests.get( episode_URL )
        assert( response.ok )
        html_ep = BeautifulSoup( response.content, 'lxml' )
        date_f = date_s.strftime( '%Y-%m-%d' )
        date_elems = list(html_ep.find_all('meta', { 'name' : 'date', 'content' : date_f } ) )
        if len( date_elems ) != 1:
            logging.error( 'could not find date elem for %s.' % episode_URL )
            return None
        #
        ## keep going, get the title    
        title_elems = list(html_ep.find_all('title'))
        if len( title_elems ) == 0:
            logging.error( 'could not find title elem for %s.' % episode_URL )
            return None
        title = titlecase.titlecase( ' '.join(map(lambda tok: tok.strip(), title_elems[0].text.split(':')[:-1])) )
        #
        ## now get the MP3 URL
        mp3_url = get_mp3_url( episode_URL, html_ep )
        print( episode_URL, date_s, mp3_url )
        if mp3_url is None: return None
        #
        ## now get order
        bname = re.sub('_$', '', os.path.basename( mp3_url ).split('.')[0].strip( ) ).strip( )
        logging.info('INFO get_npr_waitwait_story(%s,%s).bname = %s.' % (
            episode_URL, date_s, bname ) )
        try:
            order = int( bname.split('_')[-1] )
            #
            ## return tuple of order, title, URL
            logging.info('info: %d, %s, %s' % ( 1, title, mp3_url ) )
            return order, title, mp3_url
        except:
            logging.debug('info: %d, %s, %s' % ( 1, title, mp3_url ) )
            return 1, title, mp3_url

    #
    ## get the tuples in order
    ordered_npr_waitwait = sorted(
        filter(None, map(lambda episode_URL: get_npr_waitwait_story( episode_URL, date_s ), episode_urls ) ),
        key = lambda tup: tup[0] )
    assert( len( ordered_npr_waitwait ) == len( episode_urls ) )
    print( ordered_npr_waitwait )
    logging.info("finished getting list of stories for NPR Wait Wait episode: %s. Story list: %s." % (
        date_s, '\n'.join(map(lambda tup: '%s' % list(tup), ordered_npr_waitwait ) ) ) )
    return list(map(lambda tup: ( tup[1], tup[2] ), ordered_npr_waitwait ) )

def get_waitwait(
    outputdir, date_s, order_totnum = None, dump = False, driver = None, justFix = False ):
    """
    The main driver method that downloads `NPR Wait Wait <waitwait_>`_ episodes for a given date into a specified output directory.
    
    :param str outputdir: the directory into which one downloads the `NPR Wait Wait <waitwait_>`_ episodes.
    :param date_s: the :py:class:`date <datetime.date>` for this episode, which must be a weekday.
    :param tuple order_totnum: optional argument, the :py:class:`tuple` of track number and total number of tracks of `NPR Wait Wait <waitwait_>`_ episodes for that year. If ``None``, then this information is gathered from :py:meth:`get_order_num_saturday_in_year <nprstuff.core.npr_utils.get_order_num_saturday_in_year>`.
    :param bool dump: optional argument, if ``True`` returns the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` XML tree for the `NPR Wait Wait <waitwait_>`_ episode (and downloads the XML tree into a file). Default is ``False``.
    :param driver: optional argument, the :py:class:`Webdriver <selenium.webdriver.remote.webdriver.WebDriver>` used for webscraping and querying (instead of using a functional API) for `NPR Wait Wait <waitwait_>`_ episodes. If ``None``, then a new :py:class:`Webdriver <selenium.webdriver.remote.webdriver.WebDriver>` will be defined and used within this method's scope.
    :param bool justFix: optional argument, if ``True`` and if `NPR Wait Wait <waitwait_>`_ file exists, then just change the title of the M4A_ file. Default is ``False``.

    :returns: the name of the `NPR Wait Wait <waitwait_>`_ episode file.
    :rtype: str
    """
    # check if outputdir is a directory
    if not os.path.isdir(outputdir):
        raise ValueError("Error, %s is not a directory." % outputdir)
    
    # check if actually saturday
    if not npr_utils.is_saturday(date_s):
        raise ValueError(
            "Error, date = %s not a Saturday." % npr_utils.get_datestring(date_s) )

    #
    ## if driver is None
    if driver is None: driver = npr_utils.get_chrome_driver( )

    exec_dict = npr_utils.find_necessary_executables()
    assert( exec_dict is not None )
    avconv_exec = exec_dict['avconv']
    logging.debug('avconv exec = %s.' % avconv_exec )
  
    if order_totnum is None:
        order_totnum = npr_utils.get_order_number_saturday_in_year(date_s)
    order_in_year, tot_in_year = order_totnum
  
    file_data = get_waitwait_image( )
  
    year = date_s.year
    decdate = npr_utils.get_decdate( date_s )
    m4afile = os.path.join(outputdir, 'NPR.WaitWait.%s.m4a' % decdate )
    logging.info( 'INFO TO GET FIGURE OUT get_title_mp3s_url_working: %s, %s, %s, %s' % ( m4afile, date_s, driver, dump ) )
    if year >= 2006:
        data = get_title_mp3_urls_working( '.', date_s, driver, dump = dump )
        if dump: return data
        title_mp3_urls = data
        if title_mp3_urls is None or len( title_mp3_urls ) == 0: return None
        titles, songurls = list(zip(*title_mp3_urls))
        title = date_s.strftime('%B %d, %Y')
        title = '%s: %s.' % ( title,
                             '; '.join([ '%d) %s' % ( num + 1, titl ) for
                                    (num, titl) in enumerate(titles) ]) )
        if justFix:
            if not os.path.isfile( m4afile ):
                print( "Error, %s does not exist." % os.path.basename( m4afile ) )
                return
            mp4tags = mutagen.mp4.MP4(m4afile)
            mp4tags.tags['\xa9nam'] = [ title, ]
            mp4tags.save( )
            logging.info('fixed title for %s.' % m4afile )
            return m4afile

        logging.info('got here in NPR Wait Wait episode %s, title = %s.' % (
            date_s, title ) )
        
        # temporary directory
        tmpdir = tempfile.mkdtemp( )
        m4afile_temp = os.path.join( tmpdir,  'NPR.WaitWait.%s.m4a' % decdate )
        outfiles = [ os.path.join(tmpdir, 'waitwait.%s.%d.mp3' % 
                                  ( decdate, num + 1) ) for
                    (num, mp3url) in enumerate( songurls ) ]

        # download those files
        with multiprocessing.Pool( processes = min( multiprocessing.cpu_count( ), len( songurls ) ) ) as pool:
            outfiles = sorted( filter(None, pool.map( _download_file, zip( songurls, outfiles ) ) ) )
        
        # now convert to m4a file
        fnames = list(map(lambda filename: filename.replace(' ', '\ '), outfiles))
        avconv_concat_cmd = 'concat:%s' % '|'.join(fnames)
        split_cmd = [ avconv_exec, '-y', '-i', avconv_concat_cmd, '-ar', '44100', '-ac', '2', '-threads', 
                     '%d' % multiprocessing.cpu_count(), '-strict', 'experimental', '-acodec', 'aac',
                     m4afile_temp ]
        logging.info("here is the split command: %s." % split_cmd )
        proc = subprocess.Popen(split_cmd, stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        stdout_val, stderr_val = proc.communicate( )
        logging.debug("stdout_val: %s." % stdout_val )
        logging.debug("stderr_val: %s." % stderr_val )
        #
        ## remove mp3 files
        for filename in outfiles: os.remove(filename)
    else:
        tmpdir = tempfile.mkdtemp( )
        title = waitwait_realmedia.rm_get_title_from_url( date_s )
        rmfile = waitwait_realmedia.rm_download_file(
            date_s, outdir = tmpdir )
        wavfile = waitwait_realmedia.rm_create_wav_file(
            date_s, rmfile, outdir = tmpdir )
        os.remove( rmfile )
        #
        ## now convert to m4a file
        m4afile_temp = os.path.join(outputdir, 'NPR.WaitWait.%s.m4a' % decdate )
        split_cmd = [ avconv_exec, '-y', '-i', wavfile, '-ar', '44100',
                     '-ac', '2', '-threads', '%d' % multiprocessing.cpu_count(),
                     '-strict', 'experimental', '-acodec', 'aac', m4afile_temp ]
        proc = subprocess.Popen(split_cmd, stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        stdout_val, stderr_val = proc.communicate()
        #
        ## remove wav file
        os.remove( wavfile )
    #
    ## now put in metadata
    mp4tags = mutagen.mp4.MP4(m4afile_temp)
    mp4tags.tags['\xa9nam'] = [ title, ]
    mp4tags.tags['\xa9alb'] = [ "Wait Wait...Don't Tell Me: %d" % year, ]
    mp4tags.tags['\xa9ART'] = [ 'Peter Sagal', ]
    mp4tags.tags['\xa9day'] = [ '%d' % year, ]
    mp4tags.tags['\xa9cmt'] = [ "more info at : NPR Web site", ]
    mp4tags.tags['trkn'] = [ ( order_in_year, tot_in_year ), ]
    mp4tags.tags['covr'] = [ mutagen.mp4.MP4Cover(file_data, mutagen.mp4.MP4Cover.FORMAT_PNG ), ]
    mp4tags.tags['\xa9gen'] = [ 'Podcast', ]
    mp4tags.save()
    os.chmod( m4afile_temp, 0o644 )
    #
    ## now copy to actual location and remove temp directory
    shutil.copy( m4afile_temp, m4afile )
    shutil.rmtree( tmpdir )
    return m4afile
