#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os

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

