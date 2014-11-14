#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os, sys, numpy, glob, requests, json
import lxml.html, datetime, pytz, textwrap
import titlecase, codecs, urllib2, gui_common

class NYTimesFrame(QGroupBox):
    def __init__(self, mainFrame = True):
        super(NYTimesFrame, self).__init__()
        self.setWindowTitle('New York Times Printer')
        self.urlInfoBox = URLInfoBox( self )
        qfd = QFontDatabase()
        self.defaultFont = min(filter(lambda fam: qfd.isFixedPitch(fam), qfd.families()))
        if self.defaultFont is None:
            raise ValueError("Error, could find no fixed width fonts.")
        #
        self.pictureLabel = gui_common.PictureLabel( self )
        #
        self.authorName = QLabel('')
        self.dateLabel = QLabel('')
        self.titleLabel = QLabel('')
        self.articleText = QLabel('')
        self.toFileButton = QPushButton('Save to File')
        self.printButton = QPushButton('Print')
        self.printPreviewButton = QPushButton('Print Preview')
        self.showPictureButton = QPushButton('Show Article Pic')
        self.setStyleSheet('QGroupBox { background-color: #FCF5F5; }')
        for button in ( self.toFileButton, self.showPictureButton,
                        self.printButton, self.printPreviewButton ):
            button.setStyleSheet("""
            QPushButton { background-color: #EBF7EC;
            border-style: outset;
            border-width: 2px;
            border-radius: 10px;
            border-color: #E4EEF2 ;
            padding: 6px; }
            QPushButton:pressed {
            background-color: #FCF5F5;
            border-style: inset;
            }
            """)
        #
        # set font for articleText
        self.qf = QFont( self.defaultFont, pointSize = 12 )
        self.articleText.setFont( self.qf )
        #
        # set layout
        qvlayout = QVBoxLayout()
        self.setLayout( qvlayout )
        qvlayout.addWidget( self._createTopWidget() )
        self.qsa = gui_common.CustomScrollArea()
        self.qsa.setWidget( self.articleText )
        self.qsa.setWidgetResizable(True)        
        qvlayout.addWidget( self.qsa )
        self.articleText.setStyleSheet('QLabel { background-color: white; }')
        #
        # add slots
        self.urlInfoBox.returnPressed.connect( self.urlInfoBox.validateAndGetData )
        self.toFileButton.clicked.connect( self.toFile )
        self.printButton.clicked.connect( self.printData )
        self.printPreviewButton.clicked.connect( self.printPreviewData )
        self.showPictureButton.clicked.connect( self.showPicture )
        self._disableMainDialog()
        
        if mainFrame:
            #
            # ctrl-Q
            exitAction = QAction(self)
            exitAction.setShortcut('Ctrl+Q')
            exitAction.triggered.connect(qApp.quit)
            self.addAction(exitAction)        
            #
            # make visible, resize to something nice
            qfm = QFontMetrics( self.qf )
            wdth = int( 70 * qfm.averageCharWidth() * 1.25 )
            self.resize( wdth, 900)
            self.setFixedWidth( wdth )
            self.show()

    def _disableMainDialog(self):
        for widg in ( self.toFileButton, self.printButton, self.printPreviewButton, self.showPictureButton):
            widg.setEnabled(False)

    def _enableMainDialog(self):
        for widg in ( self.toFileButton, self.printButton, self.printPreviewButton, self.showPictureButton):
            widg.setEnabled(True)

    def _createTopWidget(self):
        topBox = QGroupBox()
        topBox.setStyleSheet('QGroupBox { background-color: #E4EEF2; }')
        qgl = QGridLayout()
        topBox.setLayout( qgl )
        qgl.addWidget( QLabel('NY Times URL'), 0, 0, 1, 1)
        qgl.addWidget( self.urlInfoBox, 0, 1, 1, 3)
        qgl.addWidget( QLabel('Author'), 1, 0, 1, 1)
        qgl.addWidget( self.authorName, 1, 1, 1, 2)
        qgl.addWidget( QLabel('Date Added'), 2, 0, 1, 1)
        qgl.addWidget( self.dateLabel, 2, 1, 1, 2)
        qgl.addWidget( QLabel('Title'), 3, 0, 1, 1)
        qgl.addWidget( self.titleLabel, 3, 1, 1, 2)
        qgl.addWidget( self.toFileButton, 4, 0, 1, 1)
        qgl.addWidget( self.printButton, 4, 1, 1, 1)
        qgl.addWidget( self.printPreviewButton, 4, 2, 1, 1)
        qgl.addWidget( self.showPictureButton, 4, 3, 1, 1)
        return topBox

    def getQTextDocument(self):
        tottext =  u'%s\n\n' % self.titleLabel.text()
        tottext += u'by %s\n\n' % self.authorName.text()
        tottext += u'%s\n\n' % self.dateLabel.text()
        tottext += self.articleText.text()
        qtd = QTextDocument( tottext )
        qtd.setDefaultFont( QFont( self.defaultFont, pointSize = 11 ) )
        qtd.setTextWidth( 85.0 )
        return qtd

    def writeToFile(self, filename):
        with codecs.open(filename, 'wb', 'utf-8') as outfile:
            outfile.write(u'%s\n\n' % self.titleLabel.text() )
            outfile.write(u'by %s\n\n' % self.authorName.text() )
            outfile.write(u'%s\n\n' % self.dateLabel.text() )
            for ptext in self.urlInfoBox.currentData[:-1]:
                outfile.write('%s\n\n' % textwrap.fill(ptext) )
            outfile.write('%s\n' % textwrap.fill( self.urlInfoBox.currentData[-1] ) )

    def updateData(self, data_dict):
        self.authorName.setText( data_dict['author'] )
        self.titleLabel.setText( data_dict['title'] )
        self.dateLabel.setText( data_dict['date'].strftime('%B %d, %Y' ) )
        qpm = data_dict['image']
        self.pictureLabel.resize( qpm.size() )
        self.pictureLabel.setFixedSize( qpm.size() )
        self.pictureLabel.setPixmap( qpm )
        self.pictureLabel.setWindowTitle( data_dict['title'] )
        #
        # now set the text
        article_text = u'\n\n'.join([ textwrap.fill(txt) for txt in
                                      self.urlInfoBox.currentData ] )
        self.articleText.setText( article_text )
        #
        # now make those buttons enabled
        self.toFileButton.setEnabled(True)
        self.printButton.setEnabled(True)
        self.printPreviewButton.setEnabled(True)
        if qpm.size().width() != 0: self.showPictureButton.setEnabled(True)

    def toFile(self):
        if self.urlInfoBox.currentData is not None:
            self._disableMainDialog()
            while(True):
                fname = str(QFileDialog.getSaveFileName(self, 'Save File', 
                                                        os.getcwd(), filter = '*.txt' ) )
                if fname.lower().endswith('.txt') or len(os.path.basename(fname)) == 0:
                    break
            if fname.lower().endswith('.txt'):
                self.writeToFile( fname )
            self._enableMainDialog()

    def printPreviewData(self):
        dialog = QPrintPreviewDialog()
        self._disableMainDialog()
        qtd =  self.getQTextDocument()
        dialog.paintRequested.connect( qtd.print_ )
        dialog.exec_()
        self._enableMainDialog()
        
    def printData(self):
        dialog = QPrintDialog()
        self._disableMainDialog()
        if dialog.exec_() == QDialog.Accepted:
            qtd = self.getQTextDocument()
        self._enableMainDialog()

    def showPicture(self):
        self._disableMainDialog()
        self.pictureLabel.show()

    def closePicture(self):
        self.pictureLabel.hide()
        self._enableMainDialog()

class URLInfoBox(QLineEdit):
    
    @staticmethod
    def getHTMLTree(req):
        return lxml.html.fromstring( req.text )
        
    @staticmethod
    def getMetaData(tree):
        elems_one = filter(lambda elem: 'name' in elem.keys() and
                           'content' in elem.keys() and
                           elem.get('name') in ( 'hdl', 'author', 'ptime'), tree.iter('meta'))
        meta_dict = { elem.get('name') : elem.get('content') for elem in elems_one }
        elems_two = filter(lambda elem: 'property' in elem.keys() and
                           elem.get('property') == 'og:image', tree.iter('meta'))
        for elem in elems_two:
            meta_dict['pic_url'] = elem.get('content')
        return meta_dict

    @staticmethod
    def getData( tree ):
        paras = filter(lambda elem: 'class' in elem.keys() and
                       elem.get('class') == "story-body-text story-content",
                       tree.iter('p'))
        textData = [  unicode(para.text_content()) for para in paras ]
        return len(paras) - 1, textData

    def __init__(self, myParent):
        assert(myParent is not None)
        assert(isinstance( myParent, NYTimesFrame ) )
        super(URLInfoBox, self).__init__('')
        self.myParent = myParent
        self.currentURL = ''
        self.currentData = None
        self.setStyleSheet( 'background-color: white' )

    def mousePressEvent(self, evt):
        self.setStyleSheet( 'background-color: #f3f1ff' )

    def validateAndGetData(self):
        data_dict = self._validateAndGetData(str(self.text()).strip(), updateText = False)
        self.myParent.updateData( data_dict )

    def _validateAndGetData(self, candURL, updateText = False):
        if candURL == self.currentURL and not updateText:
            self.setStyleSheet( 'background-color: white' )
            return
        
        try:
            req = requests.get(candURL)
        except Exception:
            self.setStyleSheet( 'background-color: white' )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT LOAD IN URL = %s.' % candURL
            return

        tree = URLInfoBox.getHTMLTree( req )
        
        #
        # look for metadata
        meta_dict = URLInfoBox.getMetaData( tree )
        if len(set([ 'author', 'hdl', 'ptime', 'pic_url' ]) - set(meta_dict.keys())) != 0:
            self.setStyleSheet( 'background-color: white' )
            self.setText( self.currentURL )
            print 'ERROR, THESE ENTRIES = %s COULD NOT BE FOUND.' % \
                ( set([ 'author', 'hdl', 'ptime', 'pic_url' ]) - set(meta_dict.keys()) )
            return
        try:
            dt = datetime.datetime.strptime( meta_dict['ptime'],
                                             '%Y%m%d%H%M%S' )
        except Exception:
            self.setStyleSheet( 'background-color: white' )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT PARSE DATE STRING = %s.' % meta_dict['ptime']
            return

        try:
            qpm = QPixmap()
            stat = qpm.loadFromData( urllib2.urlopen( meta_dict['pic_url'] ).read() )
        except Exception:
            self.setStyleSheet( 'background-color: white' )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT LOAD IMAGE URL = %s.' % meta_dict['image_url']
            return
        
        last_idx, textData = URLInfoBox.getData( tree )
        if last_idx == 0:
            self.setStyleSheet( 'background-color: white' )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT FIND ENDING CHARACTER IN %s.' % candURL
            return

        self.currentData = textData
        self.currentURL = candURL
        self.setStyleSheet( 'background-color: white' )
        
        data_dict = { 'title'  : titlecase.titlecase( meta_dict['hdl'] ),
                      'author' : meta_dict['author'],
                      'date' : dt,
                      'image' : qpm,
                      'image-url' : meta_dict['pic_url'] }
        return data_dict

if __name__=='__main__':
    qApp = QApplication(sys.argv)
    nyf = NYTimesFrame()
    sys.exit( qApp.exec_() )
