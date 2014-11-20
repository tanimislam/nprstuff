#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import gui_common, sys, datetime, titlecase, re

class VQROnlineFrame(gui_common.MainFrame):
    def __init__(self, showFrame = True, iconPath = None):
        super(VQROnlineFrame, self).__init__('Virginia Quarterly Review Online Printer',
                                            VQROnlineURLInfoBox(),
                                            showFrame = showFrame,
                                            iconPath = iconPath)

class VQROnlineURLInfoBox(gui_common.URLInfoBox):
    def getMetaDataDict(self, tree):
        meta_dict = {}
        remap = { 'hdl' : 'title', 'author' : 'author', 'ptime' : 'date_string' }
        #
        # pic_url
        img_elems = filter(lambda elem: 'class' in elem.keys() and
                           elem.get('class') == 'field-image-file', tree.iter('figure'))
        if len(img_elems) == 0: return {}
        img_elem = img_elems[0]
        img_subelems = filter(lambda elem: 'typeof' in elem.keys() and
                              elem.get('typeof') == 'foaf:Image' and
                              'src' in elem.keys(), img_elem.iter('img'))
        if len(img_subelems) != 1: return {}
        meta_dict['pic_url'] = re.sub('^/+', 'http://', max(img_subelems).get('src'))
        #
        # title
        title_elems = filter(lambda elem: 'content' in elem.keys() and
                             'property' in elem.keys() and
                             elem.get('property') == 'dc:title',
                             tree.iter('meta'))
        if len(title_elems) != 1: return meta_dict
        title_elem = max(title_elems)
        meta_dict['title'] = title_elem.get('content')
        #
        # date_string
        date_elems = filter(lambda elem: 'class' in elem.keys() and
                            elem.get('class') == 'issue-title' and
                            len(list(elem.iter('a'))) == 1 and
                            max(list(elem.iter('a'))).text is not None,
                            tree.iter('div'))
        if len(date_elems) != 1: return meta_dict
        meta_dict['date_string'] = max(list(max(date_elems).iter('a'))).text_content().strip()
        #
        # author
        author_elems = filter(lambda elem: 'class' in elem.keys() and
                              elem.get('class') == 'byline' and
                              len(list(elem.iter('a'))) == 1 and
                              max(list(elem.iter('a'))).text is not None,
                              tree.iter('h3'))
        if len(author_elems) != 1: return meta_dict
        meta_dict['author'] = titlecase.titlecase(max(list(max(author_elems))).text_content().strip())            
        return meta_dict

    def getData(self, tree ):
        field_body_elems = filter(lambda elem: 'class' in elem.keys() and
                                  elem.get('class') == 'field-body', tree.iter('div'))
        if len(field_body_elems) != 1: return None
        field_body_elem = max(field_body_elems)
        paras = filter(lambda elem: elem.text is not None and
                       len(elem.text_content()) != 0, field_body_elem.iter('p'))
        textData = [  unicode(para.text_content()) for para in paras ]
        return textData

    def getDate(self, dateString):
        date_map = { 'Fall' : 'September 15',
                     'Winter' : 'December 15',
                     'Summer' : 'June 15',
                     'Spring' : 'March 15' }
        fixedString = ', '.join([ date_map[ dateString.split()[0] ],
                                  dateString.split()[1] ])
        return datetime.datetime.strptime( fixedString, '%B %d, %Y')

    def __init__(self):
        super(VQROnlineURLInfoBox, self).__init__('VQR Online URL')

if __name__=='__main__':
    qApp = QApplication(sys.argv)
    nyf = VQROnlineFrame(iconPath = 'icons/vqr.png')
    sys.exit( qApp.exec_() )
