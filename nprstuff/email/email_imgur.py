import os, sys, base64, httplib2, numpy, glob, traceback
import hashlib, requests, io, datetime, logging, time
import pathos.multiprocessing as multiprocessing
from PIL import Image
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#
from nprstuff import QDialogWithPrinting
from nprstuff.email import (
    get_imgurl_credentials, store_imgurl_credentials, check_imgurl_credentials )

class PNGWidget( QDialogWithPrinting ):
    
    def __init__( self, parent ):
        time0 = time.time( )
        if parent is not None:
            super( PNGWidget, self ).__init__( parent, isIsolated = True, doQuit = False )
        else:
            super( PNGWidget, self ).__init__( parent, isIsolated = True, doQuit = True )
        self.setModal( True )
        self.parent = parent
        self.setWindowTitle( 'PNG IMAGES' )
        logging.debug( 'just about to initialize NPRStuffIMGClient in %0.3f seconds.' % (
            time.time( ) - time0 ) )
        self.nIMGClient = NPRStuffIMGClient( verify = False )
        logging.debug( 'initialized NPRStuffIMGClient in %0.3f seconds.' % (
            time.time( ) - time0 ) )
        #
        myLayout = QVBoxLayout( )
        self.setLayout( myLayout )        
        logging.debug( 'just about to initialize PNGPicTableModel in %0.3f seconds.' % (
            time.time( ) - time0 ) )
        self.pngPicTableModel = PNGPicTableModel( self )
        logging.debug( 'initialized PNGPicTableModel in %0.3f seconds.' % (
            time.time( ) - time0 ) )
        #
        topWidget = QWidget( self )
        topLayout = QHBoxLayout( )
        topWidget.setLayout( topLayout )
        topLayout.addWidget( QLabel( 'FILTER' ) )
        topLayout.addWidget( self.pngPicTableModel.filterOnNames )
        myLayout.addWidget( topWidget )
        #
        self.pngTV = PNGPicTableView( self )
        myLayout.addWidget( self.pngTV )
        myLayout.addWidget( self.pngPicTableModel.showingPNGPicturesLabel )
        #
        # self.setFixedWidth( self.pngTV.sizeHint( ).width( ) )
        self.resize( 550, 450 )
        self.setFixedHeight( 450 )
        self.hide( )

    def getAllDataAsDict( self ):
        return self.pngPicTableModel.getDataAsDict( )

class PNGPicDelegate( QItemDelegate ):
    def __init__( self ):
        super( PNGPicDelegate, self ).__init__( )

    def createEditor( self, parent, option, index ):
        return QLineEdit( parent )

    def setEditorData( self, editor, index ):
        index_unproxy = index.model( ).mapToSource( index )
        model = index.model( ).sourceModel( )
        row = index_unproxy.row( )
        col = index_unproxy.column ( )
        #
        name = model.pngPicObjects[ row ].actName
        if col == 0: editor.setText( name.strip( ) )

class PNGPicTableView( QTableView ):
    
    def __init__( self, parent ):
        super( PNGPicTableView, self ).__init__( parent )
        self.nIMGClient = parent.nIMGClient
        self.setModel( PNGPicQSortFilterModel( parent.pngPicTableModel ) )
        self.setItemDelegateForColumn( 0, PNGPicDelegate( ) )
        self.setShowGrid( True )
        self.verticalHeader( ).setSectionResizeMode( QHeaderView.Fixed )
        self.horizontalHeader( ).setSectionResizeMode( QHeaderView.Fixed )
        self.setSelectionBehavior( QAbstractItemView.SelectRows )
        self.setSelectionMode( QAbstractItemView.SingleSelection )
        self.setSortingEnabled( True )
        #
        self.setColumnWidth( 0, 270 )
        self.setColumnWidth( 1, 55 )
        self.setColumnWidth( 2, 85 )
        #self.setFixedWidth( 410 )
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
        pngFileName, _ = QFileDialog.getOpenFileName(
            self, 'Choose PNG file', os.getcwd( ), filter = '*.png' )
        if len( os.path.basename( pngFileName.strip( ) ) ) == 0:
            return
        if not os.path.isfile( pngFileName ):
            return

        #
        ## now check to see if this image already in nIMGClient
        imgMD5 = NPRStuffIMGClient.get_image_md5(
            Image.open( pngFileName.strip( ) ) )
        if imgMD5 in self.nIMGClient.imghashes: return
        
        #
        ## now collisions in name are not allowed, just pick a random name
        model = self.model( ).sourceModel( )
        if os.path.basename( pngFileName.strip( ) ) in set(
            map(lambda pngpo: pngpo.actName, model.pngPicObjects ) ):
            actName = os.path.join( os.path.dirname( pngFileName.strip( ) ),
                                    'figure-%s.png' % str( uuid.uuid4( ) ).split('-')[0] )
        else:
            actName = pngFileName.strip( )

        self.model( ).sourceModel( ).addPicObject(
            PNGPicObject( {
                'initialization' : 'FILE',
                'filename' : pngFileName,
                'actName' : actName }, self.nIMGClient ) )
    
    def copyImageURL( self ):
        indices_valid_row = self.getValidIndicesAtRow( )
        if indices_valid_row is None or len( indices_valid_row ) == 0: return
        self.model( ).sourceModel( ).copyURLAtRow( max( indices_valid_row ) )
        
    def info( self ):
        indices_valid_row = self.getValidIndicesAtRow( )
        if indices_valid_row is None or len( indices_valid_row ) == 0: return
        self.model( ).sourceModel( ).infoOnPicAtRow( max( indices_valid_row ) )

    def remove( self ):
        indices_valid_row = self.getValidIndicesAtRow( )
        if indices_valid_row is None or len( indices_valid_row ) == 0: return
        self.model( ).sourceModel( ).removePicObject( max( indices_valid_row ) )

    def removeAndDelete( self ):
        indices_valid_row = self.getValidIndicesAtRow( )
        if indices_valid_row is None or len( indices_valid_row ) == 0: return
        self.model( ).sourceModel( ).removeAndDeletePicObject( max( indices_valid_row ) )
        
    def contextMenuEvent( self, event ):
        menu = QMenu( self )
        addAction = QAction( 'Add', menu )
        addAction.setShortcut( 'Ctrl+O' )
        addAction.triggered.connect( self.add )
        menu.addAction( addAction )
        if len( self.model( ).sourceModel( ).pngPicObjects ) != 0:
            copyURLAction = QAction( 'Copy Image URL', menu )
            copyURLAction.triggered.connect( self.copyImageURL )
            menu.addAction( copyURLAction )
            infoAction = QAction( 'Information', menu )
            infoAction.triggered.connect( self.info )
            menu.addAction( infoAction)
            #removeAction = QAction( 'Remove', menu )
            #removeAction.triggered.connect( self.remove )
            #menu.addAction( removeAction )
            removeAndDeleteAction = QAction( 'Remove and Delete', menu )
            removeAndDeleteAction.triggered.connect( self.removeAndDelete )
            menu.addAction( removeAndDeleteAction )
        menu.popup( QCursor.pos( ) )

    def getValidIndicesAtRow( self ):
        try:
            indices_valid_proxy = list(
                filter(
                    lambda index: index.column( ) == 0,
                    self.selectionModel( ).selectedIndexes( ) ) )
            indices_valid = list(map(
                lambda index_proxy: self.model( ).mapToSource( index_proxy ),
                indices_valid_proxy ) )
            return list(map(lambda index: index.row( ), indices_valid ) )
        except: return [ ]

    def resizeEvent( self, evt ):
        width = self.size( ).width( )
        self.setColumnWidth( 0, int( 270.0 / 410 * width ) )
        self.setColumnWidth( 1, int( 55.0 / 410 * width ) )
        self.setColumnWidth( 2, int( 85.0 / 410 * width ) )

class PNGPicQSortFilterModel( QSortFilterProxyModel ):
    def __init__( self, model ):
        super( PNGPicQSortFilterModel, self ).__init__( )
        assert( isinstance( model, PNGPicTableModel ) )
        self.setSourceModel( model )
        model.emitFilterChanged.connect( self.invalidateFilter )

    def filterAcceptsRow( self, rowNumber, sourceParent ):
        return self.sourceModel( ).filterRow( rowNumber )

class PNGPicTableModel( QAbstractTableModel ):
    _columnNames = [ 'PNG PICTURE',  'WIDTH IN CM', 'UPLOADED' ]
        
    statusSignal = pyqtSignal( str )
    emitFilterChanged = pyqtSignal( )
    
    def __init__( self, parent ):
        super(PNGPicTableModel, self).__init__( parent )
        self.parent = parent
        #
        self.filterOnNames = QLineEdit( '' )
        self.filterRegExp = QRegExp( '.', Qt.CaseInsensitive, QRegExp.RegExp )
        self.filterOnNames.textChanged.connect( self.setFilterString )
        self.showingPNGPicturesLabel = QLabel( '' )
        self.emitFilterChanged.connect( self.showNumberPNGPictures )
        #
        self.layoutAboutToBeChanged.emit( )
        self.pngPicObjects = sorted( PNGPicObject.createPNGPicObjects(
            parent.nIMGClient ), key = lambda pngpo: pngpo.imgDateTime )[::-1]
        self.layoutChanged.emit( )
        #
        self.showNumberPNGPictures( )

    def infoOnPicAtRow( self, actualRow ):
        currentRow = self.pngPicObjects[ actualRow ]
        currentRow.getInfoGUI( self.parent )

    def rowCount( self, parent ):
        return len( self.pngPicObjects )

    def columnCount( self, parent ):
        return len( self._columnNames )

    def flags( self, index ):
        col = index.column( )
        if col in ( 0, ):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData( self, col, orientation, role ):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._columnNames[ col ]
        return None

    def setData( self, index, value, role ):
        col = index.column( )
        row = index.row( )
        if col == 0:
            picObjNames = set(map(lambda picObject: picObject.actName, self.pngPicObjects ) )
            candActName = os.path.basename( value.strip( ) )
            if not candActName.endswith('.png'):
                return False
            if candActName in picObjNames:
                return False
            self.pngPicObjects[ row ].changeName(
                candActName, self.parent.nIMGClient )
            return True
        elif col == 1:
            try:
                currentWidth = float( str( value.toString( ) ).strip( ) )
                if currentWidth <= 0:
                    return False
                self.pngPicObjects[ row ].currentWidth = currentWidth
                return True
            except Exception as e:
                return False

    def data( self, index, role ):
        if not index.isValid( ): return None
        row = index.row( )
        col = index.column( )
        if role == Qt.BackgroundRole:
            color = QColor( 'yellow' )
            color.setAlphaF( 0.2 )
            return QBrush( color )
        elif role == Qt.DisplayRole:
            if col == 0:
                return self.pngPicObjects[ row ].actName
            elif col == 1:
                return '%0.3f' % self.pngPicObjects[ row ].currentWidth
            elif col == 2:
                return self.pngPicObjects[ row ].imgDateTime.strftime( '%d/%m/%Y' )

    def sort( self, col, order ): # sort on datetime
        self.layoutAboutToBeChanged.emit( )
        if col == 0: # name
            self.pngPicObjects.sort(
                key = lambda pngpo: pngpo.actName  )
        elif col == 1: # image width
            self.pngPicObjects.sort(
                key = lambda pngpo: -pngpo.originalWidth )
        elif col == 2: # date uploaded
            self.pngPicObjects.sort(
                key = lambda pngpo: pngpo.imgDateTime )
        self.layoutChanged.emit( )

    def copyURLAtRow( self, row ):
        assert( row >= 0 and row < len( self.pngPicObjects ) )
        pngpo = self.pngPicObjects[ row ]
        QApplication.clipboard( ).setText( pngpo.imgurlLink )

    def removePicObject( self, row ):
        assert( row >= 0 and row < len( self.pngPicObjects ) )
        pngpo = self.pngPicObjects.pop( row )
        pngpo.delete( parent.plexImgClient )
        self.layoutAboutToBeChanged.emit( )
        self.layoutChanged.emit( )

    def removeAndDeletePicObject( self, row ):
        assert( row >= 0 and row < len( self.pngPicObjects ) )
        pngpo = self.pngPicObjects.pop( row )
        self.parent.nIMGClient.delete_image( pngpo.b64string, pngpo.imgMD5 )
        self.layoutAboutToBeChanged.emit( )
        self.layoutChanged.emit( )

    def addPicObject( self, pngPicObject ):
        picObjNames = set(map(lambda picObject: picObject.actName, self.pngPicObjects ) )
        assert( pngPicObject.actName not in picObjNames )
        self.pngPicObjects.append( pngPicObject )
        self.layoutAboutToBeChanged.emit( )
        self.layoutChanged.emit( )

    def getDataAsDict( self ):
        data = { }
        for pngpo in self.pngPicObjects:
            b64data, widthInCM, link = pngpo.b64String( )
            data[ pngpo.actName ] = ( b64data, widthInCM, link )
        return data

    def filterRow( self, rowNumber ):
        assert( rowNumber >= 0 )
        assert( rowNumber < len( self.pngPicObjects ) )
        name = self.pngPicObjects[ rowNumber ].actName
        return self.filterRegExp.indexIn( name ) != -1

    def setFilterString( self, newString ):
        mytext = newString.strip( )
        if len( mytext ) == 0: mytext = '.'
        self.filterRegExp = QRegExp( mytext, Qt.CaseInsensitive, QRegExp.RegExp )
        self.emitFilterChanged.emit( )

    def showNumberPNGPictures( self ):
        num_pics = len(list(filter(self.filterRow, range(len(self.pngPicObjects)))))
        self.showingPNGPicturesLabel.setText( 'SHOWING %d PNG PICTURES' % num_pics )

class NPRStuffIMGClient( object ):
    """
    This object contains and implements the collection of images located in a single main album in the Imgur_ account. This uses the Imgur_ API to peform all operations. This object is constructed using Imgur_ credentials -- the client ID, secret, and refresh token -- stored in the SQLite3_ configuration database, and stores the following attributes: the client ID, secret, refresh token, and the *access token* used for API access to your Imgur_ album and images.

    If the Imgur_ albums cannot be accessed, or there are no albums, then ``self.albumID = None``, the ``self.imgHashes`` is an empty :py:class:`dict`.

    The main album ID is stored as a :py:class:`string <str>` in the Imgur_ configuration under the ``mainALBUMID`` key, if it exists; otherwise the Imgur_ configuration dictionary does not have a ``mainALBUMID`` key.

    * If there is no main album ID defined, or if there is no album with that ID, then we choose the first album found, and reset the Imgur_ configuration data into the SQLite3_ database with this album ID and name.

    * If the configured album exists in our Imgur_ library, then continue with this the main album.

    Once the main album is found, populate ``self.imghashes`` with all the pictures in this album. The pictures in an album in our Imgur_ account are expected to be filled through methods in this object.

    * The key is the MD5_ hash of the image in that library.
    
    * The value is a four element :py:class:`tuple`: image name, image ID, the URL link to this image, and the :py:class:`datetime <datetime.datetime>` at which the image was uploaded.

    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param dict data_imgurl: optional argument. If defined, must have the following keys: ``clientID``, ``clientSECRET``, and ``clientREFRESHTOKEN``. Must be consistent with :py:class:`dict` returned by :py:meth:`get_imgurl_credentials <nprstuff.email.get_imgurl_credentials>`.
    
    :var bool verify: whether to verify SSL connections.
    :var str access_token: the persistent API access token to the user's Imgur_ account.
    :var str clientID: the Imgur_ client ID.
    :var str clientSECRET: the Imgur_ client secret.
    :var str albumID: the hashed name of the main album.
    :var dict imghashes: the structure of images stored in the main album.

    :raise ValueError: if images in the new album cannot be accessed.

    .. seealso:: :py:meth:`refreshImages <howdy.email.email_imgur.NPRStuffIMGClient.refreshImages>`.
    
    .. _MD5: https://en.wikipedia.org/wiki/MD5
    """

    @classmethod
    def get_image_md5( cls, image ):
        """
        :returns: the MD5_ hash of the image.
        :param image: the native Pillow PNG image object.
        :type image: :py:class:`PngImageFile <PIL.PngImagePlugin.PngImageFile>`
        """
        with io.BytesIO( ) as buf:
            image.save( buf, format = 'PNG' )
            b64string = base64.b64encode( buf.getvalue( ) )
            imgMD5 = hashlib.md5( b64string ).hexdigest( )
            return imgMD5
    
    def __init__( self, verify = True, data_imgurl = None ):
        time0 = time.time( )
        #
        ## https://api.imgur.com/oauth2 advice on using refresh tokens
        self.verify = verify
        if data_imgurl is None:
            data_imgurl = get_imgurl_credentials( )
        clientID = data_imgurl[ 'clientID' ]
        clientSECRET = data_imgurl[ 'clientSECRET' ]
        clientREFRESHTOKEN = data_imgurl[ 'clientREFRESHTOKEN' ]
        response = requests.post(
            'https://api.imgur.com/oauth2/token',
            data = {'client_id': clientID,
                    'client_secret': clientSECRET,
                    'grant_type': 'refresh_token',
                    'refresh_token': clientREFRESHTOKEN },
            verify = self.verify )
        if response.status_code != 200:
            raise ValueError( "ERROR, COULD NOT GET ACCESS TOKEN." )
        logging.debug( 'was able to check is valid IMGUR access in %0.3f seconds.' % (
            time.time( ) - time0 ) )
        data = response.json( )
        self.logger = logging.getLogger( )
        self.access_token = data[ 'access_token' ]
        self.clientID = clientID
        self.clientSECRET = clientSECRET
        self.clientREFRESHTOKEN = clientREFRESHTOKEN
        self.imghashes = { }
        #
        ## now first see if there are any albums
        response = requests.get( 'https://api.imgur.com/3/account/me/albums',
                                 headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                 verify = verify )

        #
        ## error state #1: cannot access my own albums
        if response.status_code != 200:
            self.albumID = None
            return
        logging.debug( 'was able to access albums in %0.3f seconds.' % (
            time.time( ) - time0 ) )

        #
        ## error state #2: do not have any albums
        albumDatas = response.json( )[ 'data' ]
        if len( albumDatas ) == 0:
            self.albumID = None
            return

        logging.debug( 'could find my albums in %0.3f seconds.' % (
            time.time( ) - time0 ) )

        #
        ## three possible situations
        ## #1: if mainALBUMID not defined OR album name not defined, use first img hash
        if 'mainALBUMID' not in data_imgurl or data_imgurl[ 'mainALBUMID' ] not in set(map(lambda albumData: albumData['id'], albumDatas)):
            sorting_cand = min(map(lambda albumData: ( albumData[ 'id' ], albumData[ 'title' ] ), albumDatas ),
                               key = lambda tup: tup[1] )
            self.albumID, albumName = sorting_cand
            #
            ## put new information into database
            store_imgurl_credentials(
                clientID, clientSECRET, clientREFRESHTOKEN, 
                mainALBUMID = self.albumID,
                mainALBUMNAME = albumName,
                verify = verify )
        else:
            self.albumID = data_imgurl['mainALBUMID']
        #
        ## now get all the images in that album
        ## remember: Authorization: Bearer YOUR_ACCESS_TOKEN
        logging.debug( 'got out to refreshImages in %0.3f seconds.' % (
            time.time( ) - time0 ) )
        self.refreshImages( )

    def get_main_album_name( self ):
        """
        :returns: the name of the main Imgur_ album, if albums exist on this account. Otherwise returns ``None``.
        :rtype: str
        """
        if self.albumID is None: return None
        response = requests.get( 'https://api.imgur.com/3/album/%s' % self.albumID,
                                 headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                 verify = self.verify )
        if response.status_code != 200: return None
        return response.json( )[ 'data' ][ 'title' ]

    def change_album_name( self, new_album_name ):
        """
        Changes the main album name to a new name, only if the new name is different from the old name.

        :param str new_album_name: the new name to change the main Imgur_ album.

        .. seealso:: :py:meth:`refreshImages <howdy.email.email_imgur.NPRStuffIMGClient.refreshImages>`.
        """
        if new_album_name == self.get_main_album_name( ): return
        response = requests.post( 'https://api.imgur.com/3/album/%s' % self.albumID,
                                  data = { 'title' : new_album_name },
                                  headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                  verify = self.verify )
        if response.status_code != 200: return

        #
        ## put new information into database
        store_imgurl_credentials(
            self.clientID, self.clientSECRET, self.clientREFRESHTOKEN, 
            mainALBUMID = self.albumID,
            mainALBUMNAME = new_album_name,
            verify = self.verify )
        
        self.refreshImages( )

    def set_main_album( self, new_album_name ):
        """
        Sets or changes the main Imgur_ album used for storing and displaying images to a new album name. If ``new_album_name`` exists in the Imgur_ account, then sets that name. If ``new_album_name`` does not exist, then creates this new Imgur_ album.

        Once this album is set or created,

        * sets the new Imgur_ credentials using :py:meth:`store_imgur_credentials <nprstuff.email.store_imgurl_credentials>`.

        * populates ``self.imghashes`` with all the images found in this library. If the album does not exist, then ``self.imghashes`` is an empty :py:class:`dict`.
        
        :param str new_album_name: the new name of the Imgur_ album to use for images.
        :raise ValueError: if images in the new album cannot be accessed.

        .. seealso:: :py:meth:`refreshImages <howdy.email.email_imgur.NPRStuffIMGClient.refreshImages>`.
        """

        #
        ## if nothing there, then make new album
        response = requests.get( 'https://api.imgur.com/3/account/me/albums',
                                 headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                 verify = self.verify )
        if response.status_code != 200:
            return

        albumDatas = response.json( )[ 'data' ]
        albumNames = dict(map(lambda albumData: ( albumData[ 'title' ], albumData[ 'id' ] ), albumDatas ) )
        if new_album_name in albumNames:
            self.albumID = albumNames[ new_album_name ]
            
        else: # create this album
            response = requests.post( 'https://api.imgur.com/3/album',
                                      headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                      data = { 'title' : new_album_name, 'privacy' : 'public' },
                                      verify = self.verify )
            if response.status_code != 200: return
            data = response.json( )[ 'data' ]
            self.albumID = data[ 'id' ]

        #
        ## put new information into database
        store_imgurl_credentials(
            self.clientID, self.clientSECRET, self.clientREFRESHTOKEN, 
            mainALBUMID = self.albumID,
            mainALBUMNAME = new_album_name,
            verify = self.verify )
            
        #
        ## now get all the images in that album
        ## remember: Authorization: Bearer YOUR_ACCESS_TOKEN
        self.refreshImages( )

    def get_candidate_album_names( self ):
        """
        :returns: a :py:class:`list` of album names in the Imgur_ account. :py:meth:`set_main_album <howdy.email.PlexIMGClient.set_main_album>` can use this method to determine the valid album name to choose.

        .. seealso:: :py:meth:`get_candidate_albums <howdy.email.PlexIMGClient.get_candidate_albums>`.
        """
        return sorted( self.get_candidate_albums( ) )

    def get_candidate_albums( self ):
        """
        :returns: a :py:class:`dict` of album information, organized by album name. Each key in the top-level dictionary is the album name. Each value is a lower level dictionary: the ``id`` key is the album ID, and the ``images`` key is a :py:class:`list` of low-level Imgur_ image information.
        """
        response = requests.get( 'https://api.imgur.com/3/account/me/albums',
                                 headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                 verify = self.verify )
        if response.status_code != 200: return { }
        albumDatas = response.json( )[ 'data' ]
        # now for each album, get all the photos associated with this album
        def get_album_images( albumID ):
            response = requests.get( 'https://api.imgur.com/3/album/%s/images' % albumID, 
                                     headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                     verify = self.verify )
            if response.status_code != 200: return []
            return response.json( )[ 'data' ]
                                      
        return dict(map(lambda albumData: ( albumData[ 'title' ],
                                          { 'id' : albumData[ 'id' ],
                                            'images' : get_album_images( albumData[ 'id' ] ) } ),
                        albumDatas))

    def delete_candidate_album( self, candidate_album_name ):
        """
        This deletes the candidate album from the Imgur_ account. This album with that name must exist in the Imgur_ account.
        
        :param str candidate_album_name: the name of the album to remove, with its underlying images.
        
        .. seealso:: :py:meth:`refreshImages <howdy.email.email_imgur.NPRStuffIMGClient.refreshImages>`.
        """
        cand_albums = self.get_candidate_albums( )
        if cand_albums is None: return
        if candidate_album_name not in set(cand_albums): return
        main_album = self.get_main_album_name( )
        #
        ## remove all images from album
        def remove_album_images( ):
            image_ids = list( map( lambda image_elem: image_elem[ 'id' ],
                                   cand_albums[ candidate_album_name ][ 'images' ] ) )
            album_id = cand_albums[ candidate_album_name ][ 'id' ]
            response = requests.post( 'https://api.imgur.com/3/album/%s/remove_images' % album_id,
                                      headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                      data = { 'ids' : image_ids }, verify = self.verify )
            if response.status_code != 200:
                raise ValueError( "Error, problem removing images from %s." % candidate_album_name )
        
        #
        ## I identify 3 situations
        ## a) > 1 set of albums, candidate_album_name IS main album
        ## b) > 1 set of albums, candidate_album_name NOT main album
        ## c) = 1 set of albums, candidate_album_name IS main album
        album_id = cand_albums[ candidate_album_name ][ 'id' ]
        if len( cand_albums ) == 1: # main_album == candidate_album_name
            assert( main_album == candidate_album_name )
            self.albumID = None

        elif len( cand_albums ) > 1 and main_album == candidate_album_name:
            first_album_left = min( set( cand_albums ) - set([ main_album ] ) )
            self.set_main_album( first_album_left )

        remove_album_images( )
        response = requests.delete( 'https://api.imgur.com/3/album/%s' % album_id,
                                    headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                    verify = False )
        if response.status_code != 200:
            raise ValueError( "Error, could not delete album %s." % candidate_album_name )

        #
        ## put new information into database
        if self.albumID is not None:
            store_imgurl_credentials(
                self.clientID, self.clientSECRET, self.clientREFRESHTOKEN, 
                mainALBUMID = self.albumID,
                mainALBUMNAME = self.get_main_album_name( ),
                verify = self.verify )

        self.refreshImages( )
            
    def refreshImages( self ):
        """
        Refreshes the collection of images in the main Imgur_ album, by filling out ``self.imghashes``. The pictures in an album in our Imgur_ account are expected to be filled through methods in this object.

        * The key is the MD5_ hash of the image in that library.
    
        * The value is a four element :py:class:`tuple`: image name, image ID, the URL link to this image, and the :py:class:`datetime <datetime.datetime>` at which the image was uploaded.
        """
        time0 = time.time( )
        self.imghashes = { }
        if self.albumID is None: return
        response = requests.get(
            'https://api.imgur.com/3/album/%s/images' % self.albumID,
            headers = { 'Authorization' : 'Bearer %s' % self.access_token },
            verify = self.verify )
        if response.status_code != 200:
            raise ValueError("ERROR, COULD NOT ACCESS ALBUM IMAGES." )
        logging.debug( 'was able to access album images, %s, in %0.3f seconds.' % (
            self.albumID, time.time( ) - time0 ) )
        all_imgs = response.json( )[ 'data' ]
        for imgurl_img in all_imgs:
            imgMD5 = imgurl_img[ 'name' ]
            imgID = imgurl_img[ 'id' ]
            imgLINK = imgurl_img[ 'link' ]
            imgName = imgurl_img[ 'title' ]
            imgDateTime = datetime.datetime.fromtimestamp(
                imgurl_img[ 'datetime' ] )
            self.imghashes[ imgMD5 ] = [ imgName, imgID, imgLINK, imgDateTime ]
        logging.debug( 'was able to populate a dictionary of %d images in %0.3f seconds.' % (
            len( self.imghashes ), time.time( ) - time0 ) )
            
    def upload_image( self, b64img, name, imgMD5 = None ):
        """
        Uploads a Base64_ encoded file into the main Imgur_ album. If the image exists, then returns information (from ``self.imghashes``) about the file. If not, create it, put it into ``self.imghashes``, and then return its information.

        :param str b64img: the Base64_ representation of the image.
        :param str name: name of the image.
        :param str imgMD5: optional argument. This is the MD5_ hash of the image. If not provided, this is calculated for that image represented by ``b64img``.

        :returns: a 4-element :py:class:`tuple`: image name, image ID, the URL link to this image, and the :py:class:`datetime <datetime.datetime>` at which the image was uploaded.
        :rtype: tuple

        .. seealso::

           * :py:meth:`refreshImages <nprstuff.email.email_imgur.NPRStuffIMGClient.refreshImages>`.
           * :py:meth:`delete_image <nprstuff.email.email_imgur.NPRStuffIMGClient.delete_image>`.
           * :py:meth:`change_name <nprstuff.email.email_imgur.NPRStuffIMGClient.change_name>`.
        
        .. _Base64: https://en.wikipedia.org/wiki/Base64
        """
        if imgMD5 is None:
            imgMD5 = hashlib.md5( b64img ).hexdigest( )
        if imgMD5 in self.imghashes:
            return self.imghashes[ imgMD5 ]
        #
        ## upload and add to the set of images
        data = {
            'image' : b64img,
            'type' : 'base64',
            'name' : imgMD5,
            'album' : self.albumID,
            'title' : name }
        response = requests.post( 'https://api.imgur.com/3/image', data = data,
                                  headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                  verify = self.verify )
        if response.status_code != 200:
            print('ERROR, COULD NOT UPLOAD IMAGE.')
            return False
        responseData = response.json( )[ 'data' ]
        link = responseData[ 'link' ]
        imgID = responseData[ 'id' ]
        imgDateTime = datetime.datetime.fromtimestamp( responseData[ 'datetime' ] )
        self.imghashes[ imgMD5 ] = [ name, imgID, link, imgDateTime ]
        return ( name, imgID, link, imgDateTime )

    def delete_image( self, b64img, imgMD5 = None ):
        """
        Removes an image from the main Imgur_ library.

        :param str b64img: the Base64_ representation of the image.
        :param str imgMD5: optional argument. This is the MD5_ hash of the image. If not provided, this is calculated for that image represented by ``b64img``.

        :returns: ``True`` if image can be found and returned. Otherwise returns ``False``.
        :rtype: bool

        .. seealso::

           * :py:meth:`upload_image <nprstuff.email.email_imgur.NPRStuffIMGClient.upload_image>`.
           * :py:meth:`change_name <nprstuff.email.email_imgur.NPRStuffIMGClient.change_name>`.
        """
        if imgMD5 is None:
            imgMD5 = hashlib.md5( b64img ).hexdigest( )
        if imgMD5 not in self.imghashes:
            return False

        _, imgID, _, _ = self.imghashes[ imgMD5 ]
        response = requests.delete( 'https://api.imgur.com/3/image/%s' % imgID,
                                    headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                    verify = self.verify )
        self.imghashes.pop( imgMD5 )
        return True

    def change_name( self, imgMD5, new_name ):
        """
        Changes the name of an image in the main Imgur_ library.

        :param str imgMD5: this is the MD5_ hash of the image in the main Imgur_ library.
        :param str new_name: the new name to give this image.
        :returns: ``True`` if image could be found and its name changed. Otherwise returns ``False``.
        :rtype: bool

        .. seealso::

           * :py:meth:`upload_image <nprstuff.email.email_imgur.NPRStuffIMGClient.upload_image>`.
           * :py:meth:`delete_image <nprstuff.email.email_imgur.NPRStuffIMGClient.delete_image>`.
        """
        assert( os.path.basename( new_name ).endswith('.png') )
        if imgMD5 not in self.imghashes:
            return False
        _, imgID, _, _ = self.imghashes[ imgMD5 ]
        response = requests.post(  'https://api.imgur.com/3/image/%s' % imgID,
                                 headers = { 'Authorization' : 'Bearer %s' % self.access_token },
                                 data = { 'title' : os.path.basename( new_name ) }, verify = self.verify )
        if response.status_code != 200: return False
        self.imghashes[ imgMD5 ][ 0 ] = new_name
        return True

class PNGPicLabel( QLabel ):
    """
    This class that extends :py:class:`QLabel <PyQt5.QtWidgets.QLabel>` follows advice from `this StackOverflow article`_. This object also generates its own :py:class:`QPixMap <PyQT5.QtGui.QPixMap>` from the :py:class:`QImage <PyQt5.QtGui.QImage>` it keepts.

    :param img: the :py:class:`QImage <PyQt5.QtGui.QImage>` of the PNG_ image either loaded from a file or from Imgur_.
    :param parent: the parent :py:class:`QWidget <PyQt5.QtWidgets.QWidget>`, if defined, and for which *this* widget is a child.

    :var img: the source :py:class:`QImage <PyQt5.QtGui.QImage>` used to regenerate its own background :py:class:`QPixMap <PyQT5.QtGui.QPixMap>`.

    .. _`this StackOverflow article`: https://stackoverflow.com/a/30553468/3362358
    """
    def __init__( self, img, parent = None ):
        super( PNGPicLabel, self ).__init__( parent )
        self.img = img
        self.setPixmap( QPixmap.fromImage( self.img ).scaledToWidth( 450 ) )
        self.setScaledContents( True )

    def hasHeightForWidth( self ):
        return self.pixmap( ) is not None

    def heightForWidth( self, width ):
        """
        This method is slotted to one of the resize events, and is defined to fix the aspect ratio of the source :py:class:`QImage <PyQt5.QtGui.QImage>`
        
        :param int width: the width passed on a resizing event for this widget.
        """
        if self.hasHeightForWidth( ):
            return int( width * ( self.pixmap( ).height( ) / self.pixmap( ).width( ) ) )

    def resizeEvent( self, evt ):
        """
        On resize, regenerates its own background :py:class:`QPixMap <PyQT5.QtGui.QPixMap>` with the same aspect ratio as its source :py:class:`QImage <PyQt5.QtGui.QImage>`, but with the widget's new width.
        
        :param evt: the resizing :py:class:`QEvent <PyQt5.QtCore.QEvent>`.
        """
        wdth = self.size( ).width( )
        self.setPixmap( QPixmap.fromImage( self.img ).scaledToWidth( wdth ) )

class PNGPicObject( object ):
    """
    This provides a GUI widget to the Imgur_ interface implemented in :py:class:`PlexIMGClient <nprstuff.email.email_imgur.NPRStuffIMGClient>`. Initializaton of the image can either upload this image to the Imgur_ account, or retrieve the image from the main Imgur_ album. This object can also launch a GUI dialog window through :py:meth:`getInfoGUI <nprstuff.email.PNGPicObject.getInfoGUI>`.

    :param dict initdata: the low-level dictionary that contains important information on the image, located in a file, that will either be uploaded into the main Imgur_ album or merely kept in memory. The main key that determines operation is ``initialization``. It can be one of ``"FILE"`` or ``"SERVER"``.

      If ``initialization`` is ``"FILE"``, then upload the the image to the main album in the Imgur_ account. Here are the required keys in ``initdata``.

      * ``filename`` is the location of the image file on disk.
    
      * ``actName`` is the PNG filename to be used. It must end in ``png``.

      If ``initialization`` is ``"SERVER"``, then retrieve this image from the main album in the Imgur_ account. Here are the required keys in ``initdata``.

      * ``imgurlink`` is the URL link to the image.
    
      * ``imgName`` is the name of the image.

      * ``imgMD5`` is the MD5_ hash of the image.
    
      * ``imgDateTime`` is the :py:class:`datetime <datetime.datetime>` at which the image was initially uploaded into the main Imgur_ album.

    :param PlexIMGClient pImgClient: the :py:class:`PlexIMGClient <nprstuff.email.email_imgur.NPRStuffIMGClient>` used to access and manipulate (add, delete, rename) images in the main Imgur_ album.

    :var str actName: the file name without full path, which must end in ``png``.
    :var QImage img: the :py:class:`QImage <PyQt4.QtGui.QImage>` representation of this image.
    :var Image originalImage: the :py:class:`Image <PIL.Image>` representation of this image.
    :var float originalWidth: the inferred width in cm.
    :var float currentWidth: the current image width in cm. It starts off as equal to ``originalWidth``
    :var str b64string: the Base64_ encoded representation of this image as a PNG file.
    :var str imgurlLink: the URL link to the image.
    :var datetime imgDateTime: the :py:class:`datetime <datetime.datetime>` at which this image was first uploaded to the main album in the Imgur_ account.

    :raise ValueError: if ``initdata['initialization']`` is neither ``"FILE"`` nor ``"SERVER"``.
    """
    
    @classmethod
    def createPNGPicObjects( cls, pImgClient ):
        """
        :param PlexIMGClient pImgClient: the :py:class:`PlexIMGClient <nprstuff.email.email_imgur.NPRStuffIMGClient>` used to access and manipulate (add, delete, rename) images in the main Imgur_ album.
        :returns: a :py:class:`list` of :py:class:`PNGPicObject <nprstuff.email.PNGPicObject>` representing the images in the main Imgur_ album.
        :rtype: list
        """
        pngPICObjects = [ ]
        def _create_object( imgMD5 ):
            imgName, imgID, imgurlLink, imgDateTime = pImgClient.imghashes[ imgMD5 ]
            try:
                newObj = PNGPicObject( {
                    'initialization' : 'SERVER',
                    'imgurlLink' : imgurlLink,
                    'imgName' : imgName,
                    'imgMD5' : imgMD5,
                    'imgDateTime' : imgDateTime }, pImgClient )
                return newObj
            except: return None

        with multiprocessing.Pool( processes = multiprocessing.cpu_count( ) ) as pool:
            #
            ## doesn't work with multiprocessing for some reason...
            pngPICObjects = list( filter(
                None, map( _create_object, pImgClient.imghashes ) ) )
            return pngPICObjects
                
    def __init__( self, initdata, pImgClient ):
        dpi = 300.0

        if 'initialization' not in initdata or initdata['initialization'] not in ( 'FILE', 'SERVER' ):
            raise ValueError( "ERROR, initialization key must be one of 'FILE' or 'SERVER'" )
        
        # filename, actName
        if initdata[ 'initialization' ] == 'FILE':
            filename = initdata[ 'filename' ]
            actName = initdata[ 'actName' ]
            assert( os.path.isfile( filename ) )
            assert( actName.endswith('.png') )
            self.actName = os.path.basename( actName )
            self.img = QImage( filename )
            self.originalImage = Image.open( filename )
            self.originalWidth = self.originalImage.size[0] * 2.54 / dpi # current width in cm
            self.currentWidth = self.originalWidth
            #
            ## do this from http://stackoverflow.com/questions/31826335/how-to-convert-pil-image-image-object-to-base64-string
            buf = io.BytesIO( )
            self.originalImage.save( buf, format = 'PNG' )
            self.b64string = base64.b64encode( buf.getvalue( ) )
            self.imgMD5 = hashlib.md5( self.b64string ).hexdigest( )
            _, _, link, imgDateTime = pImgClient.upload_image(
                self.b64string, self.actName, imgMD5 = self.imgMD5 )
            self.imgurlLink = link
            self.imgDateTime = imgDateTime

        # imgurlLink, imgName, imgMD5, imgDatetime
        elif initdata[ 'initialization' ] == 'SERVER':
            imgurlLink = initdata[ 'imgurlLink' ]
            imgName = initdata[ 'imgName' ]
            imgMD5 = initdata[ 'imgMD5' ]
            imgDateTime = initdata[ 'imgDateTime' ]
            self.imgurlLink = imgurlLink
            self.actName = imgName
            self.imgMD5 = imgMD5
            self.imgDateTime = imgDateTime
            cnt = requests.get( self.imgurlLink, verify = False ).content
            self.originalImage = Image.open( io.BytesIO( cnt ) )
            self.img = QImage( )
            self.img.loadFromData( cnt )
            self.originalWidth = self.originalImage.size[ 0 ] * 2.54 / dpi
            self.currentWidth = self.originalWidth
            buf = io.BytesIO( )
            self.originalImage.save( buf, format = 'PNG' )
            self.b64string = base64.b64encode( buf.getvalue( ) )
        
    def getInfoGUI( self, parent ):
        """
        Launches a :py:class:`QDialog <PyQt5.QtWidgets.QDialog>` that contains the underlying image and some other labels: ``ACTNAME`` is the actual PNG file name, ``URL`` is the image's Imgur_ link, and ``UPLOADED AT`` is the date and time at which the file was uploaded. An example image is shown below,

        .. figure:: /_static/email_pngpicobject_infogui.png
           :width: 100%
           :align: left

           An example PNG_ image that can be stored in the main Imgur_ library. Note the three rows above the image: the *name* of the PNG_ image; its URL; and the date and time it was uploaded.
        
        :param parent: the parent :py:class:`QWidget <PyQt5.QtWidgets.QWidget>` that acts as the :py:class:`QDialog <PyQt5.QtWidgets.QDialog>` window's parent. Can be ``None``.
        :type parent: :py:class:`QWidget <PyQt5.QtWidgets.QWidget>`

        .. _PNG: https://en.wikipedia.org/wiki/Portable_Network_Graphics
        """
        qdl = QDialog( parent )
        qdl.setModal( True )
        myLayout = QVBoxLayout( )
        mainColor = qdl.palette().color( QPalette.Background )
        qdl.setWindowTitle( 'PNG IMAGE: %s.' % self.actName )
        qdl.setLayout( myLayout )
        myLayout.addWidget( QLabel( 'ACTNAME: %s' % self.actName ) )
        myLayout.addWidget( QLabel( 'URL: %s' % self.imgurlLink ) )
        myLayout.addWidget( QLabel(
            'UPLOADED AT: %s' %
            self.imgDateTime.strftime( '%B %d, %Y @ %I:%M:%S %p' ) ) )
        qpm = QPixmap.fromImage( self.img ).scaledToWidth( 450 )
        qlabel = PNGPicLabel( self.img, qdl )
        myLayout.addWidget( qlabel )
        qdl.resize( 1.1 * qpm.width( ), qdl.sizeHint( ).height( ) )
        result = qdl.exec_( )

    def b64String( self ):
        """
        :returns: a 3-element :py:class:`tuple` on the image incorporated into this object: its Base64_ string, its width in pixels, and the Imgur_ link.
        :rtype: tuple
        """
        #assert( self.currentWidth > 0 )
        #buffer = StringIO( )
        #reldif = abs( 2 * ( self.originalWidth - self.currentWidth ) / ( self.originalWidth + self.currentWidth ) )
        #self.originalImage.save( buffer, format = 'PNG' )
        #return base64.b64encode( buffer.getvalue( ) ), self.currentWidth, self.imgurlLink
        return self.b64string, self.currentWidth, self.imgurlLink

    def changeName( self, new_name, nImgClient ):
        """
        changes the filename into a new name.

        :param str new_name: the new name of the image file to be changed in the main album on the Imgur_ account. This must end in ``png``.
        :param NPRStuffIMGClient nImgClient: the :py:class:`NPRStuffIMGClient <nprstuff.email.email_imgur.NPRStuffIMGClient>` used to access and manipulate (add, delete, rename) images in the main Imgur_ album.
        """
        assert( new_name.endswith( '.png' ) )
        status = nImgClient.change_name( self.imgMD5, os.path.basename( new_name ) )
        if not status: return
        self.actName = os.path.basename( new_name )
