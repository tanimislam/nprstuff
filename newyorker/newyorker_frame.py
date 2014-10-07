#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os, sys, numpy, glob, requests, json, textwrap
import lxml.html, datetime, pytz, urllib2, cStringIO
from PIL import Image

_styleSheetUnselect = 'background-color: #ffffff'
_styleSheetSelect = 'background-color: #cbdbff'
_send = u'\xa0\u2666'

class NewYorkerFrame(QApplication):
    def __init__(self, args):
        super(NewYorkerFrame, self).__init__(args)
        self.urlInfoBox = URLInfoBox( self )
        self.authorName = QLabel('')
        self.dateLabel = QLabel('')
        self.titleLabel = QLabel('')
        self.articleText = QLabel('')
        self.toFileButton = QPushButton('Save to File')
        self.printButton = QPushButton('Print')
        #
        # set font for articleText
        qf = QFont( 'Liberation Mono', pointSize = 12 )
        self.articleText.setFont( qf )
        #
        # add main frame
        self.mainFrame = QGroupBox()
        qvlayout = QVBoxLayout()
        self.mainFrame.setLayout( qvlayout )
        qvlayout.addWidget( self._createTopWidget() )
        qsa = QScrollArea()
        qsa.setWidget( self.articleText )
        qsa.setWidgetResizable(True)        
        qvlayout.addWidget( qsa )
        #
        # add slots
        self.urlInfoBox.returnPressed.connect( self.urlInfoBox.validateAndGetData )
        self.toFileButton.clicked.connect( self.toFile )
        self.printButton.clicked.connect( self.printData )
        #
        # make visible, resize to something nice
        qfm = QFontMetrics( qf )
        wdth = int( 70 * qfm.averageCharWidth() * 1.05 )
        self.mainFrame.resize(wdth, 400)
        self.mainFrame.setFixedWidth(wdth)
        self.mainFrame.show()
        
    def _createTopWidget(self):
        topBox = QGroupBox()
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
        qgl.addWidget( self.toFileButton, 4, 0, 1, 2)
        qgl.addWidget( self.printButton, 4, 2, 1, 2)
        return topBox

    def updatemeta(self, data_dict):
        self.authorName.setText( data_dict['author'] )
        self.titleLabel.setText( data_dict['title'] )
        self.dateLabel.setText( data_dict['date'].strftime('%B %d, %Y' ) )
        #
        # now set the text
        article_text = ''
        for ptext in self.urlInfoBox.currentData[:-1]:
            article_text += '%s\n\n' % textwrap.fill(ptext)
        article_text += '%s\n' % textwrap.fill( self.urlInfoBox.currentData[-1] )
        self.articleText.setText( article_text )

    def toFile(self):
        print 'CLICKED TO FILE BUTTON'
        
    def printData(self):
        print 'CLICKED PRINT ARTICLE'

class URLInfoBox(QLineEdit):
    def __init__(self, myParent):
        assert(myParent is not None)
        assert(isinstance( myParent, NewYorkerFrame ) )
        super(URLInfoBox, self).__init__('')
        self.myParent = myParent
        self.currentURL = ''
        self.currentData = None
        self.setStyleSheet( _styleSheetUnselect )

    def mousePressEvent(self, evt):
        self.setStyleSheet( _styleSheetSelect )

    def validateAndGetData(self):
        candURL = str(self.text()).strip()
        if candURL == self.currentURL:
            self.setStyleSheet( _styleSheetUnselect )
            return
        
        try:
            req = requests.get(candURL)
        except Exception:
            self.setStyleSheet( _styleSheetUnselect )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT LOAD IN URL = %s.' % candURL
            return

        tree = lxml.html.fromstring( req.text )
        
        #
        # look for metadata
        meta_elems = filter(lambda elem: 'name' in elem.keys() and
                            elem.get('name') == 'parsely-page' and
                            'content' in elem.keys() , tree.iter('meta'))
        if len(meta_elems) != 1:
            self.setStyleSheet( _styleSheetUnselect )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT FIND METADATA FOR URL = %s.' % candURL
            return

        meta_elem = max(meta_elems)
        meta_dict = json.loads( meta_elem.get('content') )
        if len(set([ 'author', 'title', 'pub_date', 'image_url' ]) - set(meta_dict.keys())) != 0:
            self.setStyleSheet( _styleSheetUnselect )
            self.setText( self.currentURL )
            print 'ERROR, THESE ENTRIES = %s COULD NOT BE FOUND.' % \
                ( set([ 'author', 'title', 'pub_date', 'image_url' ]) - set(meta_dict.keys()) )
            return
        try:
            dt = datetime.datetime.strptime( meta_dict['pub_date'],
                                             '%Y-%m-%dT%H:%M:%SZ' )
        except Exception:
            self.setStyleSheet( _styleSheetUnselect )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT PARSE DATE STRING = %s.' % meta_dict['pub_date']
            return

        try:
            data = cStringIO.StringIO(urllib2.urlopen( meta_dict['image_url'] ).read() )
            img = Image.open(data)
        except Exception:
            self.setStyleSheet( _styleSheetUnselect )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT LOAD IMAGE URL = %s.' % meta_dict['image_url']
            return

        paras = list( tree.iter('p') )
        last_idx =  max( enumerate(paras), key = lambda tup:
                             _send in tup[1].text_content() )[0]
        if last_idx is None:
            self.setStyleSheet( _styleSheetUnselect )
            self.setText( self.currentURL )
            print 'ERROR, COULD NOT FIND ENDING CHARACTER IN %s.' % candURL
            return None

        self.currentData = [ para.text_content() for para in paras[:last_idx+1] ]
        self.currentURL = candURL
        
        data_dict = { 'title'  : meta_dict['title'],
                      'author' : meta_dict['author'],
                      'date' : dt,
                      'imageURL' : img }
        self.myParent.updatemeta( data_dict )

if __name__=='__main__':
    nyf = NewYorkerFrame(sys.argv)
    sys.exit( nyf.exec_() )
