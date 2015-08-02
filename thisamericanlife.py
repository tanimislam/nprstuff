#!/usr/bin/env python
__author__ = 'Tanim Islam'

import os, sys, time
import urllib2, lxml.html
from mutagen.id3 import APIC, TDRC, TALB, COMM, TRCK, TPE2, TPE1, TIT2, TCON, ID3
from optparse import OptionParser

def get_americanlife_info(epno, throwException = True, extraStuff = None):
    """
    Returns a tuple of title, year given the episode number for This American Life.
    """

    # first see if this episode of this american life exists...
    try:
        if extraStuff is None:
            req = urllib2.urlopen('http://www.thisamericanlife.org/radio-archives/episode/%d' % epno)
        else:
            req = urllib2.urlopen('http://www.thisamericanlife.org/radio-archives/episode/%d/%s' % 
                                  ( epno, extraStuff) )
    except urllib2.HTTPError as e:
        if throwException:
            raise ValueError("Error, could not find This American Life episode %d, because could not open webpage." % epno)
        else:
            return None

    enc = req.headers['content-type'].split(';')[-1].split('=')[-1].strip().upper()
    if enc not in ( 'UTF-8', ):
        tree = lxml.html.fromstring(unicode(req.read(), encoding=enc))
    else:
        tree = lxml.html.fromstring(req.read())

    elem_info_list = filter(lambda elem: 'class' in elem.keys() and
                            elem.get('class') == "top-inner clearfix", tree.iter('div'))
    if len(elem_info_list) != 1:
        if throwException:
            raise ValueError("Error, cannot find date and title for This American Life episode #%d," % epno +
                             " because could not get proper elem from HTML source.")
        else:
            return None
    elem_info = max(elem_info_list)
    date_list = filter(lambda elem: 'class' in elem.keys() and elem.get('class') == 'date',
                        elem_info.iter('div'))
    if len(date_list) != 1:
        if throwException:
            raise ValueError("Error, cannot find date and title for This American Life episode #%d." % epno)
        else:
            return None
    date_s = max(date_list).text.strip()
    date_act = time.strptime(date_s, '%b %d, %Y')
    year = date_act.tm_year

    title_elem_list = filter(lambda elem: 'class' in elem.keys() and
                                          elem.get('class') == 'node-title', elem_info.iter('h1'))
    if len(title_elem_list) != 1:
        raise ValueError("Error, cannot find date and title for This American Life episode #%d." % epno)
    title = max(title_elem_list).text.strip()
    title = ':'.join(title.split(':')[1:]).strip()
    return title, year

def get_american_life(epno, directory = '/mnt/media/thisamericanlife', extraStuff = None):
    """
    Downloads an episode of This American Life into a given directory.
    The description of which URL the episodes are downloaded from is given in
    http://www.dirtygreek.org/t/download-this-american-life-episodes.

    The URL is http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/epno.mp3
    """

    try:
        title, year = get_americanlife_info(epno, extraStuff = extraStuff)
    except ValueError as e:
        print e
        print 'Cannot find date and title for This American Life episode #%d.' % epno
        return

    if not os.path.isdir(directory):
        raise ValueError("Error, %s is not a directory." % directory)
    outfile = os.path.join(directory, 'PRI.ThisAmericanLife.%03d.mp3' % epno)    
    urlopn = 'http://www.podtrac.com/pts/redirect.mp3/podcast.thisamericanlife.org/podcast/%d.mp3' % epno
    
    try:
        with open(outfile, 'wb') as openfile: openfile.write(urllib2.urlopen(urlopn).read())
    except urllib2.HTTPError:
        try:
            urlopn = 'http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/%d.mp3' % epno
            with open(outfile, 'wb') as openfile: openfile.write(urllib2.urlopen(urlopn).read())
        except urllib2.HTTPError:
            print "Error, could not download This American Life episode #%d. Exiting..." % epno
            return

    mp3tags = ID3( outfile )
    mp3tags['TDRC'] = TDRC(encoding = 0, text = [ u'%d' % year ])
    mp3tags['TALB'] = TALB(encoding = 0, text = [ u'This American Life' ])
    mp3tags['TRCK'] = TRCK(encoding = 0, text = [ u'%d' % epno ])
    mp3tags['TPE2'] = TPE2(encoding = 0, text = [u'Chicago Public Media'])
    mp3tags['TPE1'] = TPE1(encoding = 0, text = [u'Ira Glass'])
    mp3tags['TIT2'] = TIT2(encoding = 0, text = [u'%d: %s' % ( epno, title ) ])
    mp3tags['TCON'] = TCON(encoding = 0, text = [u'Podcast'])
    mp3tags.save()

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
    options, args = parser.parse_args()
    direct = os.path.expanduser( options.directory )
    get_american_life(options.episode, directory=direct, extraStuff = options.extraStuff)
