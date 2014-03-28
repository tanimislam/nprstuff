#!/usr/bin/env python

import os, sys, glob, re, multiprocessing
import subprocess, lxml, urllib2, datetime, time
import npr_utils
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
        
def get_waitwait(outputdir, datetime_saturday, order_totnum = None,
                 file_data = None):
    
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
        file_data = get_freshair_image()
        
    nprURL = npr_utils.get_NPR_URL(datetime_s, 
                                   _npr_waitwait_progid, 
                                   _npr_waitwait_key )
    year = datetime_s.tm_year
    
    # download this data into an lxml elementtree
    tree = lxml.etree.fromstring( urllib2.urlopen(nprURL).read())
    
    # now get tuple of title to mp3 file
    title_mp3_urls = []
    for elem in list(tree.iter('story'))[1:]:
        title = elem.iter('title')[0].text.strip()
        m3uurl = max( elem.iter('mp3') ).text.strip()
        mp3url = urllib2.urlopen( m3uurl ).read().strip()
        title_mp3_urls.append( ( title, mp3url ) )
        
    decdate = time.strftime('%d.%m.%Y', datetime_s)

    titles, mp3urls = zip(*title_mp3_urls)
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
    wavfile = os.path.join(outputdir, 'freshair%s.wav' % wgdate ).replace(' ', '\ ')
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

    # now convert to m4a file
    m4afile = os.path.join(outputdir, 'NPR.FreshAir.%s.m4a' % decdate )
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
                      action = 'store', default = '/mnt/media/freshair',
                      help = 'Name of the directory to store the file. Default is %s.' %
                      '/mnt/media/freshair')
    parser.add_option('--date', dest='date', type=str,
                      action = 'store', default = npr_utils.get_datestring(time.localtime()),
                      help = 'The date, in the form of "January 1, 2014." The default is last Saturday, %s.' %
                      npr_utils.get_datestring( _get_last_saturday( time.localtime() ) ) )
    opts, args = parser.parse_args()
    fname = get_waitwait( opts.dirname, npr_utils.get_time_from_datestring( opts.date ) )
