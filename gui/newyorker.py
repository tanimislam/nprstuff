#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import json, gui_common, sys, datetime

class NewYorkerFrame(gui_common.MainFrame):
    def __init__(self, showFrame = True, iconPath = None):
        super(NewYorkerFrame, self).__init__('New Yorker Printer', NewYorkerURLInfoBox(),
                                             showFrame = showFrame, iconPath = iconPath)        
        
class NewYorkerURLInfoBox(gui_common.URLInfoBox):
    def getMetaDataDict(self, tree):
        meta_elems = filter(lambda elem: 'name' in elem.keys() and
                            elem.get('name') == 'parsely-page' and
                            'content' in elem.keys() , tree.iter('meta'))
        if len(meta_elems) != 1: return {}
        meta_elem = max(meta_elems)
        meta_dict = json.loads( meta_elem.get('content') )
        remap = { 'author' : 'author', 'title' : 'title',
                  'pub_date' : 'date_string',
                  'image_url' : 'pic_url' }
        return { remap[ key ] : meta_dict[key] for key in set(meta_dict.keys()) and set(remap.keys()) }

    def getData(self, tree):
        textData = self._getDataOne(tree)
        if textData is not None: return textData
        return self._getDataTwo(tree)

    def _getDataOne( self, tree ):
        s_end = u'\u2666'
        paras = list( tree.iter('p') )
        last_idx =  max( enumerate(paras), key = lambda tup:
                         s_end in unicode(tup[1].text_content()) )[0]
        textData = [  unicode(para.text_content()) for para in paras[:last_idx+1] ]
        if last_idx == 0: return None
        return textData

    def _getDataTwo(self, tree):
        paras = filter(lambda elem: 'word_count' in elem.keys(), tree.iter('p'))
        if len(paras) == 0: return None
        textData = [ unicode(para.text_content()) for para in paras ]
        return textData

    def getDate( self, dateString ):
        return datetime.datetime.strptime( dateString,
                                           '%Y-%m-%dT%H:%M:%SZ' )
    
    def __init__(self):
        super(NewYorkerURLInfoBox, self).__init__('New Yorker URL')

if __name__=='__main__':
    qApp = QApplication(sys.argv)
    nyf = NewYorkerFrame()
    sys.exit( qApp.exec_() )
