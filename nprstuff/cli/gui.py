import os, sys
from PyQt5.QtWidgets import QApplication, qApp
from nprstuff import resourceDir

def _maingui( ):
    from nprstuff.gui import maingui
    qApp = QApplication( sys.argv )
    mg = maingui.MainGui( )
    sys.exit( qApp.exec_( ) )

def _lightspeed( ):
    from nprstuff.gui import lightspeed
    qApp = QApplication(sys.argv)
    lsf = lightspeed.LightSpeedFrame()
    sys.exit( qApp.exec_() )

def _medium( ):
    from nprstuff.gui import medium
    qApp = QApplication(sys.argv)
    nyf = medium.MediumFrame(
        iconPath = os.path.join( resourceDir, 'icons',
                                'medium.png' ) )
    sys.exit( qApp.exec_() )

def _newyorker( ):
    from nprstuff.gui import newyorker
    qApp = QApplication(sys.argv)
    nyf = newyorker.NewYorkerFrame()
    sys.exit( qApp.exec_() )

def _nytimes( ):
    from nprstuff.gui import nytimes
    qApp = QApplication(sys.argv)
    nyf = nytimes.NYTimesFrame(
        iconPath = os.path.join(
            resourceDir, 'icons', 'nytimes.png' ) )
    sys.exit( qApp.exec_() )

def _vqronline( ):
    from nprstuff.gui import vqronline
    qApp = QApplication(sys.argv)
    nyf = vqronline.VQROnlineFrame(
        iconPath = os.path.join(
            resourceDir, 'icons', 'vqr.png' ) )
    sys.exit( qApp.exec_() )
