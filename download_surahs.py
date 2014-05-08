#!/usr/bin/env python

import lxml.html, urllib2, urlparse, time
from multiprocessing import Pool, cpu_count

def get_suras(tree):
    suras = []
    top_url = 'http://quranicradio.com'
    for elem in tree.iter('tr'):
        sura_elems = list(elem.iter('td'))
        if len(sura_elems) != 4:
            continue
        if 'class' in elem.keys():
            continue
        num_sura = int( sura_elems[0].text.strip() )
        name_sura = max( sura_elems[1].iter('a') ).text.strip()
        mp3_url = 'http://download.quranicaudio.com/quran/abdurrashid_sufi/%03d.mp3' % num_sura
        suras.append( ( num_sura, name_sura, mp3_url ) )
    return suras

def _download_per_tuple(input_tuple):
    time0 = time.time()
    num, name, mp3_url = input_tuple
    filename = '%03d.%s.mp3' % ( num, name )
    with open(filename, 'wb') as openfile:
        openfile.write( urllib2.urlopen( mp3_url ).read() )
    print 'Downloaded Sura %03d - %s, in %0.3f seconds.' % ( num, name, time.time() - time0 )

def download_all_suras(suras):
    time0 = time.time()
    pool = Pool(processes = cpu_count())
    pool.map(_download_per_tuple, suras)
    print 'Downloaded all suras in %0.3f seconds.' % ( time.time() - time0)

