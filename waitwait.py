#!/usr/bin/env python

import os, sys, glob, re, multiprocessing
import subprocess, lxml.etree, urllib2, datetime, time
import npr_utils, mutagen.mp4, waitwait_realmedia
from optparse import OptionParser

_npr_waitwait_key = 'MDA2OTgzNTcwMDEyOTc1NDg4NTNmMWI5Mg001'
_npr_waitwait_progid = 35

def _get_last_saturday(dt):
    datetime_s = npr_utils.get_sanitized_time(dt)

    # first find today's date
    tm_wday = datetime_s.tm_wday
    if tm_wday < 5:
        tm_wday = tm_wday + 7
    days_go_back = tm_wday - 5
    dt_s = datetime.datetime( datetime_s.tm_year, datetime_s.tm_mon,
                              datetime_s.tm_mday )
    dt_sat = dt_s - datetime.timedelta(days_go_back, 0, 0)
    return dt_sat.timetuple()

def get_waitwait_image():
    return urllib2.urlopen('http://upload.wikimedia.org/wikipedia/en/f/f4/WaitWait.png').read()
    
def _download_file( input_tuple ):
    mp3URL, filename = input_tuple
    with open(filename, 'wb') as openfile:
        openfile.write( urllib2.urlopen(mp3URL).read() )

def get_waitwait_date_from_name(candidateNPRWaitWaitFile):
    if not os.path.isfile(candidateNPRWaitWaitFile):
        raise ValueError("Error, %s is not a file," % candidateNPRWaitWaitFile )
    if not os.path.basename(candidateNPRWaitWaitFile).endswith('.m4a'):
        raise ValueError("Error, %s does not end in .m4a" % candidateNPRWaitWaitFile )
    if not os.path.basename(candidateNPRWaitWaitFile).startswith('NPR.WaitWait.'):
        raise ValueError("Error, %s is not a valid file" % candidateNPRWaitWaitFile )
    day, mon, year = [ int(tok) for tok in os.path.basename(candidateNPRWaitWaitFile).split('.')[2:5] ]
    return time.strptime('%d-%d-%04d' % ( day, mon, year ), '%d-%m-%Y' )

def get_waitwait_valid_dates_remaining_tuples(yearnum, inputdir):
    waitwait_files_downloaded = glob.glob( os.path.join(inputdir, 'NPR.WaitWait.*.%04d.m4a' % yearnum ) )
    dates_downloaded = set([ get_waitwait_date_from_name(filename) for filename in
                             waitwait_files_downloaded ])
    all_order_saturdays = { datetime : (num+1) for (num, datetime) in
                            enumerate( npr_utils.get_saturday_times_in_year( yearnum ) ) }
    saturdays_left = filter(lambda datetime: datetime < time.localtime(), set( all_order_saturdays.keys() ) - 
                            set( dates_downloaded ) )
    totnum = len( all_order_saturdays.keys() )
    order_dates_remain = sorted([ ( all_order_saturdays[datetime], totnum, datetime ) for
                                  datetime in saturdays_left ], key = lambda tup: tup[0] )
    return order_dates_remain

def _process_waitwaits_by_year_tuple(input_tuple):
    outputdir, totnum, verbose, datetimes_order_tuples = input_tuple
    ww_image = get_waitwait_image()
    for datetime, order in datetimes_order_tuples:
        time0 = time.time()
        try:
            fname = get_waitwait(outputdir, datetime, order_totnum = ( order, totnum),
                                 file_data = ww_image)
            if verbose:
                print 'Processed %s in %0.3f seconds.' % ( fname, time.time() - time0 )
        except Exception as e:
            print 'Could not create Wait Wait episode for date %s for some reason.' % (
                npr_utils.get_datestring( datetime ) )

def get_all_waitwaits_year( yearnum,
                            inputdir, verbose = True):
    order_dates_remain = get_waitwait_valid_dates_remaining_tuples( yearnum, inputdir )
    if len( order_dates_remain ) == 0: return
    totnum = order_dates_remain[0][1]
    nprocs = multiprocessing.cpu_count()
    input_tuples = [ ( inputdir, totnum, verbose, [ ( datetime, order) for ( order, totnum, datetime ) in
                                                    order_dates_remain if ( order - 1 ) % nprocs == procno ] ) for
                     procno in xrange( nprocs ) ]
    time0 = time.time()
    pool = npr_utils.MyPool(processes = nprocs )
    pool.map(_process_waitwaits_by_year_tuple, input_tuples)
    if verbose:
        print 'processed all Wait Wait downloads for %04d in %0.3f seconds.' % ( yearnum, time.time() - time0 )

def get_title_wavfile_standard(datetime_s, outputdir, debugonly = False):
    
    # download this data into an lxml elementtree
    nprURL = npr_utils.get_NPR_URL(datetime_s, 
                                   _npr_waitwait_progid, 
                                   _npr_waitwait_key )
    decdate = npr_utils.get_decdate( datetime_s )
    tree = lxml.etree.fromstring( urllib2.urlopen(nprURL).read())
    if debugonly:
        openfile = os.path.join( outputdir, 'NPR.WaitWait.tree.%s.xml' %
                                 decdate )
        with open( openfile, 'w') as outfile:
            outfile.write( lxml.etree.tostring( tree ) )
        return None
        
    # now get tuple of title to mp3 file
    title_mp3_urls = []
    for elem in filter(lambda elem: len(list(elem.iter('mp3'))) != 0, tree.iter('story')):
        title = list(elem.iter('title'))[0].text.strip()
        m3uurl = max( filter(lambda elm: 'type' in elm.keys() and
                             elm.get('type') == 'm3u', elem.iter('mp3') ) ).text.strip()
        try:
            mp3url = urllib2.urlopen( m3uurl ).read().strip()
            mp3h = urllib2.urlopen( mp3url )
            order = int( mp3url.split('_')[-1].replace('.mp3', '') )
            title_mp3_urls.append( ( title, mp3url, order ) )
        except Exception:
            pass
            
    titles, mp3urls, orders = zip(*sorted(title_mp3_urls, key = lambda tup: tup[2]))
    title = time.strftime('%B %d, %Y', datetime_s)
    title = '%s: %s.' % ( title,
                          '; '.join([ '%d) %s' % ( num + 1, titl ) for
                                      (num, titl) in enumerate(titles) ]) )
    outfiles = [ os.path.join(outputdir, 'waitwait.%s.%d.mp3' % 
                              ( decdate, num + 1) ) for
                 (num, mp3url) in enumerate( mp3urls) ]
    
    # download those files
    time0 = time.time()
    pool = multiprocessing.Pool(processes = len(mp3urls) )
    pool.map(_download_file, zip( mp3urls, outfiles ) )
    
    # sox magic command
    time0 = time.time()
    wgdate = time.strftime('%d-%b-%Y', datetime_s)
    wavfile = os.path.join(outputdir, 'waitwait%s.wav' % wgdate ).replace(' ', '\ ')
    fnames = [ filename.replace(' ', '\ ') for filename in outfiles ]
    split_cmd = [ '(for', 'file', 'in', ] + fnames + [ 
        ';', '/usr/bin/sox', '$file', '-t', 'cdr', '-', ';', 'done)' ] + [ 
            '|', '/usr/bin/sox', 't-', 'cdr', '-', wavfile ]
    split_cmd = [ '/usr/bin/sox', ] + fnames + [ wavfile, ]
    proc = subprocess.Popen(split_cmd, stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE)
    stdout_val, stderr_val = proc.communicate()
    for filename in outfiles:
        os.remove(filename)
    return title, wavfile
        
def get_waitwait(outputdir, datetime_saturday, order_totnum = None,
                 file_data = None, debugonly = False):
    
    # check if outputdir is a directory
    if not os.path.isdir(outputdir):
        raise ValueError("Error, %s is not a directory." % outputdir)

    # check if actually saturday
    datetime_s = npr_utils.get_sanitized_time(datetime_saturday)
    if not npr_utils.is_saturday(datetime_s):
        raise ValueError("Error, date = %s not a Saturday." %
                         npr_utils.get_datestring(datetime_s) )

    if order_totnum is None:
        order_totnum = npr_utils.get_order_number_saturday_in_year(datetime_s)
    order_in_year, tot_in_year = order_totnum
        
    if file_data is None:
        file_data = get_waitwait_image()
        
    year = datetime_s.tm_year
    decdate = npr_utils.get_decdate( datetime_s )

    if year >= 2006:
        tup = get_title_wavfile_standard(datetime_s, outputdir, 
                                         debugonly = debugonly )
        if tup is None:
            return
        title, wavfile = tup
    else:
        title = waitwait_realmedia.rm_get_title_from_url( datetime_s )
        rmfile = waitwait_realmedia.rm_download_file( datetime_s, 
                                                      outdir = outputdir )
        wavfile = waitwait_realmedia.rm_create_wav_file( datetime_s, rmfile,
                                                         outdir = outputdir )
        os.remove( rmfile )

    # now convert to m4a file
    m4afile = os.path.join(outputdir, 'NPR.WaitWait.%s.m4a' % decdate )
    split_cmd = [ '/usr/bin/avconv', '-y', '-i', wavfile, '-ar', '44100',
                  '-ac', '2', '-threads', '%d' % multiprocessing.cpu_count(),
                  '-strict', 'experimental', '-acodec', 'aac', m4afile ]
    proc = subprocess.Popen(split_cmd, stdout = subprocess.PIPE,
                            stderr = subprocess.PIPE)
    stdout_val, stderr_val = proc.communicate()
    
    # remove wav file
    os.remove( wavfile )

    # now put in metadata
    mp4tags = mutagen.mp4.MP4(m4afile)
    mp4tags.tags['\xa9nam'] = [ title, ]
    mp4tags.tags['\xa9alb'] = [ "Wait Wait...Don't Tell Me: %d" % year, ]
    mp4tags.tags['\xa9ART'] = [ 'Peter Sagal', ]
    mp4tags.tags['\xa9day'] = [ '%d' % year, ]
    mp4tags.tags['\xa9cmt'] = [ "more info at : NPR Web site", ]
    mp4tags.tags['trkn'] = [ ( order_in_year, tot_in_year ), ]
    mp4tags.tags['covr'] = [ mutagen.mp4.MP4Cover(file_data, mutagen.mp4.MP4Cover.FORMAT_PNG ), ]
    mp4tags.save()
    return m4afile

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--dirname', dest='dirname', type=str,
                      action = 'store', default = '/mnt/media/waitwait',
                      help = 'Name of the directory to store the file. Default is %s.' %
                      '/mnt/media/waitwait')
    parser.add_option('--date', dest='date', type=str,
                      action = 'store', default = npr_utils.get_datestring(_get_last_saturday(time.localtime())),
                      help = 'The date, in the form of "January 1, 2014." The default is last Saturday, %s.' %
                      npr_utils.get_datestring( _get_last_saturday( time.localtime() ) ) )
    parser.add_option('--debugonly', dest='debugonly', action='store_true', default = False,
                      help = 'If chosen, download the NPR XML data sheet for this Wait Wait episode.')
    opts, args = parser.parse_args()
    fname = get_waitwait( opts.dirname, npr_utils.get_time_from_datestring( opts.date ), debugonly = opts.debugonly )

