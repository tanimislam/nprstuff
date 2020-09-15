#!/usr/bin/env python3.7

import sys, signal
 # code to handle Ctrl+C, convenience method for command line tools
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
signal.signal( signal.SIGINT, signal_handler )
import logging, glob, os, warnings, qtmodern.styles, qtmodern.windows, time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
#
from nprstuff.email.email_imgur import PNGWidget
from nprstuff import QDialogWithPrinting

if __name__=='__main__':
    time0 = time.time( )
    logger = logging.getLogger( )
    logger.setLevel( logging.INFO )
    app = QApplication([])
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    qtmodern.styles.dark( app )
    pngw = PNGWidget( None )
    logging.info( 'got here in %0.3f seconds.' % (
        time.time( ) - time0 ) )
    pngw.show( )
    mw = qtmodern.windows.ModernWindow( pngw )
    mw.show( )
    result = app.exec_( )
