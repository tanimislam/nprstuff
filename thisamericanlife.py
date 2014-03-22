__author__ = 'Tanim Islam'

#!/usr/bin/env python

import os, sys, tagpy, time
import urllib2, lxml.html
from optparse import OptionParser

def get_americanlife_info(epno):

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





