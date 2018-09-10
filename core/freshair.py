import os, glob, multiprocessing, datetime, time, re, titlecase
import mutagen.mp4, subprocess, multiprocessing.pool, requests
from optparse import OptionParser
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from . import npr_utils

_npr_FreshAir_progid = 13

def get_freshair_image():
    myURL = 'http://media.npr.org/images/podcasts/2013/primary/fresh_air.png'
    return requests.get( myURL ).content
    
def _download_file(input_tuple):
    mp3URL, filename = input_tuple
    resp = requests.get( mp3URL, stream = True )
    if resp.ok:
        with open(filename, 'wb') as openfile:
            for chunk in resp.iter_content(65536):
                openfile.write( chunk )
        return filename
    else:
        print('SOMETHING HAPPENED WITH %s' % filename)
        return None

def get_freshair_date_from_name(candidateNPRFreshAirFile):
    if not os.path.isfile(candidateNPRFreshAirFile):
        raise ValueError("Error, %s is not a file," % candidateNPRFreshAirFile )
    if not os.path.basename(candidateNPRFreshAirFile).endswith('.m4a'):
        raise ValueError("Error, %s does not end in .m4a" % candidateNPRFreshAirFile )
    if not os.path.basename(candidateNPRFreshAirFile).startswith('NPR.FreshAir.'):
        raise ValueError("Error, %s is not a valid file" % candidateNPRFreshAirFile )
    day, mon, year = [ int(tok) for tok in os.path.basename(candidateNPRFreshAirFile).split('.')[2:5] ]
    return datetime.date(year, mon, day)
    
def get_freshair_valid_dates_remaining_tuples(yearnum, inputdir):
    freshair_files_downloaded = glob.glob( os.path.join(inputdir, 'NPR.FreshAir.*.%04d.m4a' % yearnum ) )
    dates_downloaded = set( [ get_freshair_date_from_name(filename) for filename in 
                              freshair_files_downloaded ] )
    all_order_weekdays = { date_s : (num+1) for (num, date_s) in
                           enumerate( npr_utils.get_weekday_times_in_year(yearnum) ) }
    dtime_now = datetime.datetime.now()
    nowd = datetime.date(dtime_now.year, dtime_now.month, dtime_now.day)
    weekdays_left = set( filter(lambda date_s: date_s < nowd, set( all_order_weekdays . keys() ) ) ) - \
        set( dates_downloaded )
    totnum = len( all_order_weekdays.keys() )
    order_dates_remain = sorted([ ( all_order_weekdays[date_s], totnum, date_s ) for
                                  date_s in weekdays_left ], key = lambda tup: tup[0] ) 
    return order_dates_remain

def _process_freshairs_by_year_tuple(input_tuple):
    outputdir, totnum, verbose, datetimes_order_tuples = input_tuple
    fa_image = get_freshair_image()
    for date_s, order in datetimes_order_tuples:
        time0 = time.time()
        try:
            fname = get_freshair(outputdir, date_s, order_totnum = ( order, totnum),
                                 file_data = fa_image )
            if verbose:
                print('processed %s in %0.3f seconds.' % ( os.path.basename(fname), time.time() - time0 ))
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
        pool = npr_utils.MyPool(processes = multiprocessing.cpu_count())
        pool.map(_process_freshairs_by_year_tuple, input_tuples)
    else:
        print( 'Missing %d episodes for %04d.' % ( len(order_dates_remain), yearnum ) )
        for order, totnum, date_s in order_dates_remain:
            print( 'Missing NPR FreshAir episode for %s.' %
                   date_s.strftime('%B %d, %Y') )
    if verbose:
        print( 'processed all Fresh Air downloads for %04d in %0.3f seconds.' %
               ( yearnum, time.time() - time0 )  )

def process_freshair_titlemp3_tuples( html ):
    titles = []
    mp3s = []
    for story_elem in html.find_all('story'):
        all_http_lines = list(map(lambda line: line.strip(),
                                  filter(lambda line: len(line.strip()) > 0 and
                                         line.strip().startswith('https'), story_elem.text.split('\n') ) ) )
        story_line_url = all_http_lines[ 0 ]
        h2 = BeautifulSoup( requests.get( story_line_url ).content, 'lxml' )
        title_elems = h2.find_all('title')
        title = None
        if len( title_elems ) != 0:
            title = titlecase.titlecase(
                ': '.join(map(lambda tok: tok.strip( ),
                              title_elems[0].text.split(':')[:-1] ) ) )
        titles.append(title)
    for elem in html.find_all('mp3', {'type' : 'm3u' }):
        m3uurl = elem.text.strip()
        mp3url = requests.get( m3uurl ).text.strip()
        mp3s.append( mp3url )
    title_mp3_urls = sorted( filter(None, zip( titles, mp3s ) ),
                             key = lambda tup: tup[1] ) 
    return title_mp3_urls

def get_freshair(outputdir, date_s, order_totnum = None,
                 file_data = None, debug = False,
                 exec_dict = None, check_if_exist = False,
                 mp3_exist = False, to_file_debug = True ):
    
    # check if outputdir is a directory
    if not os.path.isdir(outputdir):
        raise ValueError("Error, %s is not a directory." % outputdir)

    # check if actually a weekday
    assert( npr_utils.is_weekday(date_s) )
    
    if exec_dict is None:
        exec_dict = npr_utils.find_necessary_executables()
    assert( exec_dict is not None )
    avconv_exec = exec_dict['avconv']
    
    if order_totnum is None:
        order_totnum = npr_utils.get_order_number_weekday_in_year(date_s)
    order_in_year, tot_in_year = order_totnum

    if file_data is None:
        file_data = get_freshair_image()

    decdate = date_s.strftime('%d.%m.%Y')
    m4afile = os.path.join(outputdir, 'NPR.FreshAir.%s.m4a' % decdate )
    if check_if_exist and os.path.isfile(m4afile):
        return
    
    nprURL = npr_utils.get_NPR_URL(date_s, _npr_FreshAir_progid, 
                                   npr_utils.get_api_key() )
    year = date_s.year
    
    # download this data into a BeautifulSoup object
    resp = requests.get( nprURL )
    html = BeautifulSoup( resp.content, 'lxml' )
    
    if debug:
        # print 'URL = %s' % nprURL
        if to_file_debug:
            with open(os.path.join(outputdir, 'NPR.FreshAir.tree.%s.xml' % decdate), 'w') as openfile:
                openfile.write( '%s\n' % html.prettify( ) )
        return html
    
    # check for unavailable tag
    if len( html.find_all('unavailable', { 'value' : 'true' } ) ) != 0:
        unavailable_elem = html.find_all('unavailable', { 'value' : 'true' } )[ 0 ]
        if unavailable_elem.text is None:
            print( 'Could not create Fresh Air episode for date %s for some reason' %
                   npr_utils.get_datestring( date_s ) )
        else:
            print( 'Could not create Fresh Air episode for date %s for this reason: %s' % 
                   ( npr_utils.get_datestring( date_s ), unavailable_elem.text.strip() ) )
        return

    # now get tuple of title to mp3 file
    title_mp3_urls = process_freshair_titlemp3_tuples( html )
    if len(title_mp3_urls) == 0:
        print( 'Error, could not find any Fresh Air episodes for date %s.' %
               npr_utils.get_datestring( date_s ) )
        return
    
    titles, songurls = zip(*title_mp3_urls)
    outfiles = [ os.path.join(outputdir, 'freshair.%s.%d.mp3' % 
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
    pool = multiprocessing.Pool(processes = len(songurls) )
    if not mp3_exist:
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
    split_cmd = [ avconv_exec, '-y', '-i', avconv_concat_cmd, '-ar', '44100', '-ac', '2',
                  '-threads', '%d' % multiprocessing.cpu_count(),
                  '-strict', 'experimental', '-acodec', 'aac', m4afile ]
    proc = subprocess.Popen(split_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout_val, stderr_val = proc.communicate()
    
    # remove mp3 files
    for filename in outfiles:
        os.remove(filename)
    
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
    return m4afile
    
