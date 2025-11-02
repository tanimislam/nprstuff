import os, glob, datetime, json, logging
import time, re, titlecase, tempfile
import mutagen.mp4, subprocess, requests, shutil
from pathos.multiprocessing import Pool, cpu_count, ThreadPool
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from nprstuff.core import npr_utils
from nprstuff import resourceDir, nprstuff_logger as logger

_npr_FreshAir_progid = 13

def get_freshair_image( ):
    """
    Get the `NPR Fresh Air`_ logo as binary data.
    
    :returns: the `NPR Fresh Air logo`_ as binary data, see below.
    
    .. image:: /_static/fresh_air.png
       :width: 100%
       :align: center

    .. _`NPR Fresh Air`: https://freshair.npr.org
    .. _`NPR Fresh Air logo`: https://media.npr.org/images/podcasts/2013/primary/fresh_air.png
    """
    fa_image_file = os.path.join( resourceDir, 'fresh_air.png' )
    if os.path.isfile( fa_image_file ):
        return open( fa_image_file, 'rb' ).read( )
    #
    myURL = 'https://media.npr.org/images/podcasts/2013/primary/fresh_air.png'
    response = requests.get( myURL )
    with open( fa_image_file, 'wb' ) as openfile:
        openfile.write( response.content )
    return response.content

def _download_file( input_tuple ):
    mp3URL, filename = input_tuple
    resp = requests.get( mp3URL, stream = True )
    if not resp.ok:
        logger.error( 'SOMETHING HAPPENED WITH %s' % filename )
        return None
    #
    with open(filename, 'wb') as openfile:
        for chunk in resp.iter_content(65536):
            openfile.write( chunk )
    return filename

def get_freshair_date_from_name( candidateNPRFreshAirFile ):
    """
    :param str candidateNPRFreshAirFile: the name of the `NPR Fresh Air`_ episode file name.
    :returns: the :py:class:`date <datetime.date>` object from the `NPR Fresh Air`_ episode file name.
    :rtype: :py:class:`date <datetime.date>`
    """
    if not os.path.isfile(candidateNPRFreshAirFile):
        raise ValueError("Error, %s is not a file," % candidateNPRFreshAirFile )
    if not os.path.basename(candidateNPRFreshAirFile).endswith('.m4a'):
        raise ValueError("Error, %s does not end in .m4a" % candidateNPRFreshAirFile )
    if not os.path.basename(candidateNPRFreshAirFile).startswith('NPR.FreshAir.'):
        raise ValueError("Error, %s is not a valid file" % candidateNPRFreshAirFile )
    day, mon, year = list(
        map(lambda tok: int(tok),
            os.path.basename(candidateNPRFreshAirFile).split('.')[2:5] ) )
    return datetime.date(year, mon, day)
    
def get_freshair_valid_dates_remaining_tuples(yearnum, inputdir):
    """
    :param int yearnum: the year for which to search for missing `NPR Fresh Air`_ episodes.
    :param str inputfdir: the directory in which the `NPR Fresh Air`_ episodes live.
    :returns: a sorted :py:class:`list` of :py:class:`tuple`, ordered by candidate track number of the `NPR Fresh Air`_ episode. The :py:class:`tuple` has three elements: the track number of `NPR Fresh Air`_ episodes that year, the total number of `NPR Fresh Air`_ episodes that year, and the :py:class:`date <datetime.date>` for that episode.
    :rtype: list
    """
    freshair_files_downloaded = glob.glob( os.path.join(inputdir, 'NPR.FreshAir.*.%04d.m4a' % yearnum ) )
    dates_downloaded = set( [ get_freshair_date_from_name(filename) for filename in 
                             freshair_files_downloaded ] )
    all_order_weekdays = { date_s : (num+1) for (num, date_s) in
                          enumerate( npr_utils.get_weekday_times_in_year(yearnum) ) }
    dtime_now = datetime.datetime.now()
    nowd = datetime.date(dtime_now.year, dtime_now.month, dtime_now.day)
    weekdays_left = set( filter(lambda date_s: date_s <= nowd, set( all_order_weekdays.keys() ) ) ) - \
      set( dates_downloaded )
    totnum = len( all_order_weekdays.keys() )
    order_dates_remain = sorted(
        map(lambda date_s: ( all_order_weekdays[date_s], totnum, date_s ), weekdays_left ),
        key = lambda tup: tup[0] )
    return order_dates_remain

def _process_freshairs_by_year_tuple( input_tuple ):
    outputdir, totnum, datetimes_order_tuples = input_tuple
    for date_s, order in datetimes_order_tuples:
        time0 = time.perf_counter( )
        logging.debug( 'DATE = %s, order = %d, totnum = %d, outputdir = %s.' % (
            date_s, order, totnum, outputdir ) )
        try:
            fname = get_freshair(outputdir, date_s, order_totnum = ( order, totnum ) )
            if fname is None:
                logger.info( 'could not process freshair date = %s in %0.3f seconds.' % (
                    npr_utils.get_datestring( date_s ), time.perf_counter( ) - time0 ) )
                return
            logger.info( 'processed %s in %0.3f seconds.' % ( os.path.basename(fname), time.perf_counter( ) - time0 ) )
        except Exception as e:
            logger.error( str( e ) )
            logger.error('Could not create Fresh Air episode for date %s for some reason' %
                npr_utils.get_datestring( date_s ) )
            
def process_all_freshairs_by_year(yearnum, inputdir, justCoverage = False):
    """
    Either downloads all missing `NPR Fresh Air`_ episodes for a given year, or prints out a report of those missing episodes.
    
    :param int yearnum: the year for which to search for missing `NPR Fresh Air`_ episodes.
    :param str inputdir:  the directory in which the `NPR Fresh Air`_ episodes live.
    :param bool justCoverage: if ``True``, then only report on missing `NPR Fresh Air`_ episodes.

    .. seealso:: :py:meth:`get_freshair <nprstuff.core.freshair.get_freshair>`.
    """
    order_dates_remain = get_freshair_valid_dates_remaining_tuples( yearnum, inputdir )
    if len(order_dates_remain) == 0: return
    totnum = order_dates_remain[0][1]
    nprocs = cpu_count( )
    input_tuples = list(filter(
        lambda tup: len( tup[-1] ) != 0, [ ( inputdir, totnum,
                      [ ( date_s, order ) for ( order, totnum, date_s) in 
                       order_dates_remain if (order - 1) % nprocs == procno ] ) for
                    procno in range(nprocs) ] ) )
    time0 = time.perf_counter( )
    if not justCoverage:
        with npr_utils.MyPool(processes = min( cpu_count( ), len( input_tuples ) ) ) as pool:
            _ = list( pool.map(_process_freshairs_by_year_tuple, input_tuples) )
    else:
        print( 'Missing %d episodes for %04d.' % ( len(order_dates_remain), yearnum ) )
        for order, totnum, date_s in order_dates_remain:
            print( 'Missing NPR FreshAir episode for %s.' %
                  date_s.strftime('%B %d, %Y') )
    #
    logging.info( 'processed all Fresh Air downloads for %04d in %0.3f seconds.' %
                 ( yearnum, time.perf_counter( ) - time0 )  )

def _process_freshair_titlemp3_tuples( html ):
    def _get_title( story_elem ):
        all_http_lines = list(
            map(lambda line: line.strip(),
                filter(lambda line: len(line.strip()) > 0 and
                       line.strip().startswith('https'),
                       story_elem.text.split('\n') ) ) )
        story_line_url = all_http_lines[ 0 ]
        h2 = BeautifulSoup( requests.get( story_line_url ).content, 'html.parser' )
        title_elems = h2.find_all('title')
        if len( title_elems ) == 0: return None
        title = titlecase.titlecase(
            ': '.join(map(lambda tok: tok.strip( ),
                          title_elems[0].text.split(':')[:-1] ) ) )
        return title
    #
    titles = list(filter(None, map(_get_title, html.find_all('story'))))
    mp3s = list(
        map(lambda elem: requests.get( elem.text.strip( ) ).text.strip( ),
            html.find_all( 'mp3', { 'type' : 'm3u' } ) ) )
    title_mp3_urls = sorted(
        filter(None, zip( titles, mp3s ) ), key = lambda tup: tup[1] ) 
    return title_mp3_urls

def _process_freshair_titlemp3_tuples_planB( html ):
    def _get_title_mp3( story_elem ):
        url_line_elems = list( story_elem.find_all( 'a' ) )
        if len( url_line_elems ) != 1:
            return None
        url_line = url_line_elems[ 0 ]['href'].strip( )
        if not url_line.startswith( 'https' ):
            return None
        title = titlecase.titlecase(
            story_elem.text.strip( ) )
        #
        ## now get the mp3 file
        h2 = BeautifulSoup( requests.get( url_line ).content, 'html.parser' )
        mp3_elems = h2.find_all( 'a', { 'class' : 'audio-module-listen' } )
        if len( mp3_elems ) != 1:
            return None
        mp3_url_scheme = urlsplit( mp3_elems[ 0 ]['href' ].strip( ) )
        mp3_url = '%s://%s%s' % (
            mp3_url_scheme.scheme,
            mp3_url_scheme.netloc,
            mp3_url_scheme.path )
        return { 'title' : title, 'mp3' : mp3_url }

    title_mp3_list = list(filter(None, map( _get_title_mp3, html.find_all('h3', { 'class' : 'rundown-segment__title' } ) ) ) )
    return sorted( map(lambda entry: ( entry['title'], entry['mp3'] ), title_mp3_list ), key = lambda entry: entry[1] )

def _find_missing_dates(
    inputdir,
    mon, year = datetime.datetime.now( ).date( ).year ):
    """
    
    """
    def _process_freshair_perproc( mydate ):
        try:
            fname = get_freshair( inputdir, mydate )
            if fname is None: return None
            return mydate
        except Exception as e:
            print(e)
            return None
    #
    assert( mon in range(1, 13))
    weekdays_of_month = npr_utils.weekdays_of_month_of_year( year, mon )
    valid_filenames = set(map(
        lambda day: os.path.join(
            inputdir, 'NPR.FreshAir.%02d.%02d.%04d.m4a' % ( day, mon, year ) ),
        npr_utils.weekdays_of_month_of_year( year, mon ) ) )
    filenames_act = set(glob.glob(
        os.path.join( inputdir, 'NPR.FreshAir.*.%02d.%04d.m4a' % ( mon, year ) ) ) )
    filenames_remain = list(valid_filenames - filenames_act)
    if len( filenames_remain ) == 0: return
    print( 'NUMBER OF CANDIDATE EPS REMAIN FOR %d / %d: %d' % (
        mon, year, len( filenames_remain ) ) )
    days_remain = list( map(lambda filename: int(
        os.path.basename( filename ).split('.')[2] ), filenames_remain ) )
    input_tuples = list( map(lambda day: datetime.datetime.strptime(
        '%02d.%02d.%04d' % ( day, mon, year ),
        '%d.%m.%Y').date( ), days_remain ) )
    logger.info( 'list of input_tuples: %s.' % input_tuples )
    # pool = multiprocessing.Pool( processes = multiprocessing.cpu_count( ) )
    with ThreadPool( processes = min( cpu_count( ), len( input_tuples ) ) ) as pool:
        successes = list(
            filter(None, pool.map( _process_freshair_perproc, input_tuples ) ) )
    print( 'successes (%d/%d): %s' % ( len(successes), len(input_tuples), successes ) )
  
def _get_freshair_lowlevel( outputdir, date_s, titles ):
    # check if outputdir is a directory
    assert( os.path.isdir( outputdir ) )
    
    # check if actually a weekday
    assert( npr_utils.is_weekday(date_s) )
    
    # check if we have found avconv
    exec_dict = npr_utils.find_necessary_executables()
    avconv_exec = exec_dict['avconv']
    
    # order of FA episode in the year
    order_in_year, tot_in_year = npr_utils.get_order_number_weekday_in_year(date_s)
    
    # temporary output directory
    tmpdir = tempfile.mkdtemp( )
    
    file_data = get_freshair_image()
    decdate = date_s.strftime('%d.%m.%Y')
    m4afile = os.path.join(tmpdir, 'NPR.FreshAir.%s.m4a' % decdate )
    year = date_s.year
    
    def create_mp3_files( date_s, titles ):
        num_titles = len( titles )
        year = date_s.year
        mon = date_s.month
        day = date_s.day
        return list(map(lambda idx: 'https://ondemand.npr.org/anon.npr-mp3/npr/fa/%02d/%02d/%d%02d%02d_fa_%02d.mp3' % (
            year, mon, year, mon, day, idx ), range(1, num_titles + 1 ) ) )
    #
    songurls = create_mp3_files( date_s, titles )
    outfiles = [ os.path.join(tmpdir, 'freshair.%s.%d.mp3' % 
                              ( decdate, num + 1) ) for
                (num, mp3url) in enumerate( songurls ) ]
    #
    title = '%s: %s.' % (
        date_s.strftime('%A, %B %d, %Y'),
        '; '.join([ '%d) %s' % ( num + 1, titl ) for
                   (num, titl) in enumerate(titles) ]) )
    #
    ## download those files
    time0 = time.perf_counter( )
    with Pool(
        processes = min( cpu_count( ), len( songurls ) ) ) as pool:
        outfiles = list( filter(None, pool.map(_download_file, zip( songurls, outfiles ) ) ) )

    # create m4a file
    time0 = time.perf_counter( )
    fnames = [ filename.replace(' ', r'\ ') for filename in outfiles ]
    avconv_concat_cmd = 'concat:%s' % '|'.join(fnames)
    split_cmd = [ avconv_exec, '-y', '-i', avconv_concat_cmd, '-ar', '44100', '-ac', '2',
                 '-threads', '%d' % multiprocessing.cpu_count(),
                 '-strict', 'experimental', '-acodec', 'aac', m4afile ]
    logger.info( 'syntax for NPR Fresh Air %s: %s.' % (
        date_s, split_cmd ) )
    stdout_val = subprocess.check_output(split_cmd, stderr = subprocess.PIPE)
    
    # remove mp3 files
    for filename in outfiles: os.remove(filename)
    
    # now put in metadata
    mp4tags = mutagen.mp4.MP4(m4afile)
    mp4tags.tags['\xa9nam'] = [ title, ]
    mp4tags.tags['\xa9alb'] = [ 'Fresh Air From WHYY: %d' % year, ]
    mp4tags.tags['\xa9ART'] = [ 'Terry Gross', ]
    mp4tags.tags['\xa9day'] = [ '%d' % year, ]
    mp4tags.tags['\xa9cmt'] = [ "more info at : Fresh Air from WHYY and NPR Web site", ]
    mp4tags.tags['trkn'] = [ ( order_in_year, tot_in_year ), ]
    mp4tags.tags['covr'] = [ mutagen.mp4.MP4Cover(file_data, mutagen.mp4.MP4Cover.FORMAT_PNG ), ]
    mp4tags.tags['\xa9gen'] = [ 'Podcast', ]
    mp4tags.tags['aART'] = [ 'Terry Gross', ]
    mp4tags.save()
    os.chmod( m4afile, 0o644 )
  
    # now copy m4afile to actual directory and remove old directory
    m4afile_act = os.path.join( outputdir, os.path.basename( m4afile ) )
    shutil.copy( m4afile, m4afile_act )
    shutil.rmtree( tmpdir ) 
    return m4afile_act

def get_title_mp3_urls_attic( outputdir, date_s, debug = False, to_file_debug = True ):
    """
    older functionality that uses the `old NPR API` to get an ordered :py:class:`list` of :py:class:`tuple` of stories for an `NPR Fresh Air`_ episode. Here is an example operation,

    .. code-block:: python

       >> date_s = datetime.datetime.strptime('July 31, 2020', '%B %d, %Y' ).date( )
       >> title_mp3_urls = get_title_mp3_urls_attic( date_s )
       >> title_list_mp3_urls
       >> [('Remembering Regis Philbin, Prolific Talk and Game Show Personality',
         'https://ondemand.npr.org/anon.npr-mp3/npr/fa/2020/07/20200731_fa_01.mp3'),
        ("With 'Folklore,' Taylor Swift Marks Off Her Past and Enters a New Phase",
         'https://ondemand.npr.org/anon.npr-mp3/npr/fa/2020/07/20200731_fa_02.mp3'),
        ('Remembering Jazz Singer Annie Ross',
         'https://ondemand.npr.org/anon.npr-mp3/npr/fa/2020/07/20200731_fa_03.mp3'),
        ("'Muppets Now' Proves It's Not Easy to Capture the Old Muppet Magic",
         'https://ondemand.npr.org/anon.npr-mp3/npr/fa/2020/07/20200731_fa_04.mp3')]

    .. note::

       I was able to get this to work by replacing the ``https://`` in the API URL query with ``http://``.
       
    :param str outputdir: the directory into which one downloads the `NPR Fresh Air`_ episodes.
    :param date_s: the :py:class:`date <datetime.date>` for this episode, which must be a weekday.
    :param bool debug: optional argument, if ``True`` returns the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` XML tree for the `NPR Fresh Air`_ episode, or its file representation. Default is ``False``.
    :param bool to_file_debug: optional argument, if ``True`` dumps out the file representation of the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` XML tree for the `NPR Fresh Air`_ episode. Default is ``False``.
    :returns: the :py:class:`list` of stories, by order, for the `NPR Fresh Air`_ episode. The first element of each :py:class:`tuple` is the story title, and th second is the MP3_ URL for the story. *However*, if ``debug`` is ``True`` and ``to_file_debug`` is ``True``, returns the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` XML tree for this `NPR Fresh Air`_ episode.
    
    .. seealso::
    
       * :py:meth:`get_freshair <nprstuff.core.freshair.get_freshair>`.
       * :py:class:`get_title_mp3_urls_working <nprstuff.core.freshair.get_title_mp3_urls_working>`.
    """
    #
    ## download this data into a BeautifulSoup object
    resp = requests.get( 'http://api.npr.org/query',
                        params = {
                            'id'  : _npr_FreshAir_progid,
                            'date': date_s.strftime('%Y-%m-%d' ),
                            'dateType' : 'story',
                            'output' : 'NPRML',
                            'apiKey' : npr_utils.get_api_key( ) } )
    params = {
        'id'  : _npr_FreshAir_progid,
        'date': date_s.strftime('%Y-%m-%d' ),
        'dateType' : 'story',
        'output' : 'NPRML',
        'apiKey' : npr_utils.get_api_key( ) }
    full_URL = 'http://api.npr.org/query?%s' % (
        '&'.join(map(lambda tup: '%s=%s' % ( tup[0], tup[1] ), params.items())))
    print( full_URL )
    
    if not resp.ok:
        logger.info(
            'ERROR GETTING FRESH AIR STORY FOR %s' %
            date_s.strftime('%d %B %Y' ) )
        return None
    html = BeautifulSoup( resp.content, 'html.parser' )
    #
    if debug:
        print( 'URL = %s' % nprURL )
        if to_file_debug:
            decdate = date_s.strftime('%d.%m.%Y')
            with open(os.path.join(outputdir, 'NPR.FreshAir.tree.%s.xml' % decdate), 'w') as openfile:
                openfile.write( '%s\n' % html.prettify( ) )
        return html
    #
    ## check for unavailable tag
    if len( html.find_all('unavailable', { 'value' : 'true' } ) ) != 0:
        unavailable_elem = html.find_all('unavailable', { 'value' : 'true' } )[ 0 ]
        if unavailable_elem.text is None:
            print( 'Could not create Fresh Air episode for date %s because unavailable without a specific reason' %
                npr_utils.get_datestring( date_s ) )
        else:
            print( 'Could not create Fresh Air episode for date %s because unavailable for this reason: %s' % 
                ( npr_utils.get_datestring( date_s ), unavailable_elem.text.strip() ) )
        return None
    #
    ## now get tuple of title to mp3 file
    title_mp3_urls = _process_freshair_titlemp3_tuples( html )
    if title_mp3_urls is None or len(title_mp3_urls) == 0:
        print( 'Error, could not find any Fresh Air episodes for date %s.' %
              npr_utils.get_datestring( date_s ) )
        return None
    return title_mp3_urls

def get_title_mp3_urls_working_2023( date_s, debug = False ):
    """
    Maybe this works? Trying out on ``2023-08-18`` (day after my 45th birthday). Same format as :py:meth:`get_title_mp3_urls_working <nprstuff.core.freshair.get_title_mp3_urls_working>`. Example code block below:

    .. code-block:: python

       >> date_s = datetime.datetime.strptime('August 17, 2023', '%B %d, %Y' ).date( )
       >> title_mp3_urls = get_title_mp3_urls_working_2023( date_s )
       >> title_mp3_urls
       >> [("James McBride's 'Heaven & Earth' is an all-American mix of prejudice and hope",
         'https://ondemand.npr.org/anon.npr-mp3/npr/fa/2023/08/20230814_fa_16b06b61-ea8e-474b-bc59-f607b3538dad.mp3'),
        ("'Like it or not, we live in Oppenheimer's world,' says director Christopher Nolan",
         'https://ondemand.npr.org/anon.npr-mp3/npr/fa/2023/08/20230814_fa_66749637-ab88-4420-948c-0b1866bb239b.mp3')]

    :param date_s: the :py:class:`date <datetime.date>` for this episode, which must be a weekday.
    :type date_s: :py:class:`date <datetime.date>`
    :param bool debug: optional argument, if ``True`` returns the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` HTML tree for the `NPR Fresh Air`_ episode, or its file representation. Default is ``False``.
    :returns: the :py:class:`list` of stories, by order, for the `NPR Fresh Air`_ episode. The first element of each :py:class:`tuple` is the story title, and the second is the MP3_ URL for the story. Otherwise returns ``None``.
    :rtype: list
    """

    def _fix_title( my_string ):
      return titlecase.titlecase( re.sub( '&#39;', "'", my_string ).strip( ) )
    
    def _get_title_url_here( article_elem ):
        #
        ## first find candidate title
        candidate_title_elem = list(filter(lambda elem: 'class' in elem.attrs and 'audio-module-title' in elem['class'], article_elem.find_all( )))
        assert( len( candidate_title_elem ) != 0 )
        candidate_title_elem = candidate_title_elem[ 0 ]
        candidate_title = _fix_title( candidate_title_elem.text.strip( ) )
        #
        ## now get episode URL
        candidate_url_elem = list(filter(lambda elem: 'href' in elem.attrs and 'ondemand' in elem['href'], article_elem.find_all('a')))
        assert( len( candidate_url_elem ) != 0 )
        candidate_url_elem = candidate_url_elem[ 0 ]
        candidate_url = candidate_url_elem['href'].strip( ).split('?')[ 0 ]
        #
        ## now return the crap
        return { 'title' : candidate_title, 'url' : candidate_url }

    def _get_title_url_here_something( elem ):
        assert( 'title' in elem )
        candidate_title = _fix_title( elem[ 'title' ].strip( ) )
        #
        try:
            assert( 'audioUrl' in elem )
            candidate_url_split = urlsplit( elem[ 'audioUrl' ] )
            assert( candidate_url_split.scheme != '' )
            candidate_url = '%s://%s%s' % ( candidate_url_split.scheme, candidate_url_split.netloc, candidate_url_split.path )
            return { 'title' : candidate_title, 'url' : candidate_url }
        except Exception as e:
            pass
        assert( 'storyUrl' in elem )
        candidate_url_split = urlsplit( elem[ 'storyUrl' ] )
        assert( candidate_url_split.scheme != '' )
        candidate_url = '%s://%s%s' % ( candidate_url_split.scheme, candidate_url_split.netloc, candidate_url_split.path )
        return { 'title' : candidate_title, 'url' : candidate_url }

    def _plan_C2_get_title_url_here( story_elem ): # stuff tried out 2024-07-30
        url_line_elems = list( story_elem.find_all( 'a' ) )
        if len( url_line_elems ) != 1:
            return None
        url_line = url_line_elems[ 0 ]['href'].strip( )
        if not url_line.startswith( 'https' ):
            return None
        title = titlecase.titlecase(
            story_elem.text.strip( ) )
        #
        ## now get the mp3 file
        h2 = BeautifulSoup( requests.get( url_line ).content, 'html.parser' )
        mp3_elems = h2.find_all( 'a', { 'class' : 'audio-module-listen' } )
        if len( mp3_elems ) != 1:
            return None
        mp3_url_scheme = urlsplit( mp3_elems[ 0 ]['href' ].strip( ) )
        mp3_url = '%s://%s%s' % (
            mp3_url_scheme.scheme,
            mp3_url_scheme.netloc,
            mp3_url_scheme.path )
        return { 'title' : title, 'url' : mp3_url }

        #title_mp3_list = list(filter(None, map( _get_title_mp3, html.find_all('h3', { 'class' : 'rundown-segment__title' } ) ) ) )
        # return sorted( map(lambda entry: ( entry['title'], entry['mp3'] ), title_mp3_list ), key = lambda entry: entry[1] )


    def _plan_C_get_title_url_here( elem ):
      data_here = json.loads( elem[ 'data-metrics-ga4' ] )
      assert( 'title' in data_here )
      candidate_title = _fix_title( data_here[ 'title' ].strip( ) )
      #
      ## now get the episode URL
      embed_url = elem['data-embed-url']
      resp = requests.get( embed_url )
      assert( resp.ok )
      assert( resp.status_code == 200 )
      myhtml2 = BeautifulSoup( resp.content, 'html.parser' )
      #
      ## now look through those codes that are unempty
      valid_script_elems = list(filter(lambda elem: len( elem.text.strip( ) ) != 0 and 'audioModel' in elem.text,
                                       myhtml2.find_all( 'script', { 'type' : 'text/javascript' } ) ) )
      assert( len( valid_script_elems ) == 1 )
      valid_script_elem = valid_script_elems[ 0 ]
      valid_json_text = '='.join( valid_script_elem.text.strip( ).split('=')[1:] ).strip( )
      valid_json_text = re.sub(';$', '', valid_json_text ).strip( )
      data_json = json.loads( valid_json_text )
      assert( 'audioSrc' in data_json )
      candidate_url_split = urlsplit( data_json[ 'audioSrc' ] )
      candidate_url = '%s://%s%s' % ( candidate_url_split.scheme, candidate_url_split.netloc, candidate_url_split.path )
      return { 'title' : candidate_title, 'url' : candidate_url }
      
    try:
        #
        ## STEP #1: do an archive search
        resp = requests.get(
            'https://www.npr.org/programs/fresh-air/archive',
            params = { 'date' : date_s.strftime('%m-%d-%Y') } )
        assert( resp.ok )
        assert( resp.status_code == 200 )
        myhtml = BeautifulSoup( resp.content, 'html.parser' )
        archive_elem = list(filter(lambda elem: 'data-episode-date' in elem.attrs and date_s.strftime('%Y-%m-%d') in elem['data-episode-date'], myhtml.find_all('article' )))
        assert( len( archive_elem ) != 0 )
        archive_elem = archive_elem[ 0 ]
        article_url_elem = list(filter(lambda elem: 'href' in elem.attrs and 'fresh-air' in elem['href'], archive_elem.find_all('a')))
        assert( len( article_url_elem ) != 0 )
        article_url_elem = article_url_elem[ 0 ]
        article_url_split = urlsplit( article_url_elem['href'].strip( ) )
        article_url = '%s://%s%s' % ( article_url_split.scheme, article_url_split.netloc, article_url_split.path )
        logger.info( 'URL TO GET = %s.' % article_url )
        #
        ## first get the info
        resp = requests.get( article_url )
        assert( resp.ok )
        assert( resp.status_code == 200 )
        #
        ## now find all the elems that have story-list, assert ONLY single story-list elem
        myhtml = BeautifulSoup( resp.content, 'html.parser' )
        if debug:
            print( 'URL = %s' % article_url )
            return myhtml
        try:
            story_list_elems = myhtml.find_all( 'div', { 'class' : 'story-list' } )
            assert( len( story_list_elems ) == 1 )
            story_list_elem = story_list_elems[ 0 ]
            article_infos_in_order = sorted(
                map(_get_title_url_here, story_list_elem.find_all( 'article', { 'class' : 'rundown-segment' } ) ),
                key = lambda entry: entry[ 'url' ] )
            if len( article_infos_in_order ) == 0:
                raise ValueError("FAILED PLAN A: length of articles = 0")
            if any(map(lambda entry: len( entry['title'].strip( ) ) <= 20, article_infos_in_order ) ):
                raise ValueError( "FAILED ON PLAN A: length of any of the titles is <= 0")
            logging.info( 'PLAN A: %s' % article_infos_in_order )
            return list(map(lambda entry: ( entry['title'], entry['url'] ), article_infos_in_order))
        except Exception as e:
            logging.info( "PROBLEM GETTING PLAN A: %s." % str( e ) )
            pass
        #
        ## otherwise PLAN B do the needful, see if this works...
        try:
            actual_elems = list(filter(lambda elem: 'data-play-all' in elem.attrs, myhtml.find_all('b')))
            assert( len( actual_elems ) != 0 )
            actual_elem = actual_elems[ 0 ]
            data = json.loads( actual_elem['data-play-all'] )
            assert( 'audioData' in data )
            data_audio = data[ 'audioData' ]
            #
            article_infos_in_order = sorted(
                map(_get_title_url_here_something, data_audio ),
                key = lambda entry: entry[ 'url' ] )
            if len( article_infos_in_order ) == 0:
                raise ValueError( "ERROR, PLAN B: length of articles = 0" )

            #
            ## now perform more sewage-processing of crappy NPR Fresh Air results
            bad_elems = list(filter(lambda elem: not elem['url'].endswith( '.mp3' ), article_infos_in_order ) )
            if len( bad_elems ) == 1:
                possible_story_urls = set(
                    map(lambda idx:
                        'https://ondemand.npr.org/anon.npr-mp3/npr/fa/%d/%02d/%s_fa_%02d.mp3' % (
                            date_s.year, date_s.month, date_s.strftime( '%Y%m%d' ), idx ), range(1, len( article_infos_in_order ) + 1 ) ) )
                possible_story_rems = possible_story_urls - set(map(lambda elem: elem['url'], article_infos_in_order ) )
                assert( len( possible_story_rems ) == 1 )
                rem_story = max( possible_story_rems )
                for elem in article_infos_in_order:
                    if elem['url'].endswith( '.mp3' ): continue
                    elem[ 'url' ] = rem_story
                logging.info( 'PLAN B: %s' % article_infos_in_order )
                return list(map(lambda entry: ( entry['title'], entry['url'] ), article_infos_in_order))
            
            raise ValueError("FAILED PLAN B: length of articles = 0")
        except Exception as e:
            logging.info( "PROBLEM GETTING PLAN B: %s." % str( e ) )
            pass
        #
        ## otherwise PLAN C what the fuck??
        # actual_elems = list(filter(lambda elem: 'data-embed-url' in elem.attrs and 'data-metrics-ga4' in elem.attrs, myhtml.find_all()))
        actual_elems = myhtml.find_all('h3', { 'class' : 'rundown-segment__title' } )
        assert( len( actual_elems ) != 0 )
        article_infos_in_order = sorted(
            map(_plan_C2_get_title_url_here, actual_elems ),
            key = lambda entry: entry[ 'url' ] )
        return list(map(lambda entry: ( entry['title'], entry['url'] ), article_infos_in_order))
    except Exception as e:
        logger.info( str( e ) )
        return None
    

def get_title_mp3_urls_working( outputdir, date_s, driver, debug = False, to_file_debug = True, relax_date_check = False ):
    """
    Using the new, non-API NPR functionality, get a :py:class:`list` of :py:class:`tuple` of stories for an `NPR Fresh Air`_ episode. This uses a :py:class:`Webdriver <selenium.webdriver.remote.webdriver.WebDriver>` to get an episode. Here is an example operation,

    .. code-block:: python

       >> date_s = datetime.datetime.strptime('July 31, 2020', '%B %d, %Y' ).date( )
       >> title_mp3_urls = get_title_mp3_urls_working( date_s, driver )
       >> title_list_mp3_urls
       >> [('Remembering Regis Philbin, Prolific Talk and Game Show Personality',
         'https://ondemand.npr.org/anon.npr-mp3/npr/fa/2020/07/20200731_fa_01.mp3'),
        ("With 'Folklore,' Taylor Swift Marks Off Her Past and Enters a New Phase",
         'https://ondemand.npr.org/anon.npr-mp3/npr/fa/2020/07/20200731_fa_02.mp3'),
        ('Remembering Jazz Singer Annie Ross',
         'https://ondemand.npr.org/anon.npr-mp3/npr/fa/2020/07/20200731_fa_03.mp3'),
        ("'Muppets Now' Proves It's Not Easy to Capture the Old Muppet Magic",
         'https://ondemand.npr.org/anon.npr-mp3/npr/fa/2020/07/20200731_fa_04.mp3')]

    :param date_s: the :py:class:`date <datetime.date>` for this episode, which must be a weekday.
    :param driver: the :py:class:`Webdriver <selenium.webdriver.remote.webdriver.WebDriver>` used for webscraping and querying (instead of using a functional API) for `NPR Fresh Air`_ episodes.
    :param bool debug: optional argument, if ``True`` returns the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` XML tree for the `NPR Fresh Air`_ episode, or its file representation. Default is ``False``.
    :param bool to_file_debug: optional argument, if ``True`` dumps out the file representation of the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` XML tree for the `NPR Fresh Air`_ episode. Default is ``False``.
    :param bool relax_date_check: optional argument, if ``True`` then do NOT check for article date in NPR stories. Default is ``False``.

    :returns: the :py:class:`list` of stories, by order, for the `NPR Fresh Air`_ episode. The first element of each :py:class:`tuple` is the story title, and th second is the MP3_ URL for the story. *However*, if ``debug`` is ``True``, returns the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` XML tree for this `NPR Fresh Air`_ episode.

    .. seealso::
    
       * :py:meth:`get_freshair <nprstuff.core.freshair.get_freshair>`.
       * :py:class:`get_title_mp3_urls_attic <nprstuff.core.freshair.get_title_mp3_urls_attic>`.
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
    time0 = time.perf_counter( )
    dt_end = datetime.datetime( date_s.year, date_s.month, date_s.day )
    t_end = int( datetime.datetime.timestamp( dt_end ) )
    #
    ## now get using the driver, go to the URL defined there
    mainURL =  'https://www.npr.org/search?query=*&page=1&refinementList[shows]=Fresh Air&range[lastModifiedDate][min]=%d&range[lastModifiedDate][max]=%d&sortType=byDateAsc' % ( t_end - 86400, t_end )
    driver.get( mainURL )
    #time.sleep( 1.5 ) # is 1.5 seconds enough?
    WebDriverWait(driver, 10).until( condition )
    html = BeautifulSoup( driver.page_source, 'html.parser' )
    if debug:
        print( 'URL = %s' % mainURL )
        if to_file_debug:
            decdate = date_s.strftime('%d.%m.%Y')
            with open(os.path.join(outputdir, 'NPR.FreshAir.tree.%s.xml' % decdate), 'w') as openfile:
                openfile.write( '%s\n' % html.prettify( ) )
        return html
    
    episode_elems = html.find_all('h2', { 'class' : 'title' } )
    episode_urls = list(map(lambda elem: urljoin( 'https://www.npr.org', elem.find_all('a')[0]['href'] ), episode_elems ) )
    #
    def _get_npr_freshair_story( episode_URL, candidate_date, relax_date_check = False ):
        response = requests.get( episode_URL )
        assert( response.ok )
        html_ep = BeautifulSoup( response.content, 'html.parser' )
        if not relax_date_check:
            date_f = candidate_date.strftime( '%Y-%m-%d' )
            date_elems = list(html_ep.find_all('meta', { 'name' : 'date', 'content' : date_f } ) )
            if len( date_elems ) != 1:
                logger.error( 'could not find date elem for %s, candidate date = %s' % ( episode_URL, date_f ) )
                return None
        #
        ## keep going, get the title    
        title_elems = list(html_ep.find_all('title'))
        if len( title_elems ) == 0:
            logger.error( 'could not find title elem for %s.' % episode_URL )
            return None
        title = titlecase.titlecase( ' '.join(map(lambda tok: tok.strip(), title_elems[0].text.split(':')[:-1])) )
        #
        ## now get the MP3 URL
        mp3_elems = list(filter(lambda elem: 'href' in elem.attrs and 'mp3' in elem['href'], html_ep.find_all('a')))
        if len( mp3_elems ) == 0: return None
        mp3_elem = mp3_elems[0]
        mp3_url_split = urlsplit( mp3_elem['href'] )
        mp3_url = urljoin( 'https://%s' % mp3_url_split.netloc, mp3_url_split.path )
        #
        ## now get order
        mp3_url_sub = re.sub(r'_rev\.mp3$', '', mp3_url).strip( )
        logger.debug( 'MP3 URL = %s.' % mp3_url_sub )
        bname = re.sub('_$', '', os.path.basename( mp3_url_sub ).split('.')[0].strip( ) ).strip( )
        order = int( bname.split('_')[-1] )
        #
        ## return tuple of order, title, URL
        return order, title, mp3_url
    #
    ## get the tuples in order
    ordered_npr_freshair = sorted(filter(None, map(lambda episode_URL: _get_npr_freshair_story( episode_URL, date_s, relax_date_check ), episode_urls ) ),
                                  key = lambda tup: tup[0] )
    assert( len( ordered_npr_freshair ) == len( episode_urls ) )
    return list(map(lambda tup: ( tup[1], tup[2] ), ordered_npr_freshair ) )

def get_freshair(
    outputdir, date_s, order_totnum = None,
    debug = False, check_if_exist = False,
    mp3_exist = False, relax_date_check = False, to_file_debug = True ):
    """
    The main driver method that downloads `NPR Fresh Air`_ episodes for a given date into a specified output directory.
    
    :param str outputdir: the directory into which one downloads the `NPR Fresh Air`_ episodes.
    :param date_s: the :py:class:`date <datetime.date>` for this episode, which must be a weekday.
    :type date_s: :py:class:`date <datetime.date>`
    :param tuple order_totnum: optional argument, the :py:class:`tuple` of track number and total number of tracks of `NPR Fresh Air`_ episodes for that year. If ``None``, then this information is gathered from :py:meth:`get_order_num_weekday_in_year <nprstuff.core.npr_utils.get_order_num_weekday_in_year>`.
    :param bool debug: optional argument, if ``True`` returns the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` HTML tree for the `NPR Fresh Air`_ episode, or its file representation. Default is ``False``.
    :param bool check_if_exist: optional argument, if ``True`` and if the correct file name for the `NPR Fresh Air`_ episode exists, then won't overwrite it. Default is ``False``.
    :param bool mp3_exist: optional argument, if ``True`` then check whether the transitional MP3_ files for the stories in the `NPR Fresh Air`_ episode has been downloaded and use the fully downloaded stories to compose an episode. Otherwise, ignore existing downloaded MP3_ stories for download.
    :param bool relax_date_check: optional argument, if ``True`` then do NOT check for article date in NPR stories. Default is ``False``.
    :param bool to_file_debug: optional argument, if ``True`` and ``debug`` is ``True``, then dump into an XML file. If ``False`` and ``debug`` is ``True``, then returns the :py:class:`list` of :py:class:`tuple` that :py:meth:`get_title_mp3_urls_working_2023 <nprstuff.core.freshair.get_title_mp3_urls_working_2023>` returns.

    :returns: the name of the `NPR Fresh Air`_ episode file.
    :rtype: str

    .. _seealso: :py:meth:`get_title_mp3_urls_working_2023 <nprstuff.core.freshair.get_title_mp3_urls_working_2023>`

    .. _MP3: https://en.wikipedia.org/wiki/MP3
    """
    # check if outputdir is a directory
    if not os.path.isdir(outputdir):
        raise ValueError("Error, %s is not a directory." % outputdir)
  
    # check if actually a weekday
    assert( npr_utils.is_weekday(date_s) )
    
    # check if we have found avconv
    exec_dict = npr_utils.find_necessary_executables()
    assert( exec_dict is not None )
    avconv_exec = exec_dict['avconv']
    
    if order_totnum is None:
        order_totnum = npr_utils.get_order_number_weekday_in_year(date_s)
    order_in_year, tot_in_year = order_totnum
  
    file_data = get_freshair_image()
    
    decdate = date_s.strftime('%d.%m.%Y')
    m4afile_init = os.path.join(outputdir, 'NPR.FreshAir.%s.m4a' % decdate )
    if check_if_exist and os.path.isfile(m4afile_init): return
    
    year = date_s.year
    
    #data = get_title_mp3_urls_working(
    #    outputdir, date_s, driver, debug = debug, to_file_debug = to_file_debug,
    #    relax_date_check = relax_date_check )
    #if debug: return data
    if debug:
        myhtml = get_title_mp3_urls_working_2023( date_s, debug = True )
        if not to_file_debug: return myhtml
        #
        decdate = date_s.strftime('%d.%m.%Y')
        outputfile = os.path.join(outputdir, 'NPR.FreshAir.tree.%s.html' % decdate)
        with open( outputfile, 'w') as openfile:
            openfile.write( '%s\n' % myhtml.prettify( ) )
        return outputfile
    title_mp3_urls = get_title_mp3_urls_working_2023( date_s, debug = False )
    if title_mp3_urls is None or len( title_mp3_urls ) == 0: return None

    # temporary directory
    tmpdir = tempfile.mkdtemp( )
    m4afile_temp = os.path.join(tmpdir, 'NPR.FreshAir.%s.m4a' % decdate )
    m4afile = os.path.join(outputdir, 'NPR.FreshAir.%s.m4a' % decdate )
    
    titles, songurls = list(zip(*title_mp3_urls))
    outfiles = [ os.path.join(tmpdir, 'freshair.%s.%d.mp3' % 
                              ( decdate, num + 1) ) for
                (num, mp3url) in enumerate( songurls ) ]
    if mp3_exist:
        assert(all(map(lambda outfile: os.path.isfile( outfile ), outfiles) ) )
    
    title = date_s.strftime('%A, %B %d, %Y')
    title = '%s: %s.' % ( title,
                         '; '.join([ '%d) %s' % ( num + 1, titl ) for
                                    (num, titl) in enumerate(titles) ]) )    
    
    # download those files
    time0 = time.perf_counter( )
    if not mp3_exist:
        with Pool(processes = len(songurls) ) as pool:
            outfiles = list( filter(None, pool.map(_download_file, zip( songurls, outfiles ) ) ) )

    # now convert to m4a file
    # /usr/bin/avconv -y -i freshair$wgdate.wav -ar 44100 -ac 2 -aq 400 -acodec libfaac NPR.FreshAir."$decdate".m4a ;
    time0 = time.perf_counter( )
    fnames = [ filename.replace(' ', r'\ ') for filename in outfiles ]
    avconv_concat_cmd = 'concat:%s' % '|'.join(fnames)
    split_cmd = [
        avconv_exec, '-y', '-i', avconv_concat_cmd, '-ar', '44100', '-ac', '2',
        '-threads', '%d' % cpu_count( ),
        '-strict', 'experimental', '-acodec', 'aac', m4afile_temp ]
    stdout_val = subprocess.check_output(split_cmd, stderr = subprocess.PIPE)
    #
    ## remove mp3 files
    for filename in outfiles: os.remove(filename)
    #
    ## now put in metadata
    mp4tags = mutagen.mp4.MP4( m4afile_temp )
    mp4tags.tags['\xa9nam'] = [ title, ]
    mp4tags.tags['\xa9alb'] = [ 'Fresh Air From WHYY: %d' % year, ]
    mp4tags.tags['\xa9ART'] = [ 'Terry Gross', ]
    mp4tags.tags['\xa9day'] = [ '%d' % year, ]
    mp4tags.tags['\xa9cmt'] = [ "more info at : Fresh Air from WHYY and NPR Web site", ]
    mp4tags.tags['trkn'] = [ ( order_in_year, tot_in_year ), ]
    mp4tags.tags['covr'] = [ mutagen.mp4.MP4Cover(file_data, mutagen.mp4.MP4Cover.FORMAT_PNG ), ]
    mp4tags.tags['\xa9gen'] = [ 'Podcast', ]
    mp4tags.tags['aART'] = [ 'Terry Gross', ]
    mp4tags.save()
    os.chmod( m4afile_temp, 0o644 )
    #
    ## copy file to outputdir, and remove directories
    shutil.copy( m4afile_temp, m4afile )
    shutil.rmtree( tmpdir )
    return m4afile
