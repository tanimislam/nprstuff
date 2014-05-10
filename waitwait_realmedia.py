#!/usr/bin/env python

import os, sys, lxml.html, urllib2
import npr_utils, time, subprocess

def rm_get_main_url(datetime_s):
    if not npr_utils.is_saturday(datetime_s):
        raise ValueError("Error, this date given by '%s' is not a Saturday." %
                         npr_utils.get_datestring(datetime_s) )
    
    mon_lower = time.strftime('%b', datetime_s).lower()
    year = datetime_s.tm_year
    dsub = time.strftime('%y%m%d', datetime_s)
    full_rm_url = 'http://www.npr.org/programs/waitwait/archrndwn/%04d/%s/%s.waitwait.html' % (
        year, mon_lower, dsub )
    return full_rm_url

def rm_get_title_from_url( datetime_s ):
    full_rm_url = rm_get_main_url( datetime_s )
    tree = lxml.html.fromstring( urllib2.urlopen( full_rm_url ).read() )
    cand_elems = filter(lambda elem: len(list(elem.iter('a'))) != 0 and
                        elem.text is not None, tree.iter('b'))
    subtites = [ elem.text.split('\n')[0].strip() for elem in cand_elems ]
    title = time.strftime('%B %d, %Y', datetime_s)
    title = '%s: %s' % ( title,
                         '; '.join([ '%d) %s' % ( num + 1, subtite ) for
                                     (num, subtite) in enumerate(subtites) ]) )
    return title

def rm_download_file( datetime_s, outdir = os.getcwd() ):
    decdate = npr_utils.get_decdate( datetime_s )
    outfile = os.path.join( outdir, 'NPR.WaitWait.%s.rm' % decdate )
    try:
        dsub = time.strftime('%Y%m%d', datetime_s)
        rm_url = 'http://download.npr.org/real.npr.na-central/waitwait/%s_waitwait.rm' % dsub
        req = urllib2.urlopen( rm_url )
        with open( outfile, 'w' ) as openfile:
            openfile.write( req.read() )
        return outfile
    except Exception as e:
        if os.path.isfile( outfile ):
            os.remove( outfile )
        raise ValueError("Error, could not download Wait Wait RM file for '%s' into %s." % (
            npr_utils.get_datestring(datetime_s), outdir ) )        

def rm_create_wav_file( datetime_s, rm_file, outdir = os.getcwd() ):
    wgdate = time.strftime('%d-%b-%Y', datetime_s)
    wavfile = os.path.join( outdir, 'waitwait%s.wav' % wgdate )
    split_cmd = [ '/usr/bin/mplayer', '-vo', 'null', '-ao', 'pcm:file=%s' % 
                  wavfile, rm_file ]
    proc = subprocess.Popen( split_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    stdout_val, stderr_val = proc.communicate()
    return wavfile
    
