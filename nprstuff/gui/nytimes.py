import datetime
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from nprstuff.gui import gui_common

class NYTimesFrame(gui_common.MainFrame):
    def __init__(self, showFrame = True, iconPath = None):
        super(NYTimesFrame, self).__init__('New York Times Printer', NYTimesURLInfoBox(),
                                           showFrame = showFrame, iconPath = iconPath)

class NYTimesURLInfoBox(gui_common.URLInfoBox):
    def getMetaDataDict(self, tree):
        remap = { 'hdl' : 'title', 'author' : 'author', 'ptime' : 'date_string' }
        elems_one = list(
            filter(lambda elem: 'name' in elem.keys() and
                   'content' in elem.keys() and
                   elem.get('name') in ( 'hdl', 'author', 'ptime'), tree.iter('meta')))
        meta_dict = { remap[elem.get('name')] : elem.get('content') for elem in elems_one }
        elems_two = list(
            filter(lambda elem: 'property' in elem.keys() and
                   elem.get('property') == 'og:image', tree.iter('meta')))
        for elem in elems_two:
            meta_dict['pic_url'] = elem.get('content')
        return meta_dict

    def getData(self, tree ):
        paras = filter(lambda elem: 'class' in elem.keys() and
                       elem.get('class') == "story-body-text story-content",
                       tree.iter('p'))
        textData = [  unicode(para.text_content()) for para in paras ]
        return textData

    def getDate(self, dateString):
        return datetime.datetime.strptime( dateString, '%Y%m%d%H%M%S' )

    def __init__(self):
        super(NYTimesURLInfoBox, self).__init__('NY Times URL')

if __name__=='__main__':
    qApp = QApplication(sys.argv)
    nyf = NYTimesFrame(iconPath = 'icons/nytimes.png')
    sys.exit( qApp.exec_() )
