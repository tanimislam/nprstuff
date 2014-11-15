#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import newyorker, nytimes, vqronline, sys

class MainGui(QTabWidget):
    def __init__(self):
        super(MainGui, self).__init__()
        nyf = newyorker.NewYorkerFrame(showFrame = False)
        nyt = nytimes.NYTimesFrame(showFrame = False)
        self.setStyleSheet('QTabWidget {background-color: #f4faff; }')
        self.addTab( nyf, QIcon('icons/newyorker.png'), 'New Yorker Printer' )
        self.addTab( nyt, QIcon('icons/nytimes.png'), 'NYTimes Printer' )
        self.addTab( vqronline.VQROnlineFrame(showFrame = False),
                     QIcon('icons/vqr.png'), 'VQR Online Printer')
        self.setWindowTitle('Main Printing GUI')
        self.setCurrentIndex(0)
        #
        # Ctrl-Q
        exitAction = QAction(self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        self.addAction(exitAction)
        #
        # Move-Right
        nextTabAction = QAction(self)
        nextTabAction.setShortcut('Ctrl+Right')
        nextTabAction.triggered.connect(self.nextTab)
        self.addAction(nextTabAction)
        #
        # Move-Left
        prevTabAction = QAction(self)
        prevTabAction.setShortcut('Ctrl+Left')
        prevTabAction.triggered.connect(self.prevTab)
        self.addAction(prevTabAction)
        #
        # make visible
        qfm = QFontMetrics( nyf.qf )
        wdth = int( 70 * qfm.averageCharWidth() * 1.25 )
        self.resize( wdth, 900)
        self.setFixedWidth( wdth )
        self.show()
        
    def nextTab(self):
        cIndx = self.currentIndex()
        if cIndx == self.count() - 1: nIndx = 0
        else: nIndx = cIndx + 1
        self.setCurrentIndex( nIndx )
    
    def prevTab(self):
        cIndx = self.currentIndex()
        if cIndx == 0: nIndx = self.count() - 1
        else: nIndx = cIndx - 1
        self.setCurrentIndex( nIndx )

if __name__=='__main__':
    qApp = QApplication(sys.argv)
    mg = MainGui()
    sys.exit(qApp.exec_() )
