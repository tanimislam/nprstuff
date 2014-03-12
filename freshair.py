#!/usr/bin/env python

import os, sys, glob, numpy, urllib2, mutagen.mp4
import multiprocessing, time, lxml.etree, subprocess
import multiprocessing.pool
sys.path.append('/mnt/software/sources/nprstuff/simple-junk')
import npr_utils
from optparse import OptionParser

# magic to get multiprocessing to get processes to be able to start daemons
class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon) 

class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess 

def get_freshair_image():
    return urllib2.urlopen('http://media.npr.org/images/podcasts/2013/primary/fresh_air.png').read()

# get NPR API tag for this program
# nprApiDate=$(date --date="$1" +%Y-%m-%d) ;
# nprURL="http://api.npr.org/query?id=13&date="$nprApiDate"&dateType=story&output=NPRML&apiKey=MDA2OTgzNTcwMDEyOTc1NDg4NTNmMWI5Mg001" ;
def get_freshair_URL(datetime_s):
    nprApiDate = time.strftime('%Y-%m-%d', datetime_s)
    return 'http://api.npr.org/query?id=13&date=%s&dateType=story&output=NPRML&apiKey=MDA2OTgzNTcwMDEyOTc1NDg4NTNmMWI5Mg001' % nprApiDate

def _download_file(input_tuple):
    mp3URL, filename = input_tuple
    with open(filename, 'wb') as openfile:
        openfile.write( urllib2.urlopen(mp3URL).read() )

def get_freshair_date_from_name(candidateNPRFreshAirFile):
    if not os.path.isfile(candidateNPRFreshAirFile):
        raise ValueError("Error, %s is not a file," % candidateNPRFreshAirFile )
    if not os.path.basename(candidateNPRFreshAirFile).endswith('.m4a'):
        raise ValueError("Error, %s does not end in .m4a" % candidateNPRFreshAirFile )
    if not os.path.basename(candidateNPRFreshAirFile).startswith('NPR.FreshAir.'):
        raise ValueError("Error, %s is not a valid file" % candidateNPRFreshAirFile )
    day, mon, year = [ int(tok) for tok in os.path.basename(candidateNPRFreshAirFile).split('.')[2:5] ]
    return time.strptime('%d-%d-%04d' % ( day, mon, year ),
                         '%d-%m-%Y' )
def get_freshair_valid_dates_remaining_tuples(yearnum, inputdir):
    freshair_files_downloaded = glob.glob( os.path.join(inputdir, 'NPR.FreshAir.*.%04d.m4a' % yearnum ) )
    dates_downloaded = set( [ get_freshair_date_from_name(filename) for filename in 
                              freshair_files_downloaded ] )
    all_order_weekdays = { datetime : (num+1) for (num, datetime) in
                           enumerate( npr_utils.get_weekday_times_in_year(yearnum) ) }
    weekdays_left = filter(lambda datetime: datetime < time.localtime(), set( all_order_weekdays . keys() ) - set( dates_downloaded ) )
    totnum = len(all_order_weekdays.keys() )
    order_dates_remain = sorted([ ( all_order_weekdays[datetime], totnum, datetime ) for
                                  datetime in weekdays_left ], key = lambda tup: tup[0] ) 
    return order_dates_remain

def _process_freshairs_by_year_tuple(input_tuple):
    outputdir, totnum, verbose, datetimes_order_tuples = input_tuple
    fa_image = get_freshair_image()
    for datetime, order in datetimes_order_tuples:
        time0 = time.time()
        fname = get_freshair(outputdir, datetime, order_totnum = ( order, totnum),
                             file_data = fa_image )
        if verbose:
            print 'processed %s in %0.3f seconds.' % ( os.path.basename(fname), time.time() - time0 )

def process_all_freshairs_by_year(yearnum, inputdir, verbose = True):
    order_dates_remain = get_freshair_valid_dates_remaining_tuples( yearnum, inputdir )
    if len(order_dates_remain) == 0: return
    totnum = order_dates_remain[0][1]
    nprocs = multiprocessing.cpu_count() 
    input_tuples = [ ( inputdir, totnum, verbose, [ ( datetime, order ) for ( order, totnum, datetime) in 
                                                    order_dates_remain if (order - 1) % nprocs == procno ] ) for
                     procno in xrange(nprocs) ]
    time0 = time.time()
    pool = MyPool(processes = multiprocessing.cpu_count())
    pool.map(_process_freshairs_by_year_tuple, input_tuples)
    if verbose:
        print 'processed all Fresh Air downloads for %04d in %0.3f seconds.' % ( yearnum, time.time() - time0 ) 

def get_freshair(outputdir, datetime_wkday, order_totnum = None,
                 file_data = None):
    
    # check if outputdir is a directory
    if not os.path.isdir(outputdir):
        raise ValueError("Error, %s is not a directory." % outputdir)

    # check if actually a weekday
    datetime_s = npr_utils.get_sanitized_time(datetime_wkday)
    if not npr_utils.is_weekday(datetime_s):
        raise ValueError("Error, date = %s not a weekday." %
                         npr_utils.get_datestring(datetime_s) )

    if order_totnum is None:
        order_totnum = npr_utils.get_order_number_weekday_in_year(datetime_s)
    order_in_year, tot_in_year = order_totnum

    if file_data is None:
        file_data = get_freshair_image()
    
    nprURL = get_freshair_URL(datetime_s)
    year = datetime_s.tm_year
    
    # download this data into an lxml elementtree
    tree = lxml.etree.fromstring( urllib2.urlopen(nprURL).read())
    
    # now get tuple of title to mp3 file
    title_mp3_urls = []
    for elem in tree.iter('story'):
        title = list( elem.iter('title') )[0].text.strip()
        m3uurl = max( elem.iter('mp3') ).text.strip()
        mp3url = urllib2.urlopen( m3uurl ).read().strip()
        title_mp3_urls.append( ( title, mp3url ) )
    
    decdate = time.strftime('%d.%m.%Y', datetime_s)
    
    titles, mp3urls = zip(*title_mp3_urls)
    title = time.strftime('%A, %B %d, %Y', datetime_s)
    title = '%s: %s.' % ( title,
                          '; '.join([ '%d) %s' % ( num + 1, titl ) for
                                      (num, titl) in enumerate(titles) ]) )    
    outfiles = [ os.path.join(outputdir, 'freshair.%s.%d.mp3' % 
                              ( decdate, num + 1) ) for
                 (num, mp3url) in enumerate( mp3urls) ]
    
    # download those files
    time0 = time.time()
    pool = multiprocessing.Pool(processes = len(mp3urls) )
    pool.map(_download_file, zip( mp3urls, outfiles ) )
    
    # sox magic command
    time0 = time.time()
    wgdate = time.strftime('%d-%b-%Y', datetime_s)
    wavfile = os.path.join(outputdir, 'freshair%s.wav' % wgdate ).replace(' ', '\ ')
    fnames = [ filename.replace(' ', '\ ') for filename in outfiles ]
    split_cmd = [ '(for', 'file', 'in', ] + fnames + [ 
        ';', '/usr/bin/sox', '$file', '-t', 'cdr', '-', ';', 'done)' ] + [ 
            '|', '/usr/bin/sox', 't-', 'cdr', '-', wavfile ]
    split_cmd = [ '/usr/bin/sox', ] + fnames + [ wavfile, ]
    proc = subprocess.Popen(split_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout_val, stderr_val = proc.communicate()
    for filename in outfiles:
        os.remove(filename)

    # now convert to m4a file
    # /usr/bin/avconv -y -i freshair$wgdate.wav -ar 44100 -ac 2 -aq 400 -acodec libfaac NPR.FreshAir."$decdate".m4a ;
    m4afile = os.path.join(outputdir, 'NPR.FreshAir.%s.m4a' % decdate )
    split_cmd = [ '/usr/bin/avconv', '-y', '-i', wavfile, '-ar', '44100', '-ac', '2', '-threads', '%d' % multiprocessing.cpu_count(),
                  '-strict', 'experimental', '-acodec', 'aac', m4afile ]
    proc = subprocess.Popen(split_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    stdout_val, stderr_val = proc.communicate()
    
    # remove wav file
    os.remove( wavfile )
    
    # now put in metadata
    mp4tags = mutagen.mp4.MP4(m4afile)
    mp4tags.tags['\xa9nam'] = [ title, ]
    mp4tags.tags['\xa9alb'] = [ 'Fresh Air From WHYY: %d' % year, ]
    mp4tags.tags['\xa9ART'] = [ 'Terry Gross', ]
    mp4tags.tags['\xa9day'] = [ '%d' % year, ]
    mp4tags.tags['\xa9cmt'] = [ "more info at : Fresh Air from WHYY and NPR Web site", ]
    mp4tags.tags['trkn'] = [ ( order_in_year, tot_in_year ), ]
    mp4tags.tags['covr'] = [ mutagen.mp4.MP4Cover(file_data, mutagen.mp4.MP4Cover.FORMAT_PNG ), ]
    mp4tags.save()
    return m4afile

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--dirname', dest='dirname', type=str,
                      action = 'store', default = os.getcwd(),
                      help = 'Name of the directory to store the file. Default is %s.' %
                      os.getcwd() )
    parser.add_option('--date', dest='date', type=str,
                      action = 'store', default = npr_utils.get_datestring(time.localtime()),
                      help = 'The date, in the form of "January 1, 2014." The default is today\'s date, %s.' %
                      npr_utils.get_datestring( time.localtime() ) )
    opts, args = parser.parse_args()
    fname = get_freshair( opts.dirname, npr_utils.get_time_from_datestring( opts.date ) )
                  
