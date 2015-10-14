#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os, sys, numpy, requests, json

class CustomScrollArea(QScrollArea):
    def __init__(self):
        super(CustomScrollArea, self).__init__()
        #
        toEndAction = QAction(self)
        toEndAction.setShortcut('End')
        toEndAction.triggered.connect( self.scrollToBottom )
        self.addAction( toEndAction )
        #
        toStartAction = QAction(self)
        toStartAction.setShortcut('Home')
        toStartAction.triggered.connect( self.scrollToTop )
        self.addAction( toStartAction )

    def scrollToBottom(self):
        sb = self.verticalScrollBar()
        sb.setValue( sb.maximum() )

    def scrollTopTop(self):
        sb = self.verticalScrollBar()
        sb.setValue( sb.minimum() )
