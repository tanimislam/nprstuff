import sys, signal
 # code to handle Ctrl+C, convenience method for command line tools
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )
signal.signal( signal.SIGINT, signal_handler )
import logging, glob, os, warnings, qtmodern.styles, qtmodern.windows
from PyQt5.QtWidgets import QApplication, QMessageBox, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
from argparse import ArgumentParser
#
from nprstuff import resourceDir
from nprstuff.email import (
    oauthGetGoogleCredentials, check_imgurl_credentials, get_imgurl_credentials )
from nprstuff.email.email_gui import NPRStuffReSTEmailGUI as RestEmail
from nprstuff.email.email_config_gui import NPRStuffConfigCredWidget
#
warnings.simplefilter( 'ignore' )

def check_valid_imgurl_credentials( verify = True ):
    try:
        imgur_credentials = get_imgurl_credentials( )
        clientID = imgur_credentials[ 'clientID' ]
        clientSECRET = imgur_credentials[ 'clientSECRET' ]
        clientREFRESHTOKEN = imgur_credentials[ 'clientREFRESHTOKEN' ]
        return check_imgurl_credentials(
            clientID, clientSECRET, clientREFRESHTOKEN,
            verify = verify )
    except: return False

def check_google_credentials( verify = True ):
    try:
        cred2 = oauthGetGoogleCredentials( verify = verify )
        if cred2 is None: return False
    except: return False

class NowLaunchFromConfigClass( QApplication ):

    @classmethod
    def numWorkings( cls, workingStatusDict ):
        notWorkings = sorted(filter(lambda entry: workingStatusDict[ entry ] == False,
                                    workingStatusDict))
        return 2 - len( notWorkings )

    class NPRStuffConfigCredWidgetSub( NPRStuffConfigCredWidget ):
        statusSignal = pyqtSignal( )

        def __init__( self, verify ):
            super( NowLaunchFromConfigClass.NPRStuffConfigCredWidgetSub, self ).__init__( verify )
            hideAction = QAction( self )
            hideAction.setShortcut( 'Ctrl+W' )
            hideAction.triggered.connect( self.closeStuff )
            self.addAction( hideAction )

        def closeStuff( self ):
            self.workingStatusClosed.emit( self._emitWorkingStatusDict )
            self.statusSignal.emit( )
            self.hide( )
            
        def closeEvent( self, evt ):
            self.closeStuff( )
            evt.accept( )
    
    def __init__( self, verify = True ):
        super( QApplication, self ).__init__( [] )
        self.verify = verify
        self.setAttribute(Qt.AA_UseHighDpiPixmaps)
        icn = QIcon( os.path.join(
            resourceDir, 'icons', 'ReST-Email-Blue.svg' ) )
        self.setWindowIcon( icn )
        qtmodern.styles.dark( self )
        #
        self.email_config_gui = NowLaunchFromConfigClass.NPRStuffConfigCredWidgetSub( verify = verify )
        self.email_config_gui.workingStatusClosed.connect( self.nowLaunchFromConfig )
        self.rest_email = RestEmail( verify = verify )
        self.email_config_gui.hide( )
        self.rest_email.hide( )
        #
        self.mw_1 = qtmodern.windows.ModernWindow( self.email_config_gui )
        self.mw_2 = qtmodern.windows.ModernWindow( self.rest_email )
        self.email_config_gui.statusSignal.connect( self.mw_1.hide )
        self.mw_1.hide( )
        self.mw_2.hide( )
    
    def nowLaunchFromConfig( self, workingStatusDict ):
        assert( set( workingStatusDict ) == set([ 'IMGURL', 'GOOGLE' ]) )
        if all(list(zip(*workingStatusDict.items( )))[1]):
            self.launchRestEmail( )
        else:
            notWorkings = sorted(filter(lambda entry: workingStatusDict[ entry ] == False, workingStatusDict))
            msgText = 'THESE SERVICES DO NOT WORK: %s. Exiting...' % ' '.join( notWorkings )
            msgBox = QMessageBox( )
            msgBox.setText( msgText )
            msgBox.setWindowTitle( 'ERROR: %d SERVICES DO NOT WORK.' % len(notWorkings))
            returnValue = msgBox.exec( )

    def launchConfig( self ):
        self.email_config_gui.show( )
        self.mw_1.show( )

    def launchRestEmail( self ):
        self.rest_email.show( )
        self.mw_2.show( )

def main( ):
    parser = ArgumentParser( )
    parser.add_argument('--info', dest='do_info', action='store_true',
                        default = False, help = 'Run info mode if chosen.')
    parser.add_argument('--noverify', dest='do_verify', action='store_false',
                        default = True, help = 'Do not verify SSL transactions if chosen.')
    parser.add_argument('--reconfig', dest='do_nothing', action='store_false', default = True,
                        help = ' '.join([
                            'If chosen, then reconfigure the Imgurl credentials (or main windows)',
                            'or reconfigure the Google credentials',
                            '(by, for example, choosing a different Google account).' ]))
    args = parser.parse_args( )
    logger = logging.getLogger( )
    if args.do_info: logger.setLevel( logging.INFO )
    #
    statuses = {
        'IMGURL' : check_valid_imgurl_credentials( args.do_verify ),
        'GOOGLE' : check_google_credentials( args.do_verify ) }
    nlfc = NowLaunchFromConfigClass( verify = args.do_verify )
    if NowLaunchFromConfigClass.numWorkings( statuses ) == 2 and args.do_nothing:
        nlfc.launchRestEmail( )
    else: nlfc.launchConfig( )

    result = nlfc.exec( )
