import os, sys, requests, logging, numpy, webbrowser
from requests_oauthlib import OAuth2Session
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#
from nprstuff import QDialogWithPrinting
from nprstuff.email import (
    oauthGetOauth2ClientGoogleCredentials, check_imgurl_credentials, get_imgurl_credentials, HtmlView,
    oauth_store_google_credentials, oauth_generate_google_permission_url )
from nprstuff.email.email_imgur import NPRStuffIMGClient

class NPRStuffImgurChooseAlbumWidget( QDialogWithPrinting ):
    changedAlbumSignal = pyqtSignal( str )
    
    def showHelpInfo( self ):
        pass

    def __init__( self, parent, data_imgurl, verify = True ):
        super( NPRStuffImgurChooseAlbumWidget, self ).__init__(
            parent, doQuit = False, isIsolated = True )
        self.hIMGClient = NPRStuffIMGClient( verify = verify, data_imgurl = data_imgurl )
        self.currentAlbumInfo = self.hIMGClient.get_candidate_albums( )
        self.main_album_name = self.hIMGClient.get_main_album_name( )
        self.setStyleSheet("""
        QWidget {
        font-family: Consolas;
        font-size: 11;
        }""" )
        #
        self.setModal( True )
        self.setWindowTitle( 'ALBUMS IN IMGUR ACCOUNT' )
        myLayout = QVBoxLayout( )
        self.setLayout( myLayout )
        self.albumTM = NPRStuffImgurChooseAlbumTableModel( self )
        self.albumTV = NPRStuffImgurChooseAlbumTableView( self )
        myLayout.addWidget( self.albumTV )
        #
        ##
        self.setFixedHeight( 450 )
        self.setFixedWidth( 430 )
        self.hide( )

    def add_album( self, new_album_name ):
        valid_names = set( self.currentAlbumInfo )
        if new_album_name in valid_names: return # do nothing
        self.hIMGClient.set_main_album( new_album_name )
        self.update( )

    def rename_main_album( self, new_album_name ):
        if self.main_album_name is None: return
        if self.main_album_name == new_album_name: return
        self.hIMGClient.change_album_name( new_album_name )
        self.update( )

    def delete_album( self, album_name ):
        if album_name not in set( self.currentAlbumInfo ): return
        self.hIMGClient.delete_candidate_album( album_name )
        self.update( )

    def set_main_album( self, album_name ):
        if self.main_album_name is None: return
        if self.main_album_name == album_name: return
        if len( self.currentAlbumInfo ) == 0: return
        if album_name not in self.currentAlbumInfo: return
        self.hIMGClient.set_main_album( album_name )
        self.update( )

    def update( self ):
        self.currentAlbumInfo = self.hIMGClient.get_candidate_albums( )
        self.main_album_name = self.hIMGClient.get_main_album_name( )
        self.albumTM.update( )
        self.changedAlbumSignal.emit( self.main_album_name )
        
class NPRStuffImgurChooseAlbumTableView( QTableView ):
    def __init__( self, parent ):
        super( NPRStuffImgurChooseAlbumTableView, self ).__init__( parent )
        self.parent = parent
        self.setModel( self.parent.albumTM )
        self.setShowGrid( True )
        self.verticalHeader( ).setSectionResizeMode( QHeaderView.Fixed )
        self.horizontalHeader( ).setSectionResizeMode( QHeaderView.Fixed )
        self.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.setSelectionMode( QAbstractItemView.SingleSelection )
        self.setSortingEnabled( False )
        #
        self.setColumnWidth( 0, 250 )
        self.setColumnWidth( 1, 150 )
        #
        toBotAction = QAction( self )
        toBotAction.setShortcut( 'End' )
        toBotAction.triggered.connect( self.scrollToBottom )
        self.addAction( toBotAction )
        #
        toTopAction = QAction( self )
        toTopAction.setShortcut( 'Home' )
        toTopAction.triggered.connect( self.scrollToTop )
        self.addAction( toTopAction )

    def add( self ):
        val, okPressed = QInputDialog.getText( self, "Candidate New Album Name", "Name:", QLineEdit.Normal, "" )
        if val.strip( ) == "": return
        if not okPressed: return
        self.parent.add_album( val.strip( ) )

    def rename_main_album( self ):
        val, okPressed = QInputDialog.getText( self, "Rename Main Album", "Name:", QLineEdit.Normal, "" )
        if val.strip( ) == "": return
        if not okPressed: return
        self.parent.rename_main_album( val.strip( ) )

    def delete_album( self ):
        indices_valid = filter(lambda index: index.column( ) == 0,
                               self.selectionModel( ).selectedIndexes( ) )
        row = max(map(lambda index: index.row( ), indices_valid ) )
        album_at_row = self.parent.albumTM.get_album_at_row( row )
        self.parent.delete_album( album_at_row )

    def set_main_album( self ):
        indices_valid = filter(lambda index: index.column( ) == 0,
                               self.selectionModel( ).selectedIndexes( ) )
        row = max(map(lambda index: index.row( ), indices_valid ) )
        album_at_row = self.parent.albumTM.get_album_at_row( row )
        self.parent.set_main_album( album_at_row )

    def contextMenuEvent( self, evt ):
        menu = QMenu( self )
        addAction = QAction( 'Add', menu )
        addAction.triggered.connect( self.add )
        menu.addAction( addAction )
        if len( self.parent.currentAlbumInfo ) != 0:
            setMainAction = QAction( 'Set Main Album', menu )
            setMainAction.triggered.connect( self.set_main_album )
            menu.addAction( setMainAction )
            renameAction = QAction( 'Rename', menu )
            renameAction.triggered.connect( self.rename_main_album )
            menu.addAction( renameAction )
            deleteAction = QAction( 'Delete', menu )
            deleteAction.triggered.connect( self.delete_album )
            menu.addAction( deleteAction )
        menu.popup( QCursor.pos( ) )

class NPRStuffImgurChooseAlbumTableModel( QAbstractTableModel ):
    def __init__( self, parent ):
        super( NPRStuffImgurChooseAlbumTableModel, self ).__init__( parent )
        self.parent = parent
        self.sortedAlbumNames = [ ]
        self.main_album = None
        self.update( )

    def rowCount( self, parent ):
        return len( self.sortedAlbumNames )

    def columnCount( self, parent ):
        return 2

    def flags( self, index ):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData( self, col, orientation, role ):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if col == 0: return 'ALBUM NAME'
            elif col == 1: return '# OF PICS'
        return None

    def update( self ):
        self.layoutAboutToBeChanged.emit( )
        self.sortedAlbumNames = sorted( self.parent.currentAlbumInfo )
        self.main_album = self.parent.main_album_name
        self.layoutChanged.emit( )

    def get_album_at_row( self, row ):
        assert( row >= 0 )
        assert( row < len( self.sortedAlbumNames ) )
        return self.sortedAlbumNames[ row ]
        
    def data( self, index, role ):
        if not index.isValid( ): return ""
        row = index.row( )
        col = index.column( )
        if role == Qt.BackgroundRole and self.sortedAlbumNames[ row ] == self.parent.main_album_name:
            color = QColor( "orange" )
            color.setAlphaF( 0.2 )
            return QBrush( color )
        elif role == Qt.DisplayRole:
            album_at_row = self.sortedAlbumNames[ row ]
            if col == 0: # name
                return album_at_row
            elif col == 1: # number of pics
                return len(
                    self.parent.currentAlbumInfo[ album_at_row ][ 'images' ] )

class NPRStuffConfigWidget( QDialogWithPrinting ):
    workingStatus = pyqtSignal( dict )
    workingStatusClosed = pyqtSignal( dict )
    _emitWorkingStatusDict = { }
    
    def showHelpInfo( self ):
        pass

    def getWorkingStatus( self ):
        return self._emitWorkingStatusDict.copy( )

    def __init__( self, service, verify = True ):
        super( NPRStuffConfigWidget, self ).__init__(
            None, isIsolated = True, doQuit = True )
        self.hide( )
        self.setModal( True )
        self.service = service
        self.verify = verify
        self.setWindowTitle( '%s CONFIGURATION' % service.upper( ) )

class NPRStuffConfigCredWidget( NPRStuffConfigWidget ):
    _emitWorkingStatusDict = {
        'IMGURL' : False,
        'GOOGLE' : True }

    def showHelpInfo( self ):
        pass

    def _initNPRStuffConfigCredStatus( self ):
        #
        ## look at the IMGURL
        def _get_creds( ):
            try:
                imgur_credentials = get_imgurl_credentials( )
                clientID = imgur_credentials[ 'clientID' ]
                clientSECRET = imgur_credentials[ 'clientSECRET' ]
                clientREFRESHTOKEN = imgur_credentials[ 'clientREFRESHTOKEN' ]
                mainALBUMID = ''
                if 'mainALBUMID' in imgur_credentials:
                    mainALBUMID = imgur_credentials[ 'mainALBUMID' ]
                mainALBUMNAME = ''
                if 'mainALBUMNAME' in imgur_credentials:
                    mainALBUMNAME = imgur_credentials[ 'mainALBUMNAME' ]
                return clientID, clientSECRET, clientREFRESHTOKEN, mainALBUMNAME
            except Exception as e:
                print( str( e ) )
                return '', '', '', ''

        clientID, clientSECRET, clientREFRESHTOKEN, mainALBUMNAME = _get_creds( )            
        try:
            if not check_imgurl_credentials(
                clientID, clientSECRET, clientREFRESHTOKEN,
                verify = self.verify ):
                raise ValueError( "Error, invalid imgurl creds.")
            self.imgurl_id.setText( clientID )
            self.imgurl_secret.setText( clientSECRET )
            self.imgurl_mainAlbumName.setText( mainALBUMNAME )
            self.imgurl_id.setStyleSheet( "QWidget {background-color: #370b4f;}" )
            self.imgurl_secret.setStyleSheet( "QWidget {background-color: #370b4f;}" )
            self.imgurl_status.setText( 'WORKING' )
            self.imgurl_seeMainAlbum.setEnabled( True )
            self._emitWorkingStatusDict[ 'IMGURL' ] = True
        except Exception as e:
            self.imgurl_id.setText( clientID )
            self.imgurl_secret.setText( clientSECRET )
            self.imgurl_mainAlbumName.setText( '' )
            self.imgurl_id.setStyleSheet( "QWidget {background-color: purple;}" )
            self.imgurl_secret.setStyleSheet( "QWidget {background-color: purple;}" )
            self.imgurl_status.setText( 'NOT WORKING' )
            self.imgurl_seeMainAlbum.setEnabled( False )
            self._emitWorkingStatusDict[ 'IMGURL' ] = False

        #
        ## now the GOOGLE
        try:
            cred2 = oauthGetOauth2ClientGoogleCredentials( )
            if cred2 is None:
                raise ValueError( "ERROR, PROBLEMS WITH GOOGLE CREDENTIALS" )
            self.google_status.setText( 'WORKING' )
            self._emitWorkingStatusDict[ 'GOOGLE' ] = True
        except Exception as e:
            self.google_status.setText( 'NOT WORKING' )
            self._emitWorkingStatusDict[ 'GOOGLE' ] = False

        self.workingStatus.emit( self._emitWorkingStatusDict )

    def pushIMGURLConfig( self ):
        clientID = self.imgurl_id.text( ).strip( )
        clientSECRET = self.imgurl_secret.text( ).strip( )
        def checkStatus( state ):
            if state:
                self.imgurl_status.setText( 'WORKING' )
                self.imgurl_id.setStyleSheet( "QWidget {background-color: #370b4f;}" )
                self.imgurl_secret.setStyleSheet( "QWidget {background-color: #370b4f;}" )
            else:
                self.imgurl_status.setText( 'NOT WORKING' )
                self.imgurl_id.setStyleSheet( "QWidget {background-color: purple;}" )
                self.imgurl_secret.setStyleSheet( "QWidget {background-color: purple;}" )
            self._emitWorkingStatusDict[ 'IMGURL' ] = state
            self.workingStatus.emit( self._emitWorkingStatusDict )

        ioauth2dlg = ImgurOauth2Dialog( self, clientID, clientSECRET )
        ioauth2dlg.emitState.connect( checkStatus )
        ioauth2dlg.show( )
        ioauth2dlg.exec_( )

    def setIMGURLMainAlbumConfig( self ):
        data_imgurl = get_imgurl_credentials( )
        picaw = NPRStuffImgurChooseAlbumWidget(
            self, data_imgurl = data_imgurl, verify = False )
        def changeMAINNAME( newAlbumMainName ):
            self.imgurl_mainAlbumName.setText( newAlbumMainName )

        picaw.changedAlbumSignal.connect( changeMAINNAME )
        picaw.show( )
        picaw.exec_( )

    def pushGoogleConfig( self ): # this is done by button
        def checkStatus( state ):
            if state:
                self.google_status.setText( 'WORKING' )
            else:
                self.google_status.setText( 'NOT WORKING' )
            self._emitWorkingStatusDict[ 'GOOGLE' ] = state
            self.workingStatus.emit( self._emitWorkingStatusDict )
        goauth2dlg = GoogleOauth2Dialog( self )
        goauth2dlg.emitState.connect( checkStatus )
        goauth2dlg.show( )
        goauth2dlg.exec_( )

    def __init__( self, verify = True ):
        super( NPRStuffConfigCredWidget, self ).__init__(
            'REST EMAIL CREDENTIALS', verify = verify )
        self.setStyleSheet("""
        QWidget {
        font-family: Consolas;
        font-size: 11;
        }""" )
        #
        ## gui stuff
        myLayout = QVBoxLayout( )
        self.setLayout( myLayout )
        #
        ## imgurl
        self.imgurl_id = QLineEdit( )
        self.imgurl_secret = QLineEdit( )
        self.imgurl_status = QLabel( )
        self.imgurl_oauth = QPushButton( 'CLIENT REFRESH' )
        self.imgurl_oauth.setAutoDefault( False )
        self.imgurl_mainAlbumName = QLabel( )
        self.imgurl_seeMainAlbum = QPushButton( 'MAIN ALBUMS' )
        self.imgurl_seeMainAlbum.setAutoDefault( False )
        imgurlWidget = QWidget( )
        imgurlWidget.setStyleSheet("""
        QWidget {
        background-color: #370b4f;
        }""" )
        imgurlLayout = QGridLayout( )
        imgurlWidget.setLayout( imgurlLayout )
        imgurlLayout.addWidget( QLabel( 'IMGURL' ), 0, 0, 1, 1 )
        imgurlLayout.addWidget( self.imgurl_oauth, 0, 1, 1, 2 )
        imgurlLayout.addWidget( self.imgurl_status, 0, 3, 1, 1 )
        imgurlLayout.addWidget( QLabel( 'ID' ), 1, 0, 1, 1 )
        imgurlLayout.addWidget( self.imgurl_id, 1, 1, 1, 3 )
        imgurlLayout.addWidget( QLabel( 'SECRET' ), 2, 0, 1, 1 )
        imgurlLayout.addWidget( self.imgurl_secret, 2, 1, 1, 3 )
        imgurlLayout.addWidget( QLabel( 'MAIN ALBUM NAME' ), 3, 0, 1, 1 )
        imgurlLayout.addWidget( self.imgurl_mainAlbumName, 3, 1, 2, 1 )
        imgurlLayout.addWidget( self.imgurl_seeMainAlbum, 3, 3, 1, 1 )
        myLayout.addWidget( imgurlWidget )
        #
        self.imgurl_oauth.clicked.connect(
            self.pushIMGURLConfig )
        self.imgurl_seeMainAlbum.clicked.connect(
            self.setIMGURLMainAlbumConfig )
        #
        ## google
        self.google_oauth = QPushButton( 'CLIENT REFRESH' )
        self.google_oauth.setAutoDefault( False )
        self.google_status = QLabel( )
        googleWidget = QWidget( )
        googleWidget.setStyleSheet("""
        QWidget {
        background-color: #450b4f;
        }""" )
        googleLayout = QHBoxLayout( )
        googleWidget.setLayout( googleLayout )
        googleLayout.addWidget( QLabel( 'GOOGLE' ) )
        googleLayout.addWidget( self.google_oauth )
        googleLayout.addWidget( self.google_status )
        myLayout.addWidget( googleWidget )
        #
        self.google_oauth.clicked.connect(
            self.pushGoogleConfig )
        #
        ## now initialize
        self._initNPRStuffConfigCredStatus( ) # set everything up
        self.setFixedWidth( self.sizeHint( ).width( ) * 1.25 )
        self.show( )

    def contextMenuEvent( self, event ):
        menu = QMenu( self )
        refreshAction = QAction( 'refresh cred config', menu )
        refreshAction.triggered.connect( self.initNPRStuffConfigCredStatus )
        menu.addAction( refreshAction )
        helpAction = QAction( 'help', menu )
        helpAction.triggered.connect( self.showHelpInfo )
        menu.addAction( helpAction )
        menu.popup( QCursor.pos( ) )

class ImgurOauth2Dialog( QDialogWithPrinting ):
    emitState = pyqtSignal( bool )

    def __init__( self, parent, imgur_clientId, imgur_clientSECRET ):
        if parent is not None:
            super( ImgurOauth2Dialog, self ).__init__(
                parent, isIsolated = True, doQuit = False )
            self.verify = parent.verify
        else:
            super( ImgurOauth2Dialog, self ).__init__(
                None, isIsolated = True, doQuit = True )
            self.verify = False
        self.setModal( True )
        self.setWindowTitle( 'PLEX ACCOUNT IMGUR OAUTH2 CREDENTIALS' )
        mainLayout = QVBoxLayout( )
        self.setLayout( mainLayout )
        self.imgur_clientId = imgur_clientId
        self.imgur_clientSECRET = imgur_clientSECRET
        #
        mainLayout.addWidget( QLabel(
            '\n'.join([
                       'FILL OUT THE MAIN URL (IN BROWSER BAR)',
                       'TO WHICH YOU ARE REDIRECTED IN THE END.'  ])))
        #
        authWidget = QWidget( )
        authLayout = QGridLayout( )
        authWidget.setLayout( authLayout )
        self.authCredentials = QLineEdit( )
        # self.authCredentials.setEchoMode( QLineEdit.Password )
        authLayout.addWidget( QLabel( 'URL:' ), 0, 0, 1, 1 )
        authLayout.addWidget( self.authCredentials, 0, 1, 1, 6 )
        mainLayout.addWidget( authWidget )
        #
        self.statusLabel = QLabel( )
        mainLayout.addWidget( self.statusLabel )
        #
        self.authCredentials.returnPressed.connect( self.check_authCredentials )
        self.setFixedWidth( 600 )
        self.setFixedHeight( self.sizeHint( ).height( ) )
        #
        ## now perform the launch window
        auth_url = 'https://api.imgur.com/oauth2/authorize'
        imgur = OAuth2Session( self.imgur_clientId )
        authorization_url, self.state = imgur.authorization_url(
            auth_url, verify = self.verify )
        #self.launchBrowser( authorization_url )
        webbrowser.open_new_tab( authorization_url )
        self.hide( )

    def launchBrowser( self, url ):
        self.statusLabel.setText( '' )
        qdl = QDialogWithPrinting( self, doQuit = False, isIsolated = True )
        #
        qdl.setModal( True )
        backButton = QPushButton( 'BACK' )
        forwardButton = QPushButton( 'FORWARD' )
        resetButton = QPushButton( 'RESET' )
        #
        ##
        qte = HtmlView( qdl )
        qte.load( QUrl( url ) )
        qdlLayout = QVBoxLayout( )
        qdl.setLayout( qdlLayout )
        qdlLayout.addWidget( qte )
        bottomWidget = QWidget( )
        bottomLayout = QHBoxLayout( )
        bottomWidget.setLayout( bottomLayout )
        bottomLayout.addWidget( resetButton )
        bottomLayout.addWidget( backButton )
        bottomLayout.addWidget( forwardButton )
        qdlLayout.addWidget( bottomWidget )
        qf = QFont( )
        qf.setFamily( 'Consolas' )
        qf.setPointSize( 11 )
        qfm = QFontMetrics( qf )
        qte.setMinimumSize( 85 * qfm.width( 'A' ), 550 )
        qdl.setMinimumSize( 85 * qfm.width( 'A' ), 550 )
        #
        def _reset( ): qte.load( QUrl( url ) )
        resetButton.clicked.connect( _reset )
        backButton.clicked.connect( qte.back )
        forwardButton.clicked.connect( qte.forward )
        #
        qte.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        qdl.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        self.statusLabel.setText( 'SUCCESS' )
        qdl.show( )
        qdl.exec_( )

    def check_authCredentials( self ):
        self.statusLabel.setText( '' )
        self.authCredentials.setText( str( self.authCredentials.text( ) ).strip( ) )
        response_url = str( self.authCredentials.text( ) )
        try:
            token_url = 'https://api.imgur.com/oauth2/token'
            imgur = OAuth2Session(
                client_id = self.imgur_clientId,
                state = self.state )
            token = imgur.fetch_token(
                token_url, client_secret = self.imgur_clientSECRET,
                authorization_response = response_url, verify = self.verify )
            self.authCredentials.setText( '' )
            stat =  store_imgurl_credentials(
                self.imgur_clientId,
                self.imgur_clientSECRET,
                token[ 'refresh_token' ] )
            assert( stat == 'SUCCESS' )
            self.accept( )
            self.emitState.emit( True )
        except Exception as e:
            logging.error( str( e ) )
            self.statusLabel.setText( 'ERROR: INVALID AUTHORIZATION CODE.' )
            self.authCredentials.setText( '' )
            self.emitState.emit( False )
        self.close( )

class GoogleOauth2Dialog( QDialogWithPrinting ):
    emitState = pyqtSignal( bool )
    
    def __init__( self, parent ):
        super( GoogleOauth2Dialog, self ).__init__(
            parent, isIsolated = True, doQuit = False )
        self.setModal( True )
        self.setWindowTitle( 'GOOGLE OAUTH2 CREDENTIALS' )
        mainLayout = QVBoxLayout( )
        self.setLayout( mainLayout )
        #
        mainLayout.addWidget( QLabel( 'TOOL TO STORE GOOGLE SETTINGS AS OAUTH2 TOKENS.' ) )
        #
        authWidget = QWidget( )
        authLayout = QGridLayout( )
        authWidget.setLayout( authLayout )
        self.authCredentials = QLineEdit( )
        self.authCredentials.setEchoMode( QLineEdit.Password )
        authLayout.addWidget( QLabel( 'CREDENTIALS:' ), 0, 0, 1, 1 )
        authLayout.addWidget( self.authCredentials, 0, 1, 1, 4 )
        mainLayout.addWidget( authWidget )
        #
        self.statusLabel = QLabel( )
        mainLayout.addWidget( self.statusLabel )
        #
        self.authCredentials.returnPressed.connect( self.check_authCredentials )
        self.setFixedWidth( 550 )
        self.setFixedHeight( self.sizeHint( ).height( ) )
        #
        self.flow, url = oauth_generate_google_permission_url( )
        #self.launchBrowser( url )
        webbrowser.open_new_tab( url )
        self.hide( )

    def launchBrowser( self, url ):
        self.statusLabel.setText( '' )
        qdl = QDialogWithPrinting( self, doQuit = False, isIsolated = True )
        #
        qdl.setModal( True )
        backButton = QPushButton( 'BACK' )
        forwardButton = QPushButton( 'FORWARD' )
        resetButton = QPushButton( 'RESET' )
        #
        ##
        qte = HtmlView( qdl )
        qte.load( QUrl( url ) )
        qdlLayout = QVBoxLayout( )
        qdl.setLayout( qdlLayout )
        qdlLayout.addWidget( qte )
        bottomWidget = QWidget( )
        bottomLayout = QHBoxLayout( )
        bottomWidget.setLayout( bottomLayout )
        bottomLayout.addWidget( resetButton )
        bottomLayout.addWidget( backButton )
        bottomLayout.addWidget( forwardButton )
        qdlLayout.addWidget( bottomWidget )
        qf = QFont( )
        qf.setFamily( 'Consolas' )
        qf.setPointSize( 11 )
        qfm = QFontMetrics( qf )
        qte.setMinimumSize( 85 * qfm.width( 'A' ), 550 )
        qdl.setMinimumSize( 85 * qfm.width( 'A' ), 550 )
        #
        def _reset( ): qte.load( QUrl( url ) )
        resetButton.clicked.connect( _reset )
        backButton.clicked.connect( qte.back )
        forwardButton.clicked.connect( qte.forward )
        #
        qte.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        qdl.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        self.statusLabel.setText( 'SUCCESS' )
        qdl.show( )
        qdl.exec_( )
        
    def check_authCredentials( self ):
        self.statusLabel.setText( '' )
        self.authCredentials.setText( self.authCredentials.text( ).strip( ) )
        authorization_code = self.authCredentials.text( ).strip( )
        try:
            credentials = self.flow.step2_exchange( authorization_code )
            oauth_store_google_credentials( credentials )
            self.authCredentials.setText( '' )
            self.accept( )
            self.emitState.emit( True )
        except:
            self.statusLabel.setText( 'ERROR: INVALID AUTHORIZATION CODE.' )
            self.authCredentials.setText( '' )
            self.emitState.emit( False )
        self.close( )
