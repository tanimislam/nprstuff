#!/usr/bin/env python3

import os, sys, datetime, titlecase
import lxml.html, requests, codecs
from mutagen.id3 import APIC, TDRC, TALB, COMM, TRCK, TPE2, TPE1, TIT2, TCON, ID3
from bs4 import BeautifulSoup
from optparse import OptionParser


def get_americanlife_info(epno, throwException = True, extraStuff = None, verify = True ):
    """
    Returns a tuple of title, year given the episode number for This American Life.
    """

    # first see if this episode of this american life exists...
    if extraStuff is None:
        resp = requests.get( 'http://www.thisamericanlife.org/radio-archives/episode/%d' % epno, verify = verify )
    else:
        resp = requests.get( 'http://www.thisamericanlife.org/radio-archives/episode/%d/%s' % ( epno, extraStuff ),
                             verify = verify )
    if resp.status_code != 200:
        raise ValueError("Error, could not find This American Life episode %d, because could not open webpage." % epno)
    
    enc = resp.headers['content-type'].split(';')[-1].split('=')[-1].strip().upper()
    if enc not in ( 'UTF-8', ):
        html = BeautifulSoup( unicode( resp.text, encoding=enc ), 'lxml' )
    else:
        html = BeautifulSoup( resp.text, 'lxml' )

    elem_info_list = list(filter(lambda elem: 'class' in elem.attrs and
                                 'top-inner' in elem.attrs['class'] and
                                 'clearfix' in elem.attrs['class'], html.find_all('div')))
    if len(elem_info_list) != 1:
        if throwException:
            raise ValueError(" ".join([ "Error, cannot find date and title for This American Life episode #%d," % epno,
                                        "because could not get proper elem from HTML source." ]) )
        else:
            return None
    elem_info = max(elem_info_list)
    date_list = list(filter(lambda elem: 'class' in elem.attrs and 'date' in elem.attrs['class'],
                            elem_info.find_all('div')))
    if len(date_list) != 1:
        if throwException:
            raise ValueError("Error, cannot find date and title for This American Life episode #%d." % epno)
        else:
            return None
    date_s = max(date_list).text.strip()
    date_act = datetime.datetime.strptime( date_s, '%b %d, %Y' ).date( )
    year = date_act.year

    title_elem_list = list(filter(lambda elem: 'class' in elem.attrs and
                                  'node-title' in elem.attrs['class'], elem_info.find_all('h1')))
    if len(title_elem_list) != 1:
        raise ValueError("Error, cannot find date and title for This American Life episode #%d." % epno)
    title = max(title_elem_list).text.strip()
    title = titlecase.titlecase( ':'.join( title.split(':')[1:]).strip() )
    return title, year

def get_american_life(epno, directory = '/mnt/media/thisamericanlife', extraStuff = None, verify = True ):
    """
    Downloads an episode of This American Life into a given directory.
    The description of which URL the episodes are downloaded from is given in
    http://www.dirtygreek.org/t/download-this-american-life-episodes.

    The URL is http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/epno.mp3
    
    Otherwise, the URL is http://www.podtrac.com/pts/redirect.mp3/podcast.thisamericanlife.org/podcast/epno.mp3
    """
    try:
        title, year = get_americanlife_info(epno, extraStuff = extraStuff, verify = verify)
    except ValueError as e:
        print(e)
        print('Cannot find date and title for This American Life episode #%d.' % epno)
        return

    if not os.path.isdir(directory):
        raise ValueError("Error, %s is not a directory." % directory)
    outfile = os.path.join(directory, 'PRI.ThisAmericanLife.%03d.mp3' % epno)    
    urlopn = 'http://www.podtrac.com/pts/redirect.mp3/podcast.thisamericanlife.org/podcast/%d.mp3' % epno

    resp = requests.get( urlopn, stream = True, verify = verify )
    if not resp.ok:
        urlopn = 'http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/%d.mp3' % epno
        resp = requests.get( urlopn, stream = True, verify = verify )
        if not resp.ok:
            print("Error, could not download This American Life episode #%d. Exiting..." % epno)
            return
    with open( outfile, 'wb') as openfile:
        for chunk in resp.iter_content(65536):
            openfile.write( chunk )
            
    mp3tags = ID3( )
    mp3tags['TDRC'] = TDRC(encoding = 0, text = [ u'%d' % year ])
    mp3tags['TALB'] = TALB(encoding = 0, text = [ u'This American Life' ])
    mp3tags['TRCK'] = TRCK(encoding = 0, text = [ u'%d' % epno ])
    mp3tags['TPE2'] = TPE2(encoding = 0, text = [u'Chicago Public Media'])
    mp3tags['TPE1'] = TPE1(encoding = 0, text = [u'Ira Glass'])
    try:
        mp3tags['TIT2'] = TIT2(encoding = 0, text = [ '#%03d: %s' % ( epno, title ) ] )
    except:
        mp3tags['TIT2'] = TIT2(encoding = 0, text = [ codecs.encode('#%03d: %s' % ( epno, title ), 'utf8') ])
    mp3tags['TCON'] = TCON(encoding = 0, text = [u'Podcast'])
    mp3tags.save( outfile )

if __name__=='__main__':
    parser = OptionParser()
    parser.add_option('--episode', dest='episode', type=int, action='store', default = 150,
                      help = 'Episode number of This American Life to download. Default is 150.')
    parser.add_option('--directory', dest='directory', type=str, action='store',
                      default = '/mnt/media/thisamericanlife',
                      help = 'Directory into which to download This American Life episodes. Default is %s.' %
                      '/mnt/media/thisamericanlife')
    parser.add_option('--extra', dest='extraStuff', type=str, action='store',
                      help = 'If defined, some extra stuff in the URL to get a This American Life episode.')
    parser.add_option('--noverify', dest = 'do_noverify', action = 'store_true', default = False,
                      help = 'If chosen, then do not verify the SSL connection.')
    options, args = parser.parse_args()
    direct = os.path.expanduser( options.directory )
    get_american_life(options.episode, directory=direct, extraStuff = options.extraStuff,
                      verify = not options.do_noverify )
