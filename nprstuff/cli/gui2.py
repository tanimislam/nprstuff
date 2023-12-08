import os, sys
from PyQt5.QtWidgets import QApplication, qApp
from nprstuff import resourceDir

def _loginwindow( ):
    from nprstuff.gui2.gui_common import get_database_data
    from nprstuff.gui2 import login_window
    statusdict = get_database_data( )
    print( 'message = %s' % statusdict['message'] )
    qApp = QApplication( sys.argv )
    lw = login_window.LoginWindow( )
    lw.setFromStatus( statusdict )
    sys.exit( qApp.exec_( ) )

def _mainapp( ):
    from nprstuff.gui2 import main_app
    ma = main_app.MainApp( sys.argv )
    ma.doLogon( )
    sys.exit( ma.exec_( ) )
