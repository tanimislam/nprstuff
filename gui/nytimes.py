#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os, sys, numpy, glob, requests, json
import lxml.html, datetime, pytz, textwrap
import titlecase, codecs, urllib2

class MainDialog(QGroupBox):
    def __init__(self, myParent):
        super(MainDialog, self).__init__()
        self.setWindowTitle('New York Times Printer')
        self.urlInfoBox = URLInfoBox( myParent )
        self.defaultFont = myParent.defaultFont
        self.authorName = QLabel('')
        self.dateLabel = QLabel('')
        self.titleLabel = QLabel('')
        self.articleText = QLabel('')
        self.toFileButton = QPushButton('Save to File')
        self.printButton = QPushButton('Print')
        self.printPreviewButton = QPushButton('Print Preview')
        self.showPictureButton = QPushButton('Show Article Pic')
        self.toFileButton.setEnabled(False)
        self.printButton.setEnabled(False)
        self.printPreviewButton.setEnabled(False)
        self.showPictureButton.setEnabled(False)
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
        qf = QFont( self.defaultFont, pointSize = 12 )
        self.articleText.setFont( qf )
        #
        # set layout
        qvlayout = QVBoxLayout()
        self.setLayout( qvlayout )
        qvlayout.addWidget( self._createTopWidget() )
        qsa = CustomScrollArea()
        qsa.setWidget( self.articleText )
        qsa.setWidgetResizable(True)        
        qvlayout.addWidget( qsa )
        self.articleText.setStyleSheet('QLabel { background-color: white; }')
        #
        # add slots
        self.urlInfoBox.returnPressed.connect( self.urlInfoBox.validateAndGetData )
        self.toFileButton.clicked.connect( myParent.toFile )
        self.printButton.clicked.connect( myParent.printData )
        self.printPreviewButton.clicked.connect( myParent.printPreviewData )
        self.showPictureButton.clicked.connect( myParent.showPicture )
        #
        # ctrl-Q
        exitAction = QAction(self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        self.addAction(exitAction)
        #
        # make visible, resize to something nice
        qfm = QFontMetrics( qf )
        wdth = int( 70 * qfm.averageCharWidth() * 1.25 )
        self.resize( wdth, 900)
        self.setFixedWidth( wdth )
        self.show()

    def _createTopWidget(self):
        topBox = QGroupBox()
        topBox.setStyleSheet('QGroupBox { background-color: #E4EEF2; }')
        qgl = QGridLayout()
        topBox.setLayout( qgl )
        qgl.addWidget( QLabel('New Yorker URL'), 0, 0, 1, 1)
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

class CustomScrollArea(QScrollArea):
    def __init__(self):
        super(CustomScrollArea, self).__init__()
        #
        toEndAction = QAction(self)
        toEndAction.setShortcut('End')
        toEndAction.triggered.connect( self.scrollToBottom )
        self.addAction(toEndAction)
        #
        toStartAction = QAction(self)
        toStartAction.setShortcut('Home')
        toStartAction.triggered.connect( self.scrollToTop )
        self.addAction(toStartAction)

    def scrollToBottom(self):
        sb = self.verticalScrollBar()
        sb.setValue( sb.maximum() )

    def scrollToTop(self):
        sb = self.verticalScrollBar()
        sb.setValue( sb.minimum())

class PictureLabel(QLabel):
    def __init__(self, myParent):
        super(PictureLabel, self).__init__()
        self.myParent = myParent
        self.resize(400, 400)
        self.setFixedSize(400, 400)
        self.setStyleSheet( 'background-color: #faf2e3' )
        self.hide()

    def closeEvent(self, evt):
        evt.ignore()
        self.myParent.closePicture()

    def mousePressEvent(self, evt):
        if evt.button() == Qt.RightButton:
            while( True ):
                fname = str(QFileDialog.getSaveFileName(self, 'Save Picture',
                                                        os.getcwd(), filter = '*.png') )
                if fname.lower().endswith('.png') or len(os.path.basename(fname)) == 0:
                    break
        if fname.lower().endswith('.png'):
            qpm = self.pixmap()
            qpm.save( fname )

class NewYorkerFrame(QApplication):
    def __init__(self, args):
        super(NewYorkerFrame, self).__init__(args)
        qfd = QFontDatabase()
        defaultFont = min(filter(lambda fam: qfd.isFixedPitch(fam), qfd.families()))
        if defaultFont is None:
            raise ValueError("Error, could find no fixed width fonts.")
        self.defaultFont = defaultFont
        self.mainDialog = MainDialog( self )
        self.pictureLabel = PictureLabel( self )

    def updateData(self, data_dict):
        self.mainDialog.authorName.setText( data_dict['author'] )
        self.mainDialog.titleLabel.setText( data_dict['title'] )
        self.mainDialog.dateLabel.setText( data_dict['date'].strftime('%B %d, %Y' ) )
        qpm = data_dict['image']
        self.pictureLabel.resize( qpm.size() )
        self.pictureLabel.setFixedSize( qpm.size() )
        self.pictureLabel.setPixmap( qpm )
        self.pictureLabel.setWindowTitle( data_dict['title'] )
        #
        # now set the text
        article_text = u'\n\n'.join([ textwrap.fill(txt) for txt in
                                      self.mainDialog.urlInfoBox.currentData ] )
        self.mainDialog.articleText.setText( article_text )
        #
        # now make those buttons enabled
        self.mainDialog.toFileButton.setEnabled(True)
        self.mainDialog.printButton.setEnabled(True)
        self.mainDialog.printPreviewButton.setEnabled(True)
        if qpm.size().width() != 0: self.mainDialog.showPictureButton.setEnabled(True)

    def toFile(self):
        if self.mainDialog.urlInfoBox.currentData is not None:
            self.mainDialog.setEnabled(False)
            while(True):
                fname = str(QFileDialog.getSaveFileName(self.mainDialog, 'Save File', 
                                                        os.getcwd(), filter = '*.txt' ) )
                if fname.lower().endswith('.txt') or len(os.path.basename(fname)) == 0:
                    break
            if fname.lower().endswith('.txt'):
                self.mainDialog.writeToFile( fname )
            self.mainDialog.setEnabled(True)
        
    def printPreviewData(self):
        dialog = QPrintPreviewDialog()
        self.mainDialog.setEnabled(False)
        qtd =  self.mainDialog.getQTextDocument()
        dialog.paintRequested.connect( qtd.print_ )
        dialog.exec_()
        self.mainDialog.setEnabled(True)
        
    def printData(self):
        dialog = QPrintDialog()
        self.mainDialog.setEnabled(False)
        if dialog.exec_() == QDialog.Accepted:
            qtd = self.mainDialog.getQTextDocument()
        self.mainDialog.setEnabled(True)

    def showPicture(self):
        self.mainDialog.setEnabled(False)
        self.pictureLabel.show()

    def closePicture(self):
        self.pictureLabel.hide()
        self.mainDialog.setEnabled(True)

class URLInfoBox(QLineEdit):
    
    @staticmethod
    def getHTMLTree(req):
        return lxml.html.fromstring( req.text )
        
    @staticmethod
    def getMetaData(tree):
        return filter(lambda elem: 'name' in elem.keys() and
                      elem.get('name') == 'parsely-page' and
                      'content' in elem.keys() , tree.iter('meta'))

    @staticmethod
    def getData( tree ):
        s_end = u'\u2666'
        paras = list( tree.iter('p') )
        last_idx =  max( enumerate(paras), key = lambda tup:
                             s_end in unicode(tup[1].text_content()) )[0]
        textData = [  unicode(para.text_content()) for para in paras[:last_idx+1] ]
        return last_idx, textData

    def __init__(self, myParent):
        assert(myParent is not None)
        assert(isinstance( myParent, NewYorkerFrame ) )
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
        meta_elems = URLInfoBox.getMetaData( tree )

        if len(meta_elems) != 1:
            self.setStyleSheet( 'background-color: white' )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT FIND METADATA FOR URL = %s.' % candURL
            return

        meta_elem = max(meta_elems)
        meta_dict = json.loads( meta_elem.get('content') )
        if len(set([ 'author', 'title', 'pub_date', 'image_url' ]) - set(meta_dict.keys())) != 0:
            self.setStyleSheet( 'background-color: white' )
            self.setText( self.currentURL )
            print 'ERROR, THESE ENTRIES = %s COULD NOT BE FOUND.' % \
                ( set([ 'author', 'title', 'pub_date', 'image_url' ]) - set(meta_dict.keys()) )
            return
        try:
            dt = datetime.datetime.strptime( meta_dict['pub_date'],
                                             '%Y-%m-%dT%H:%M:%SZ' )
        except Exception:
            self.setStyleSheet( 'background-color: white' )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT PARSE DATE STRING = %s.' % meta_dict['pub_date']
            return

        try:
            qpm = QPixmap()
            stat = qpm.loadFromData( urllib2.urlopen( meta_dict['image_url'] ).read() )
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
        
        data_dict = { 'title'  : titlecase.titlecase( meta_dict['title'] ),
                      'author' : meta_dict['author'],
                      'date' : dt,
                      'image' : qpm, 'image-url' : meta_dict['image_url'] }
        return data_dict

if __name__=='__main__':
    nyf = NewYorkerFrame(sys.argv)
    sys.exit( nyf.exec_() )
