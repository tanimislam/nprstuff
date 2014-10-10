#!/usr/bin/env python

import os, sys, numpy, pylab, requests
sys.path.append( os.path.dirname(os.path.dirname(
            os.path.abspath(__file__) ) ) )
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from newyorker import URLInfoBox

def test_bad_article():
    badURL = 'http://www.newyorker.com/magazine/2008/06/30/the-itch'
    tree = URLInfoBox.getHTMLTree( requests.get(badURL) )
    last_idx, textData = URLInfoBox.getData( tree )
    return last_idx, textData

def createQLabel( textData ):
    qlb = QLabel( u'\n\n'.join( textData ) )
    qlb.show()
    
    
    


