from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from nprstuff.gui import gui_common
import json, sys, datetime, re

class LightSpeedFrame(gui_common.MainFrame):
    def __init__(self, showFrame = True, iconPath = None):
        super(LightSpeedFrame, self).__init__(
            'Light Speed Magazine', LightSpeedURLInfoBox(),
            showFrame = showFrame, iconPath = iconPath)

class LightSpeedURLInfoBox(gui_common.URLInfoBox):
    def getMetaDataDict(self, tree):
        meta_dict = {}
        author = self._author(tree)
        if author is not None:
            meta_dict['author'] = author
        title = self._title(tree)
        if title is not None:
            meta_dict['title'] = title
        date_string = self._datestring(tree)
        if date_string is not None:
            meta_dict['date_string'] = date_string
        pic_url = self._picurl(tree)
        if pic_url is not None:
            meta_dict['pic_url'] = 'http://www.clipartbest.com/cliparts/Kcn/GKz/KcnGKzKcq.png' # fixme, help with WP redirects
        return meta_dict

    def getData(self, tree):
        entry_elem = max( filter(lambda elem: 'class' in elem.keys() and 
                                 elem.get('class') == "entry clear single_entry entry-content", tree.iter('div')))
        paras = filter(lambda elem: len(elem.text_content().strip()) > 0, entry_elem.iter('p'))
        textData = [ unicode(para.text_content().strip()) for para in paras ]
        return textData

    def getDate( self, dateString ):
        return datetime.datetime.strptime( dateString,
                                           '%Y-%m-%dT%H:%M:%S' )

    def _author(self, tree):
        elems_for_author = filter(lambda elem: 'class' in elem.keys() and
                                  elem.get('class') == 'postmetadata' and
                                  'by' in elem.text_content(), tree.iter('p'))
        if len(elems_for_author) != 1:
            return None
        elem_for_author = max(elems_for_author)
        authorName = ' '.join( elem_for_author.text_content().strip().split()[1:] )
        if len(authorName)  == 0:
            return None
        return authorName

    def _title(self, tree):
        title_elems = filter(lambda elem: 'property' in elem.keys() and
                             'content' in elem.keys() and 
                             elem.get('property') == 'og:title', tree.iter('meta'))
        if len(title_elems) != 1:
            return None
        title_elem = max(title_elems)
        title = title_elem.get('content').strip()
        title = re.sub('- Lightspeed Magazine.*', '', title).strip()
        if len(title) == 0:
            return None
        return title

    def _datestring(self, tree):
        date_elems =  filter(lambda elem: 'property' in elem.keys() and
                             'content' in elem.keys() and 
                             elem.get('property') == 'article:published_time', tree.iter('meta'))
        if len(date_elems) != 1:
            return None
        date_elem = max(date_elems)
        dateString = date_elem.get('content').strip()
        dateString = re.sub('\+.*', '', dateString)
        if len(dateString) == 0:
            return None
        return dateString

    def _picurl(self, tree):
        pic_elems =  filter(lambda elem: 'property' in elem.keys() and
                             'content' in elem.keys() and 
                             elem.get('property') == 'og:image', tree.iter('meta'))
        if len(pic_elems) != 1:
            return None
        pic_elem = max(pic_elems)
        pic_url = pic_elem.get('content').strip()
        if len(pic_url) == 0:
            return None
        return pic_url

    def __init__(self):
        super(LightSpeedURLInfoBox, self).__init__('Lightspeed Magazine URL')
