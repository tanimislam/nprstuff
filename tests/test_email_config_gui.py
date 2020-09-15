#!/usr/bin/env python3

import sys, signal
 # code to handle Ctrl+C, convenience method for command line tools
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
signal.signal( signal.SIGINT, signal_handler )
import logging, glob, os, warnings, qtmodern.styles, qtmodern.windows
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
#
from nprstuff.email.email_config_gui import NPRStuffConfigCredWidget

if __name__=='__main__':
    app = QApplication([])
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    qtmodern.styles.dark( app )
    nprccw = NPRStuffConfigCredWidget( verify = False )
    mw = qtmodern.windows.ModernWindow( nprccw )
    mw.show( )
    result = app.exec_( )
