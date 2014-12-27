#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import gui_common, sys, datetime, titlecase, re

class MediumFrame(gui_common.MainFrame):
    def __init__(self, showFrame = True, iconPath = None):
        super(VQROnlineFrame, self).__init__('Medium.com',
                                            MediumURLInfoBox(),
                                            showFrame = showFrame,
                                            iconPath = iconPath)

class MediumURLInfoBox(gui_common.URLInfoBox):
    def getMetaDataDict(self, tree):
        meta_dict = {}
        paras = filter(lambda elem: elem.text_content(), tree.iter('p'))
        #
        # pic_url FIXME
        meta_dict['pic_url'] = 'https://medium.com/apple-touch-icon-precomposed-152.png'
        #
        # title
        title_elems = filter(lambda elem: 'content' in elem.keys() and
                             'name' in elem.keys() and
                             elem.get('name') == 'title', tree.iter('meta'))
        if len(title_elems) != 1: return meta_dict
        title_elem = max(title_elems)
        meta_dict['title'] = titlecase.titlecase( title_elem.get('content') )
        #
        # date_string
        meta_dict['date_string'] = self.get_date_string( tree )
        #
        # author
        meta_dict['author'] = titlecase.titlecase( ' '.join(paras[0].text_content().split()[1:] ) )
        return meta_dict

    def get_date_string(self, tree ):
        elem = max( filter(lambda elem: 'CDATA' in elem.text_content() and 
                           'firstPublishedAt' in elem.text_content(), tree.iter('script')))
        txt = ' '.join(elem.text_content().split('\n'))
        txt = re.sub('.*firstPublishedAt":', '', txt)        
        dString = txt.split(',')[0]
        return dString

    def getData(self, tree ):
        field_body_elems = filter(lambda elem: 'class' in elem.keys() and
                                  elem.get('class') == 'field-body', tree.iter('div'))
        paras = filter(lambda elem: elem.text_content(), tree.iter('p'))
        textData = [  unicode(para.text_content()) for para in paras[2:-2] ]
        return textData

    def getDate(self, dateString):
        tStamp = int( dateString) / 1000.0
        return datetime.datetime.fromtimestam( tStamp )

    def __init__(self):
        super(MediumURLInfoBox, self).__init__('Medium.com')

if __name__=='__main__':
    qApp = QApplication(sys.argv)
    nyf = MediumFrame(iconPath = 'icons/medium.png')
    sys.exit( qApp.exec_() )
