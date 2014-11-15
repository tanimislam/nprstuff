#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import gui_common, sys, datetime

class VQROnlineFrame(gui_common.MainFrame):
    def __init__(self, showFrame = True):
        super(NYTimesFrame, self).__init__('Virginia Quarterly Review Online Printer',
                                           VQROnlineURLInfoBox(),
                                           showFrame = showFrame)

class VQROnlineURLInfoBox(gui_common.URLInfoBox):
    def getMetaDataDict(self, tree):
        meta_dict = {}
        remap = { 'hdl' : 'title', 'author' : 'author', 'ptime' : 'date_string' }
        #
        # pic_url
        img_elems = filter(lambda elem: 'class' in elem.keys() and
                           elem.get('class') == 'field-image-file', tree.iter('figure'))
        if len(img_elems) != 1: return {}
        img_elem = max(img_elems)
        img_subelems = filter(lambda elem: 'typeof' in elem.keys() and
                              elem.get('typeof') == 'foaf:Image' and
                              'src' in elem.keys(), img_elem.iter('img'))
        if len(img_subelems) != 1: return {}
        meta_dict['pic_url'] = max(img_subelems).get('src')
        #
        
        elems_one = filter(lambda elem: 'name' in elem.keys() and
                           'content' in elem.keys() and
                           elem.get('name') in ( 'hdl', 'author', 'ptime'), tree.iter('meta'))
        meta_dict = { remap[elem.get('name')] : elem.get('content') for elem in elems_one }
        elems_two = filter(lambda elem: 'property' in elem.keys() and
                           elem.get('property') == 'og:image', tree.iter('meta'))
        for elem in elems_two:
            meta_dict['pic_url'] = elem.get('content')
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
        return datetime.datetime.strptime( dateString, '%Y%m%d%H%M%S' )

    def __init__(self):
        super(NYTimesURLInfoBox, self).__init__('NY Times URL')

if __name__=='__main__':
    qApp = QApplication(sys.argv)
    nyf = NYTimesFrame()
    sys.exit( qApp.exec_() )
