__author__ = 'Tanim Islam'

#!/usr/bin/env python

import os, sys, tagpy, time
import urllib2, lxml.html
from optparse import OptionParser

def get_americanlife_info(epno):
    """
    Returns a tuple of title, year given the episode number for This American Life.
    """

    # first see if this episode of this american life exists...
    try:
        req = urllib2.urlopen('http://www.thisamericanlife.org/radio-archives/episode/%d' % epno)
    except urllib2.HTTPError as e:
        raise ValueError("Error, could not find This American Life episode %d." % epno)

    enc = req.headers['content-type'].split(';')[-1].split('=')[-1].strip().upper()
    if enc != 'UTF-8':
        tree = lxml.html.fromstring(unicode(req.read(), encoding=enc))
    else:
        tree = lxml.html.fromstring(req.read())

    elem_info_list = filter(lambda elem: 'class' in elem.keys() and
                                         elem.get('class') == "top-inner clearfix", tree.iter('div'))
    if len(elem_info_list) != 1:
        raise ValueError("Error, cannot find date and title for This American Life episode #%d." % epno)
    elem_info = max(elem_info_list)
    date_list = filter(lambda elem: 'class' in elem.keys() and elem.get('class') == 'date',
                        elem_info.iter('div'))
    if len(date_list) != 1:
        raise ValueError("Error, cannot find date and title for This American Life episode #%d." % epno)
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

def get_american_life(epno, directory = '/mnt/media/thisamericanlife'):
    """
    Downloads an episode of This American Life into a given directory.
    The description of which URL the episodes are downloaded from is given in
    http://www.dirtygreek.org/t/download-this-american-life-episodes.

    The URL is http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/epno.mp3
    """

    try:
        title, year = get_americanlife_info(epno)
    except ValueError:
        print 'Cannot find date and title for This American Life episode #%d.' % epno
        return

    if not os.path.isdir(directory):
        raise ValueError("Error, %s is not a directory." % directory)
    outfile = os.path.join(directory, 'PRI.ThisAmericanLife.%03d.mp3' % epno)
    urlopn = 'http://audio.thisamericanlife.org/jomamashouse/ismymamashouse/%d.mp3' % epno
    with open(outfile, 'wb') as openfile: openfile.write(urllib2.urlopen(urlopn).read())

    f = tagpy.FileRef(outfile)
    t = f.tag()
    t.title = '#%d: %s' % ( epno, title)
    t.year = year
    t.artist = 'Ira Glass'
    t.album = 'This American Life'
    t.track = epno
    f.save()
