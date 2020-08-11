import os, glob, datetime
import time, re, titlecase, tempfile, logging
import mutagen.mp4, subprocess, requests, shutil
import pathos.multiprocessing as multiprocessing
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from nprstuff.core import npr_utils

_npr_FreshAir_progid = 13

def get_freshair_image():
  myURL = 'http://media.npr.org/images/podcasts/2013/primary/fresh_air.png'
  return requests.get( myURL ).content

def _download_file(input_tuple):
  mp3URL, filename = input_tuple
  resp = requests.get( mp3URL, stream = True )
  if not resp.ok:
    print('SOMETHING HAPPENED WITH %s' % filename)
    return None
  
  with open(filename, 'wb') as openfile:
    for chunk in resp.iter_content(65536):
      openfile.write( chunk )
    return filename

def get_freshair_date_from_name(candidateNPRFreshAirFile):
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
    outputdir, totnum, verbose, datetimes_order_tuples = input_tuple
    fa_image = get_freshair_image( )
    driver = npr_utils.get_chrome_driver( )
    for date_s, order in datetimes_order_tuples:
        time0 = time.time()
        try:
            fname = get_freshair(outputdir, date_s, order_totnum = ( order, totnum ),
                                 file_data = fa_image, driver = driver )
            if verbose:
                print( 'processed %s in %0.3f seconds.' % ( os.path.basename(fname), time.time() - time0 ) )
        except Exception:
            print('Could not create Fresh Air episode for date %s for some reason' %
                npr_utils.get_datestring( date_s ) )
            
def process_all_freshairs_by_year(yearnum, inputdir, verbose = True, justCoverage = False):
    order_dates_remain = get_freshair_valid_dates_remaining_tuples( yearnum, inputdir )
    if len(order_dates_remain) == 0: return
    totnum = order_dates_remain[0][1]
    nprocs = multiprocessing.cpu_count() 
    input_tuples = [ ( inputdir, totnum, verbose, 
                      [ ( date_s, order ) for ( order, totnum, date_s) in 
                       order_dates_remain if (order - 1) % nprocs == procno ] ) for
                    procno in range(nprocs) ]
    time0 = time.time()
    if not justCoverage:
        with multiprocessing.Pool(processes = multiprocessing.cpu_count()) as pool:
            pool.map(_process_freshairs_by_year_tuple, input_tuples)
    else:
        print( 'Missing %d episodes for %04d.' % ( len(order_dates_remain), yearnum ) )
        for order, totnum, date_s in order_dates_remain:
            print( 'Missing NPR FreshAir episode for %s.' %
                  date_s.strftime('%B %d, %Y') )
    #
    if verbose:
        print( 'processed all Fresh Air downloads for %04d in %0.3f seconds.' %
              ( yearnum, time.time() - time0 )  )

def process_freshair_titlemp3_tuples( html ):
    def _get_title( story_elem ):
        all_http_lines = list(
        map(lambda line: line.strip(),
            filter(lambda line: len(line.strip()) > 0 and
                   line.strip().startswith('https'),
                   story_elem.text.split('\n') ) ) )
        story_line_url = all_http_lines[ 0 ]
        h2 = BeautifulSoup( requests.get( story_line_url ).content, 'lxml' )
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

def find_missing_dates(
    inputdir,
    mon, year = datetime.datetime.now( ).date( ).year ):
  def _process_freshair_perproc( mydate ):
    try:
      fname = get_freshair( inputdir, mydate )
      if fname is None: return None
      return mydate
    except Exception as e:
      print(e)
      return None
  
  assert( mon in range(1, 13))
  weekdays_of_month = npr_utils.weekdays_of_month_of_year( year, mon )
  valid_filenames = set(map(
    lambda day:
    os.path.join(
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
  # pool = multiprocessing.Pool( processes = multiprocessing.cpu_count( ) )
  successes = list(
    filter(None, map( _process_freshair_perproc, input_tuples ) ) )
  print( 'successes (%d/%d): %s' % ( len(successes), len(input_tuples), successes ) )
  
def get_freshair_lowlevel( outputdir, date_s, titles ):
  # check if outputdir is a directory
  if not os.path.isdir(outputdir):
    raise ValueError("Error, %s is not a directory." % outputdir)
  
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

  songurls = create_mp3_files( date_s, titles )
  outfiles = [ os.path.join(tmpdir, 'freshair.%s.%d.mp3' % 
                            ( decdate, num + 1) ) for
               (num, mp3url) in enumerate( songurls ) ]
  
  title = '%s: %s.' % (
    date_s.strftime('%A, %B %d, %Y'),
    '; '.join([ '%d) %s' % ( num + 1, titl ) for
                (num, titl) in enumerate(titles) ]) )

  # download those files
  time0 = time.time()
  with multiprocessing.Pool(
      processes = min( multiprocessing.cpu_count( ), len( songurls ) ) ) as pool:
    outfiles = list( filter(None, pool.map(_download_file, zip( songurls, outfiles ) ) ) )

  # create m4a file
  time0 = time.time()
  fnames = [ filename.replace(' ', '\ ') for filename in outfiles ]
  avconv_concat_cmd = 'concat:%s' % '|'.join(fnames)
  split_cmd = [ avconv_exec, '-y', '-i', avconv_concat_cmd, '-ar', '44100', '-ac', '2',
                '-threads', '%d' % multiprocessing.cpu_count(),
                '-strict', 'experimental', '-acodec', 'aac', m4afile ]
  proc = subprocess.Popen(split_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout_val, stderr_val = proc.communicate()
    
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

def _get_title_mp3_urls_attic( date_s, debug = False, to_file_debug = True ):
    #
    ## download this data into a BeautifulSoup object
    resp = requests.get( 'https://api.npr.org/query',
                        params = {
                            'id'  : _npr_FreshAir_progid,
                            'date': date_s.strftime('%Y-%m-%d' ),
                            'dateType' : 'story',
                            'output' : 'NPRML',
                            'apiKey' : npr_utils.get_api_key( ) } )
    # resp = requests.get( nprURL )
    if resp.status_code != 200:
        logging.debug('ERROR GETTING FRESH AIR STORY FOR %s' %
                      date_s.strftime('%d %B %Y' ) )
        return None
    html = BeautifulSoup( resp.content, 'lxml' )
    #
    if debug:
        # print 'URL = %s' % nprURL
        if to_file_debug:
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
    title_mp3_urls = process_freshair_titlemp3_tuples( html )
    if len(title_mp3_urls) == 0:
        print( 'Error, could not find any Fresh Air episodes for date %s.' %
              npr_utils.get_datestring( date_s ) )
        return None
    return title_mp3_urls

def get_title_mp3_urls_working( date_s, driver ):
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
    ## now get the firefox driver, go to the URL defined there
    mainURL =  'https://www.npr.org/search?query=*&page=1&refinementList[shows]=Fresh Air&range[lastModifiedDate][min]=%d&range[lastModifiedDate][max]=%d&sortType=byDateAsc' % ( t_end - 86400, t_end )
    driver.get( mainURL )
    time.sleep( 1.5 ) # is 1.5 seconds enough?
    #WebDriverWait(driver, 10).until( condition )
    html = BeautifulSoup( driver.page_source, 'lxml' )
    episode_elems = html.find_all('h2', { 'class' : 'title' } )
    episode_urls = list(map(lambda elem: urljoin( 'https://www.npr.org', elem.find_all('a')[0]['href'] ), episode_elems ) )
    #
    def get_npr_freshair_story( episode_URL, candidate_date ):
        response = requests.get( episode_URL )
        assert( response.ok )
        html_ep = BeautifulSoup( response.content, 'lxml' )
        date_f = candidate_date.strftime( '%Y-%m-%d' )
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
        mp3_elems = list(filter(lambda elem: 'href' in elem.attrs and 'mp3' in elem['href'], html_ep.find_all('a')))
        if len( mp3_elems ) == 0: return None
        mp3_elem = mp3_elems[0]
        mp3_url_split = urlsplit( mp3_elem['href'] )
        mp3_url = urljoin( 'https://%s' % mp3_url_split.netloc, mp3_url_split.path )
        #
        ## now get order
        order = int( os.path.basename( mp3_url ).split('.')[0].split('_')[-1] )
        #
        ## return tuple of order, title, URL
        return order, title, mp3_url
    #
    ## get the tuples in order
    ordered_npr_freshair = sorted(filter(None, map(lambda episode_URL: get_npr_freshair_story( episode_URL, date_s ), episode_urls ) ),
                                  key = lambda tup: tup[0] )
    assert( len( ordered_npr_freshair ) == len( episode_urls ) )
    return list(map(lambda tup: ( tup[1], tup[2] ), ordered_npr_freshair ) )

def get_freshair(
    outputdir, date_s, order_totnum = None,
    file_data = None, debug = False,
    exec_dict = None, check_if_exist = False,
    mp3_exist = False, to_file_debug = True, driver = None ):

    #
    # if cannot find the driver
    if driver is None: driver = npr_utils.get_chrome_driver( )
    
    # check if outputdir is a directory
    if not os.path.isdir(outputdir):
        raise ValueError("Error, %s is not a directory." % outputdir)
  
    # check if actually a weekday
    assert( npr_utils.is_weekday(date_s) )
    
    # check if we have found avconv
    if exec_dict is None:
        exec_dict = npr_utils.find_necessary_executables()
    assert( exec_dict is not None )
    avconv_exec = exec_dict['avconv']
    
    if order_totnum is None:
        order_totnum = npr_utils.get_order_number_weekday_in_year(date_s)
    order_in_year, tot_in_year = order_totnum
  
    if file_data is None: file_data = get_freshair_image()
    
    decdate = date_s.strftime('%d.%m.%Y')
    m4afile_init = os.path.join(outputdir, 'NPR.FreshAir.%s.m4a' % decdate )
    if check_if_exist and os.path.isfile(m4afile_init): return
    
    #nprURL = npr_utils.get_NPR_URL(date_s, _npr_FreshAir_progid, 
    #                               npr_utils.get_api_key() )
    year = date_s.year
    
    title_mp3_urls = get_title_mp3_urls_working( date_s, driver )
    if len( title_mp3_urls ) == 0: return None
    if title_mp3_urls is None: return None

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
    time0 = time.time()
    if not mp3_exist:
        with multiprocessing.Pool(processes = len(songurls) ) as pool:
            outfiles = list( filter(None, pool.map(_download_file, zip( songurls, outfiles ) ) ) )
   
    # sox magic command
    #wgdate = date_s.strftime('%d-%b-%Y')
    #wavfile = os.path.join(outputdir, 'freshair%s.wav' % wgdate ).replace(' ', '\ ')
    #split_cmd = [ '(for', 'file', 'in', ] + fnames + [ 
    #    ';', sox_exec, '$file', '-t', 'cdr', '-', ';', 'done)' ] + [ 
    #        '|', sox_exec, 't-', 'cdr', '-', wavfile ]
    #split_cmd = [ sox_exec, ] + fnames + [ wavfile, ]
    #print split_cmd
    #return
    #proc = subprocess.Popen(split_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    #stdout_val, stderr_val = proc.communicate()
    #for filename in outfiles:
    #    os.remove(filename)

    # now convert to m4a file
    # /usr/bin/avconv -y -i freshair$wgdate.wav -ar 44100 -ac 2 -aq 400 -acodec libfaac NPR.FreshAir."$decdate".m4a ;
    time0 = time.time()
    fnames = [ filename.replace(' ', '\ ') for filename in outfiles ]
    avconv_concat_cmd = 'concat:%s' % '|'.join(fnames)
    split_cmd = [
        avconv_exec, '-y', '-i', avconv_concat_cmd, '-ar', '44100', '-ac', '2',
        '-threads', '%d' % multiprocessing.cpu_count(),
        '-strict', 'experimental', '-acodec', 'aac', m4afile_temp ]
    proc = subprocess.Popen(split_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout_val, stderr_val = proc.communicate()
    #
    ## remove mp3 files
    for filename in outfiles: os.remove(filename)
    #
    ## now put in metadata
    mp4tags = mutagen.mp4.MP4(m4afile_temp)
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
