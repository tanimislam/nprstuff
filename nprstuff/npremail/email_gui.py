import glob, os, sys, textwrap, logging, time, magic, uuid
from email.utils import parseaddr, formataddr
from itertools import chain
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#
from iv_tanim.core import check_valid_RST, convert_string_RST
from nprstuff import QDialogWithPrinting
from nprstuff.npremail import (
    HtmlView, format_size, md5sum, oauthGetGoogleCredentials )
from nprstuff.npremail.email_imgur import PNGWidget
from nprstuff.npremail import npremail as nprstuff_email
#from howdy.email.email import get_all_email_contacts_dict

class AttachmentListDialog( QDialogWithPrinting ):

    class AttachmentListDelegate( QItemDelegate ):
        def __init__( self ):
            super( AttachmentListDialog.AttachmentListDelegate, self ).__init__( )

        def createEditor( self, parent, option, index ):
            return QLineEdit( parent )

        def setEditorData( self, editor, index ):
            index_unproxy = index.model( ).mapToSource( index )
            model = index.model( ).sourceModel( )
            row = index_unproxy.row( )
            column = index_unproxy.column( )
            #
            name = model.names[ row ]
            if column == 0: editor.setText( name.strip( ) )

    class AttachmentListQSortFilterModel( QSortFilterProxyModel ):
        def __init__( self, model ):
            super( AttachmentListDialog.AttachmentListQSortFilterModel, self ).__init__( )
            self.setSourceModel( model )
            model.emitFilterChanged.connect( self.invalidateFilter )

        def filterAcceptsRow( self, rowNumber, sourceParent ):
            return self.sourceModel( ).filterRow( rowNumber )

    class AttachmentListQSortFilterFileModel( QSortFilterProxyModel ):
        def __init__( self ):
            super( AttachmentListDialog.AttachmentListQSortFilterFileModel, self ).__init__( )
            model = QFileSystemModel( )
            model.setRootPath( os.getcwd( ) )
            model.setReadOnly( True )
            self.setSourceModel( model )
            self.maxSize = 15 * 1024**2 # total size of attachments = 15 MB

        def filterAcceptsRow( self, rowNumber, sourceParent ):
            model = self.sourceModel( )
            index = model.index( rowNumber, 0, sourceParent )
            if model.isDir( index ): return False
            size = model.size( index )
            return size <= self.maxSize

        def setMaxSize( self, newSize ):
            assert( newSize <= 15 * 1024**2 )
            assert( newSize >= 0 )
            self.maxSize = newSize            

    class AttachmentListTableModel( QAbstractTableModel ):
        _columnNames = [ 'NAME', 'MIMETYPE', 'SIZE' ]

        statusSignal = pyqtSignal( str )
        emitFilterChanged = pyqtSignal( )
        attachmentsSignal = pyqtSignal( dict )

        def __init__( self, parent ):
            super( AttachmentListDialog.AttachmentListTableModel, self ).__init__( )
            self.parent = parent
            self.names = [ ]
            self.mimetypes = [ ]
            self.sizes = [ ]
            self.md5s = [ ]
            self.filepaths = [ ]
            self.names_dict = { }
            self.qfilefiltermodel = AttachmentListDialog.AttachmentListQSortFilterFileModel( )
            self.qfd = QFileDialog( parent )
            self.qfd.setProxyModel( self.qfilefiltermodel )
            self.qfd.hide( )
            self.mime = magic.Magic(mime=True)
            #
            self.filterOnNames = QLineEdit( '' )
            self.filterRegExp = QRegExp( '.', Qt.CaseInsensitive, QRegExp.RegExp )
            self.filterOnNames.textChanged.connect( self.setFilterString )
            self.showingAttachmentsLabel = QLabel( '' )
            self.emitFilterChanged.connect( self.showNumberFilterAttachments )
            self.showNumberFilterAttachments( )

        def columnCount( self, parent ):
            return len( self._columnNames )

        def rowCount( self, parent ):
            return len( self.names )

        def headerData( self, col, orientation, role ):
            if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return self._columnNames[ col ]

        def flags( self, index ):
            col = index.column( )
            if col == 0:
                return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
            else:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable

        def data( self, index, role ):
            if not index.isValid( ): return None
            row = index.row( )
            col = index.column( )
            name = self.names[ row ]
            if role != Qt.DisplayRole: return
            #
            if col == 0: return self.names[ row ]
            if col == 1: return self.mimetypes[ row ]
            if col == 2: return format_size( self.sizes[ row ] )

        def getInfoOnAttachment( self, currentRow ):
            assert( currentRow >= 0 )
            assert( currentRow < len( self.names ) )
            qdl = QDialog( self.parent )
            qdl.setModal( True )
            myLayout = QVBoxLayout( )
            mainColor = qdl.palette( ).color( QPalette.Background )
            qdl.setWindowTitle( 'ATTACHMENT INFO: %s.' % self.names[ currentRow ] )
            qdl.setLayout( myLayout )
            qte = QTextEdit( qdl )
            qte.setReadOnly( True )
            qte.setPlainText('\n'.join([
                'NAME: %s.' % self.names[ currentRow ],
                'FULL PATH: %s.' % self.filepaths[ currentRow ],
                'SIZE: %s.' % format_size( self.sizes[ currentRow ] ),
                'MD5: %s.' % self.md5s[ currentRow ] ] ) )
            myLayout.addWidget( qte )
            qdl.setFixedWidth( 450 )
            qdl.setFixedHeight( qdl.sizeHint( ).height( ) )
            result = qdl.exec_( )            

        def addFile( self ):
            fname, _ = self.qfd.getOpenFileName(
                self.parent, 'Choose Attachment', os.getcwd( ) )
            if not os.path.abspath( fname ): return
            if len( os.path.basename( fname ) ) == 0: return
            #
            ## now try to add the file
            #
            ## first check the MD5
            md5 = md5sum( os.path.abspath( fname ) )
            if md5 in self.md5s:
                self.statusSignal.emit( 'ATTACHMENT ALREADY INCLUDED.' )
                return
            #
            ## second, check to see if adding this file will keep us from adding it to here
            size_rem = 15 * 1024**2 - sum( self.sizes )
            size = os.path.getsize( os.path.abspath( fname ) )
            if size > size_rem:
                self.statusSignal.emit( 'ATTACHMENT TOO BIG, WOULD EXCEED 15 MB.' )
                return
            #
            ## third, check the name, then add
            self.layoutAboutToBeChanged.emit( )
            name = os.path.basename( fname )
            if name in self.names:
                prefixpart = '.'.join( name.split('.')[:-1] )
                suffix = name.split('.')[-1]
                rando = str( uuid.uuid4( ) )[:5]
                name = '%s %s.%s' % ( prefixpart, rando, suffix )
            #
            ## fourth, get the mimetype
            mimetype = self.mime.from_file( os.path.abspath( fname ) )
            #
            ## fifth, add this entry to the list and adjust maximum size
            self.names.append( name )
            self.md5s.append( md5 )
            self.mimetypes.append( mimetype )
            self.filepaths.append( os.path.abspath( fname ) )
            self.sizes.append( size )
            self.qfilefiltermodel.setMaxSize( 15 * 1024**2 - sum( self.sizes ) )
            #
            attachmentList = list(map(lambda idx: {
                'name' : self.names[ idx ],
                'mimetype' : self.mimetypes[ idx ],
                'filepath' : self.filepaths[ idx ] }, range(len( self.names ) ) ) )
            self.attachmentsSignal.emit({
                'attachments' : attachmentList })
            self.layoutChanged.emit( )
            self.emitFilterChanged.emit( )
            self.statusSignal.emit( '' )

        def removeFileAtRow( self, row ):
            assert( row >= 0 and row < len( self.names ) )
            self.layoutAboutToBeChanged.emit( )
            self.names.pop( row )
            self.md5s.pop( row )
            self.mimetypes.pop( row )
            self.filepaths.pop( row )
            self.sizes.pop( row )
            self.qfilefiltermodel.setMaxSize( 15 * 1024**2 - sum( self.sizes ) )
            #
            attachmentList = list(map(lambda idx: {
                'name' : self.names[ idx ],
                'mimetype' : self.mimetypes[ idx ],
                'filepath' : self.filepaths[ idx ] }, range(len( self.names ) ) ) )
            self.attachmentsSignal.emit({
                'attachments' : attachmentList })
            self.layoutChanged.emit( )
            self.emitFilterChanged.emit( )

        def setData( self, index, val, role ):
            if not index.isValid( ): return False
            if role != Qt.EditRole: return False
            #
            row = index.row( )
            col = index.column( )
            if col != 0: return False
            currentName = self.names[ row ]
            if len( val.strip( ) ) == 0: return False
            if val.strip( ) in self.names: return False
            self.names[ row ] = val.strip( )
            #
            attachmentList = list(map(lambda idx: {
                'name' : self.names[ idx ],
                'mimetype' : self.mimetypes[ idx ],
                'filepath' : self.filepaths[ idx ] }, range(len( self.names ) ) ) )
            self.attachmentsSignal.emit({
                'attachments' : attachmentList })
            self.emitFilterChanged.emit( )
            return True

        def filterRow( self, rowNumber ):
            assert( rowNumber >= 0 )
            assert( rowNumber < len( self.names ) )
            name = self.names[ rowNumber ]
            return self.filterRegExp.indexIn( name ) != -1

        def showNumberFilterAttachments( self ):
            num_attachs = len(list(filter(self.filterRow, range(len(self.names)))))
            self.showingAttachmentsLabel.setText( 'SHOWING %d ATTACHMENTS' % num_attachs )

        def setFilterString( self, newString ):
            mytext = newString.strip( )
            if len( mytext ) == 0: mytext = '.'
            self.filterRegExp = QRegExp( mytext, Qt.CaseInsensitive, QRegExp.RegExp )
            self.emitFilterChanged.emit( )

    class AttachmentListTableView( QTableView ):
        def __init__( self, attachmentListTableModel ):
            super( AttachmentListDialog.AttachmentListTableView, self ).__init__( )
            self.setModel( AttachmentListDialog.AttachmentListQSortFilterModel(
                attachmentListTableModel ) )
            self.setItemDelegateForColumn(
                0, AttachmentListDialog.AttachmentListDelegate( ) )
            self.menu = self.createContextMenuEvent( attachmentListTableModel )
            #
            self.setShowGrid( True )
            self.verticalHeader( ).setSectionResizeMode( QHeaderView.Fixed )
            self.horizontalHeader( ).setSectionResizeMode( QHeaderView.Fixed )
            self.setSelectionBehavior( QAbstractItemView.SelectRows )
            self.setSelectionMode( QAbstractItemView.SingleSelection )
            #
            self.setColumnWidth( 0, 180 )
            self.setColumnWidth( 1, 180 )
            self.setColumnWidth( 2, 180 )
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
            #
            addAction = QAction( self )
            addAction.setShortcut( 'Ctrl+A' )
            addAction.triggered.connect( attachmentListTableModel.addFile )
            self.addAction( addAction )

        def createContextMenuEvent( self, model ):
            menu = QMenu( self )
            addAction = QAction( 'ADD FILE', menu )
            addAction.setShortcut( 'Ctrl+A' )
            addAction.triggered.connect( model.addFile )
            menu.addAction( addAction )
            #
            def infoFile( ):
                row = self.getValidIndexAtRow( )
                if row == -1: return
                model.getInfoOnAttachment( row )
            infoAction = QAction( 'INFO', menu )
            infoAction.triggered.connect( infoFile )
            menu.addAction( infoAction )
            def removeFile( ):
                row = self.getValidIndexAtRow( )
                if row == -1: return
                model.removeFileAtRow( row )
            removeAction = QAction( 'REMOVE FILE', menu )
            removeAction.triggered.connect( removeFile )
            menu.addAction( removeAction )
            return menu

        def contextMenuEvent( self, evt ):
            self.menu.popup( QCursor.pos( ) )

        def getValidIndexAtRow( self ):
            try:
                index_valid_proxy = max(
                    filter(
                        lambda index: index.column( ) == 0,
                        self.selectionModel( ).selectedIndexes( ) ) )
                index_valid = self.model( ).mapToSource( index_valid_proxy )
                return index_valid.row( )
            except: return -1

        def resizeTableColumns( self, newsize ):
            width = newsize.width( )
            self.setColumnWidth( 0, int( 0.6 * width ) )
            self.setColumnWidth( 1, int( 0.2 * width ) )
            self.setColumnWidth( 2, int( 0.2 * width ) )

    def __init__( self, parent ):
        super( AttachmentListDialog, self ).__init__( parent, doQuit = False, isIsolated = False )
        time0 = time.time( )
        self.setWindowTitle( 'ATTACHMENTS' )
        #
        self.attachmentListTableModel = AttachmentListDialog.AttachmentListTableModel( self )
        attachmentListTableView = AttachmentListDialog.AttachmentListTableView( self.attachmentListTableModel )
        statusLabel = QLabel( '' )
        #
        hideAction = QAction( self )
        hideAction.setShortcut( 'Ctrl+W' )
        hideAction.triggered.connect( self.hide )
        self.addAction( hideAction )
        #
        myLayout = QVBoxLayout( )
        self.setLayout( myLayout )
        #
        topWidget = QWidget( )
        topLayout = QHBoxLayout( )
        topWidget.setLayout( topLayout )
        topLayout.addWidget( QLabel( 'FILTER' ) )
        topLayout.addWidget( self.attachmentListTableModel.filterOnNames )
        myLayout.addWidget( topWidget )
        #
        myLayout.addWidget( attachmentListTableView )
        #
        botWidget = QWidget( )
        botLayout = QHBoxLayout( )
        botWidget.setLayout( botLayout )
        botLayout.addWidget( self.attachmentListTableModel.showingAttachmentsLabel )
        botLayout.addWidget( statusLabel )
        myLayout.addWidget( botWidget )
        #
        self.attachmentListTableModel.statusSignal.connect( statusLabel.setText )
        #
        self.setFixedWidth( 600 )
        self.setFixedHeight( 600 )
        attachmentListTableView.resizeTableColumns( self.size( ) )
        self.hide( )
        logging.info( 'initialized AttachmentListDialog in %0.3f seconds.' % (
            time.time( ) - time0 ) )
                
class EmailListDialog( QDialogWithPrinting ):
    
    class EmailListDelegate( QItemDelegate ):
        def __init__( self, parent ):
            super( EmailListDialog.EmailListDelegate, self ).__init__( )
            self.emailCompleter = parent.emailCompleter
            self.nameCompleter = parent.nameCompleter

        def createEditor( self, parent, option, index ):
            lineedit = QLineEdit( parent )
            if index.column( ) == 0:
                lineedit.setCompleter( self.emailCompleter )
            elif index.column( ) == 1:
                lineedit.setCompleter( self.nameCompleter )
            return lineedit

        def setEditorData( self, editor, index ):
            index_unproxy = index.model( ).mapToSource( index )
            model = index.model( ).sourceModel( )
            row = index_unproxy.row( )
            column = index_unproxy.column( )
            emailC = model.emails[ row ]
            name = model.names[ row ]
            if column == 0:
                editor.setText( emailC.strip( ) )
            elif column == 1:
                editor.setText( name.strip( ) )

    class EmailListQSortFilterModel( QSortFilterProxyModel ):
        def __init__( self, model ):
            super( EmailListDialog.EmailListQSortFilterModel, self ).__init__( )
            self.setSourceModel( model )
            model.emitFilterChanged.connect( self.invalidateFilter )

        def filterAcceptsRow( self, rowNumber, sourceParent ):
            return self.sourceModel( ).filterRow( rowNumber )
    
    class EmailListTableModel( QAbstractTableModel ):
        _columnNames = [ 'EMAIL', 'NAME' ]

        statusSignal = pyqtSignal( str )
        emitFilterChanged = pyqtSignal( )
        changedEmailSignal = pyqtSignal( dict )
        
        def __init__( self, parent ):
            super( EmailListDialog.EmailListTableModel, self ).__init__( parent )
            self.parent = parent
            self.emails = [ ]
            self.names = [ ]
            self.key = parent.key
            #
            self.filterOnNamesOrEmails = QLineEdit( '' )
            self.filterRegExp = QRegExp( '.', Qt.CaseInsensitive, QRegExp.RegExp )
            self.filterOnNamesOrEmails.textChanged.connect( self.setFilterString )
            self.showingEmailsLabel = QLabel( '' )
            self.emitFilterChanged.connect( self.showNumberFilterEmails )
            self.showNumberFilterEmails( )

        def columnCount( self, parent ):
            return 2

        def rowCount( self, parent ):
            return len( self.emails )

        def headerData( self, col, orientation, role ):
            if orientation == Qt.Horizontal and role == Qt.DisplayRole:
                return self._columnNames[ col ]

        def flags(self, index):
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

        def data( self, index, role ):
            if not index.isValid( ): return None
            row = index.row( )
            col = index.column( )
            email = self.emails[ row ]
            name = self.names[ row ]
            if role != Qt.DisplayRole: return
            #
            if col == 0: return email
            if col == 1: return name

        def addEmail( self, input_tuple ):
            name, emailCurrent = input_tuple
            emails_lower = set(map(lambda emailC: emailC.lower( ), self.emails) )
            names_lower = set(map(lambda name: name.lower( ), self.names ) ) - set([''])
            if emailCurrent.lower( ) in emails_lower:
                self.statusSignal.emit( 'EMAIL ALREADY IN PLACE.' )
                return
            if name.lower( ) != '':
                if name.lower( ) in names_lower:
                    self.statusSignal.emit('NAME ALREADY IN PLACE.' )
                    return
            #
            ## now add the email and name
            self.layoutAboutToBeChanged.emit( )
            self.emails.append( emailCurrent )
            self.names.append( name )
            self.changedEmailSignal.emit({
                'key' : self.key,
                'names and emails' : sorted(
                map(formataddr, zip( self.names, self.emails ) ) ) } )
            self.layoutChanged.emit( )
            self.emitFilterChanged.emit( )
            self.sort( 1, Qt.AscendingOrder )

        def sort( self, ncol, order ):
            if len( self.emails ) == 0: return
            self.layoutAboutToBeChanged.emit( )
            email_names_list = sorted(zip(self.emails, self.names), key = lambda tup: tup[1] )
            self.emails = list( list(zip(*email_names_list))[0] )
            self.names = list( list(zip(*email_names_list))[1] )
            self.layoutChanged.emit( )

        def removeEmailAtRow( self, row ):
            assert( row >= 0 and row < len( self.emails ) )
            self.layoutAboutToBeChanged.emit( )
            self.emails.pop( row )
            self.names.pop( row )
            self.parent.allData[ self.key ] = sorted(
                map(formataddr, zip( self.names, self.emails ) ) )
            self.layoutChanged.emit( )
            self.emitFilterChanged.emit( )
            self.sort( 1, Qt.AscendingOrder )

        def setData( self, index, val, role ):
            if not index.isValid( ): return False
            if role != Qt.EditRole: return False
            #
            row = index.row( )
            col = index.column( )
            currentEmail = self.emails[ row ]
            currentName = self.names[ row ]
            if col == 0: # check and change email
                emails_rem = set(map(lambda emailC: emailC.lower( ), self.emails ) ) - set([ currentEmail.lower() ])
                _, checkEmail = parseaddr( val.strip( ) )
                if checkEmail == '': return False
                if checkEmail.lower( ) in emails_rem: return False
                self.emails[ row ] = checkEmail
            elif col == 1: # check and change name
                names_rem =  set(map(lambda name: name.lower( ), self.names ) ) - set([ currentName.lower(), '' ])
                if val.strip( ).lower( ) in names_rem: return False
                self.names[ row ] = val.strip( )
            #
            self.parent.allData[ self.key ] = sorted(
                map(formataddr, zip( self.names, self.emails ) ) )
            self.sort( 1, Qt.AscendingOrder )
            self.emitFilterChanged.emit( )
            return True
        
        def filterRow( self, rowNumber ):
            assert( rowNumber >= 0 )
            assert( rowNumber < len( self.emails ) )
            name = self.names[ rowNumber ]
            email = self.emails[ rowNumber ]
            #
            ## if not one of selected emails and ONLY show selected emails...
            if self.filterRegExp.indexIn( name ) != -1: return True
            if self.filterRegExp.indexIn( email ) != -1: return True
            return False

        def showNumberFilterEmails( self ):
            num_emails = len(list(filter(self.filterRow, range(len(self.emails)))))
            self.showingEmailsLabel.setText('SHOWING %d EMAILS' % num_emails )

        def setFilterString( self, newString ):
            mytext = newString.strip( )
            if len( mytext ) == 0: mytext = '.'
            self.filterRegExp = QRegExp( mytext, Qt.CaseInsensitive, QRegExp.RegExp )
            self.emitFilterChanged.emit( )

        def createCopyTextEmails( self ):
            allText = '\n'.join(
                map(lambda formaddr: '.. %s: %s' % ( self.key.upper( ), formaddr ),
                    sorted( self.parent.allData[ self.key ] ) ) )
            clipboard = QApplication.clipboard( )
            clipboard.setText( allText )
            
    class EmailListTableView( QTableView ):
        def __init__( self, parent ):
            super( EmailListDialog.EmailListTableView, self ).__init__( )
            self.parent = parent
            self.setModel( EmailListDialog.EmailListQSortFilterModel(
                parent.emailListTableModel ) )
            self.setItemDelegate( EmailListDialog.EmailListDelegate( parent ) )
            #
            self.setShowGrid( True )
            self.verticalHeader( ).setSectionResizeMode( QHeaderView.Fixed )
            self.horizontalHeader( ).setSectionResizeMode( QHeaderView.Fixed )
            self.setSelectionBehavior( QAbstractItemView.SelectRows )
            self.setSelectionMode( QAbstractItemView.SingleSelection )
            self.setSortingEnabled( True )
            #
            self.setColumnWidth( 0, 180 )
            self.setColumnWidth( 1, 180 )
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
            #
            addAction = QAction( self )
            addAction.setShortcut( 'Ctrl+A' )
            addAction.triggered.connect( self.parent.emailListAddEmailName.show )
            self.addAction( addAction )

        def contextMenuEvent( self, evt ):
            menu = QMenu( self )
            addAction = QAction( 'ADD EMAIL', menu )
            addAction.setShortcut( 'Ctrl+A' )
            addAction.triggered.connect( self.parent.emailListAddEmailName.show )
            menu.addAction( addAction )
            if len( self.parent.emailListTableModel.emails ) != 0:
                def removeEmail( ):
                    self.parent.emailListTableModel.removeEmailAtRow(
                        self.getValidIndexRow( ) )
                removeAction = QAction( 'REMOVE EMAIL', menu )
                removeAction.triggered.connect( removeEmail )
                menu.addAction( removeAction )
                #
                copyEmailsAction = QAction( 'COPY %s EMAILS' % self.parent.emailListTableModel.key.upper( ), menu )
                copyEmailsAction.triggered.connect( self.parent.emailListTableModel.createCopyTextEmails )
                menu.addAction( copyEmailsAction )
            menu.popup( QCursor.pos( ) )

        def getValidIndexRow( self ):
            index_valid_proxy = max(
                filter(
                    lambda index: index.column( ) == 0,
                    self.selectionModel( ).selectedIndexes( ) ) )
            index_valid = self.model( ).mapToSource( index_valid_proxy )
            return index_valid.row( )

        def resizeTableColumns( self, newsize ):
            width = newsize.width( )
            self.setColumnWidth( 0, int( 0.5 * width ) )
            self.setColumnWidth( 1, int( 0.5 * width ) )
    
    class EmailListAddEmailName( QDialogWithPrinting ):

        statusSignal = pyqtSignal( tuple )
        
        def __init__( self, parent ):
            super( EmailListDialog.EmailListAddEmailName, self ).__init__(
                parent, doQuit = False, isIsolated = False )
            self.setWindowTitle( 'EMAIL AND NAME TO ADD' )
            self.emailLineEdit = QLineEdit( '' )
            self.nameLineEdit = QLineEdit( '' )
            self.parent = parent
            #
            myLayout = QGridLayout( )
            self.setLayout( myLayout )
            myLayout.addWidget( QLabel( 'EMAIL:' ), 0, 0, 1, 1 )
            myLayout.addWidget( self.emailLineEdit, 0, 1, 1, 3 )
            myLayout.addWidget( QLabel( 'NAME:' ), 1, 0, 1, 1 )
            myLayout.addWidget( self.nameLineEdit, 1, 1, 1, 3 )
            myLayout.addWidget( QLabel( 'PRESS SHIFT+CTRL+A TO ADD EMAIL + NAME.' ), 2, 0, 1, 4 )
            #
            self.emailLineEdit.returnPressed.connect( self.checkValidEmail )
            self.nameLineEdit.returnPressed.connect( self.checkValidName )
            self.emailLineEdit.setCompleter( parent.emailCompleter )
            self.nameLineEdit.setCompleter( parent.nameCompleter )
            addAction = QAction( self )
            addAction.setShortcut( 'Shift+Ctrl+A' )
            addAction.triggered.connect( self.addEmail )
            self.addAction( addAction )
            #
            self.setFixedWidth( 300 )
            self.hide( )

        def checkValidEmail( self, replaceName = True ):
            _, checkEmail = parseaddr( self.emailLineEdit.text( ) )
            if checkEmail == '':
                self.emailLineEdit.setText( '' )
                return False
            self.emailLineEdit.setText( checkEmail )
            if not replaceName: return True
            if self.parent.get_name_for_email( checkEmail ) is None: return True
            #
            checkName = self.parent.get_name_for_email( checkEmail )
            self.nameLineEdit.setText( checkName )
            return True

        def checkValidName( self, replaceEmail = True ):
            checkName = self.nameLineEdit.text( ).strip( )
            self.nameLineEdit.setText( checkName )
            if not replaceEmail: return True
            if len( self.parent.get_emails_for_name( checkName ) ) != 1: return True
            #
            checkEmail = max( self.parent.get_emails_for_name( checkName ) )
            self.emailLineEdit.setText( checkEmail )
            return True

        def addEmail( self ):
            checkEmail = ''
            if self.checkValidEmail( replaceName = False ):
                _, checkEmail = parseaddr( self.emailLineEdit.text( ) )
            self.checkValidName( )
            checkName = self.nameLineEdit.text( ).strip( )
            self.statusSignal.emit(( checkName, checkEmail ))
            self.hide( )
            self.emailLineEdit.setText( '' )
            self.nameLineEdit.setText( '' )
            
    
    def __init__( self, parent, key = 'to' ):
        super( EmailListDialog, self ).__init__( parent, doQuit = False, isIsolated = False )
        time0 = time.time( )
        assert( key in ( 'to', 'cc', 'bcc' ) )
        assert( key in parent.allData )
        self.key = key
        self.allData = parent.allData
        self.setWindowTitle( 'EMAIL %s' % key.upper( ) )
        #
        self.all_emails = sorted( parent.allData[ 'emails dict rev' ] )
        self.all_names = sorted( parent.allData[ 'emails dict' ] )
        self.emailCompleter = QCompleter( self.all_emails )
        self.nameCompleter = QCompleter( self.all_names )
        self.emailListAddEmailName = EmailListDialog.EmailListAddEmailName( self )
        self.emailListTableModel = EmailListDialog.EmailListTableModel( self )
        emailListTableView = EmailListDialog.EmailListTableView( self )
        #
        self.emailListAddEmailName.statusSignal.connect(
            self.emailListTableModel.addEmail )
        hideAction = QAction( self )
        hideAction.setShortcut( 'Ctrl+W' )
        hideAction.triggered.connect( self.hide )
        self.addAction( hideAction )
        #
        myLayout = QVBoxLayout( )
        self.setLayout( myLayout )
        #
        topWidget = QWidget( )
        topLayout = QHBoxLayout( )
        topWidget.setLayout( topLayout )
        topLayout.addWidget( QLabel( 'FILTER' ) )
        topLayout.addWidget( self.emailListTableModel.filterOnNamesOrEmails )
        myLayout.addWidget( topWidget)
        #
        myLayout.addWidget( emailListTableView )
        #
        myLayout.addWidget( self.emailListTableModel.showingEmailsLabel )
        #
        self.setFixedWidth( 600 )
        self.setFixedHeight( 600 )
        emailListTableView.resizeTableColumns( self.size( ) )
        self.hide( )
        logging.info( 'initialized %s EmailListDialog in %0.3f seconds.' % (
            self.key, time.time( ) - time0 ) )

    def get_emails_for_name( self, name ):
        if name not in self.all_names: return [ ]
        return sorted( set(
            self.allData[ 'emails dict' ][ name ] ) )

    def get_name_for_email( self, email ):
        if email not in self.all_emails: return None
        return self.allData[ 'emails dict rev' ][ email ]

class FromDialog( QDialogWithPrinting ):

    emailAndNameChangedSignal = pyqtSignal( str )
    changedDataSignal = pyqtSignal( dict )
    
    class EmailListModel( QAbstractListModel ):
        def __init__( self, emails ):
            super( FromDialog.EmailListModel, self ).__init__( None )
            self.emails = [ ]
            self.changeData( emails )

        def rowCount( self, parent ):
            return len( self.emails )

        def data( self, index, role ):
            if not index.isValid( ): return None
            row = index.row( )
            return self.emails[ row ]

        def changeData( self, new_emails ):
            self.beginResetModel( )
            self.emails = sorted( set( new_emails ) )
            self.endResetModel( )

    class NameListModel( QAbstractListModel ):
        def __init__( self, names ):
            super( FromDialog.NameListModel, self ).__init__( None )
            self.beginResetModel( )
            self.names = sorted( set( names ) )
            self.endResetModel( )

        def rowCount( self, parent ):
            return len( self.names )

        def data( self, index, role ):
            if not index.isValid( ): return None
            row = index.row( )
            return self.names[ row ]
    
    def __init__( self, parent ):
        super( FromDialog, self ).__init__( parent, doQuit = False, isIsolated = False )
        self.setWindowTitle( 'SENDING EMAIL' )
        assert( 'from name' in parent.allData )
        assert( 'from email' in parent.allData )
        #
        self.parent = parent
        self.emailLineEdit = QLineEdit( '' )
        self.nameLineEdit = QLineEdit( '' )
        self.emailListModel = FromDialog.EmailListModel( sorted( parent.allData[ 'emails dict rev' ] ) )
        self.nameListModel = FromDialog.NameListModel( sorted( parent.allData[ 'emails dict' ] ) )
        #
        myLayout = QGridLayout( )
        self.setLayout( myLayout )
        myLayout.addWidget( QLabel( 'EMAIL:' ), 0, 0, 1, 1 )
        myLayout.addWidget( self.emailLineEdit, 0, 1, 1, 3 )
        myLayout.addWidget( QLabel( 'NAME:' ), 1, 0, 1, 1 )
        myLayout.addWidget( self.nameLineEdit, 1, 1, 1, 3 )
        #
        self.emailLineEdit.setCompleter( QCompleter( sorted( parent.allData[ 'emails dict rev' ] ) ) )
        self.nameLineEdit.setCompleter( QCompleter( sorted( parent.allData[ 'emails dict' ] ) ) )
        self.emailLineEdit.returnPressed.connect( self.setValidEmail )
        self.nameLineEdit.returnPressed.connect( self.setValidName )
        hideAction = QAction( self )
        hideAction.setShortcut( 'Ctrl+W' )
        hideAction.triggered.connect( self.actuallyCloseHide )
        self.addAction( hideAction )
        #
        self.setFixedWidth( 300 )
        self.hide( )

    def setCompleters( self, allData ):
        assert( len(
            set([ 'emails dict', 'emails dict rev' ] ) - set( allData ) ) == 0 )
        #emailC = QCompleter( self )
        #emailC.setPopup( QListView( self ) )
        #emailC.setModel( self.emailListModel )
        #emailC.setCompletionMode( QCompleter.PopupCompletion )
        #emailC.setMaxVisibleItems( 7 )
        #self.emailLineEdit.setCompleter( emailC )
        self.emailLineEdit.setCompleter( QCompleter( sorted( allData[ 'emails dict rev' ] ) ) )
        #
        #nameC = QCompleter( self )
        #nameC.setModel( self.nameListModel )
        #nameC.setCompletionMode( QCompleter.PopupCompletion )
        #nameC.setMaxVisibleItems( 7 )
        #self.nameLineEdit.setCompleter( nameC )
        self.nameLineEdit.setCompleter( QCompleter( sorted( allData[ 'emails dict' ] ) ) )

    def closeEvent( self, evt ):
        self.actuallyCloseHide( )

    def actuallyCloseHide( self ):
        self.hide( )
        self.setValidEmail( False )
        self.setValidName( False )
        self.emailAndNameChangedSignal.emit( self.getEmailAndName( ) )

    def setValidEmail( self, emit = True ):
        _, checkEmail = parseaddr( self.emailLineEdit.text( ) )
        if checkEmail == '':
            validEmail = self.parent.allData[ 'from email' ]
            self.emailLineEdit.setText( validEmail )
            return
        self.parent.allData[ 'from email' ] = checkEmail
        self.emailLineEdit.setText( checkEmail )
        self.changedDataSignal.emit({
            'from email' : checkEmail })
        if checkEmail in self.parent.allData[ 'emails dict rev' ]:
            checkName = self.parent.allData[ 'emails dict rev' ][ checkEmail ]
            self.parent.allData[ 'from name' ] = checkName
            self.nameLineEdit.setText( checkName )
            emails = self.parent.allData[ 'emails dict' ][ checkName ]
            #self.emailListModel.changeData( emails )
            #self.emailLineEdit.setCompleter( QCompleter( sorted( emails ) ) )
        if emit: self.emailAndNameChangedSignal.emit( self.getEmailAndName( ) )

    def setValidName( self, emit = True, setEmail = False ):
        checkName = self.nameLineEdit.text( ).strip( )
        self.parent.allData[ 'from name' ] = checkName
        self.nameLineEdit.setText( checkName )
        self.changedDataSignal.emit({
            'from name' : checkName })
        if checkName == '' or checkName not in self.parent.allData[ 'emails dict' ]:
            emails = sorted( self.parent.allData[ 'emails dict rev' ] )
            #self.emailListModel.changeData( emails )
            #self.emailLineEdit.setCompleter( QCompleter( sorted( emails ) ) )
        elif checkName in self.parent.allData[ 'emails dict' ]:
            emails = self.parent.allData[ 'emails dict' ][ checkName ]
            #self.emailListModel.changeData( emails )
            #self.emailLineEdit.setCompleter( QCompleter( sorted( emails ) ) )
        if emit: self.emailAndNameChangedSignal.emit( self.getEmailAndName( ) ) 

    def getEmailAndName( self ):
        validEmail = self.parent.allData[ 'from email' ]
        validName = self.parent.allData[ 'from name' ]
        if validEmail == '': return ''
        emailAndName = validEmail
        if validName == '': return emailAndName
        return formataddr( ( validName, validEmail ) )

class NPRStuffReSTEmailGUI( QDialogWithPrinting ):
    
    def __init__( self, verify = True, use_mathjax = False ):
        super( NPRStuffReSTEmailGUI, self ).__init__( None, doQuit = True, isIsolated = True )
        self.setWindowTitle( 'RESTRUCTUREDTEXT EMAIL SENDER' )
        self.setStyleSheet("""
        QWidget {
        font-family: Consolas;
        font-size: 11;
        }""" )
        #
        qf = QFont( )
        qf.setFamily( 'Consolas' )
        qf.setPointSize( 11 )
        qfm = QFontMetrics( qf )
        self.allData = {
            'from email' : '',
            'from name' : '',
            'to' : [ ],
            'cc' : [ ],
            'bcc' : [ ],
            'attachments' : [ ] }
        time0 = time.time( )
        self.use_mathjax = use_mathjax
        credentials = oauthGetGoogleCredentials( verify = verify )
        self.email_service = nprstuff_email.get_email_service(
            verify = verify, credentials = credentials )
        self.people_service = nprstuff_email.get_people_service(
            verify = verify, credentials = credentials )
        self.allData[ 'emails dict' ] = nprstuff_email.get_all_email_contacts_dict(
            people_service = self.people_service, pagesize = 2000 )
        if len( self.allData[ 'emails dict' ] ) == 0:
            raise ValueError("Error, could find no Google contacts! Exiting..." )
        emails_dict_rev = dict(chain.from_iterable(
            map(lambda name: map(lambda email: ( email, name ),
                                 self.allData[ 'emails dict' ][ name ] ),
                self.allData[ 'emails dict' ] ) ) )
        self.allData[ 'emails dict rev' ] = emails_dict_rev
        logging.info( 'took %0.3f seconds to find all %d Google contacts.' % (
            time.time( ) - time0, len( self.allData[ 'emails dict' ] ) ) )
        #
        self.statusLabel = QLabel( )
        self.rowColLabel = QLabel( )
        self.textOutput = QPlainTextEdit( )
        self.textOutput.setTabStopWidth( 2 * qfm.width( 'A' ) )
        #
        self.fromDialog = FromDialog( self )
        self.toEmailListDialog = EmailListDialog( self, key = 'to' )
        self.ccEmailListDialog = EmailListDialog( self, key = 'cc' )
        self.bccEmailListDialog = EmailListDialog( self, key = 'bcc' )
        self.attachmentListDialog = AttachmentListDialog( self )
        #
        self.fromButton = QPushButton( 'FROM' )
        self.toButton = QPushButton( 'TO' )
        #
        self.convertButton = QPushButton( 'CONVERT' )
        self.sendButton = QPushButton( 'SEND' )
        #
        self.fromLabel = QLabel( '' )
        self.subjLineEdit = QLineEdit( '' )
        #
        logging.info('just about to initialze PNGWidget in %0.3f seconds.' % (
            time.time( ) - time0 ) )
        self.pngWidget = PNGWidget( self )
        self.pngWidget.hide( )
        logging.info( 'initialized all interactive widgets in %0.3f seconds.' % (
            time.time( ) - time0 ) )
        #
        myLayout = QVBoxLayout( )
        self.setLayout( myLayout )
        #
        ## top widget
        ## email buttons
        topWidget = QWidget( )
        topLayout = QGridLayout( )
        topWidget.setLayout( topLayout )
        topLayout.addWidget( self.fromButton, 0, 0, 1, 3 )
        topLayout.addWidget( self.toButton, 0, 3, 1, 3 )
        #
        ## editing buttons
        topLayout.addWidget( self.convertButton, 1, 0, 1, 3 )
        topLayout.addWidget( self.sendButton, 1, 3, 1, 3 )
        #
        ## email subject and from widgets
        topLayout.addWidget( QLabel( 'FROM:' ), 2, 0, 1, 1 )
        topLayout.addWidget( self.fromLabel, 2, 1, 1, 5 )
        topLayout.addWidget( QLabel( 'SUBJECT:' ), 3, 0, 1, 1 )
        topLayout.addWidget( self.subjLineEdit, 3, 1, 1, 5 )
        myLayout.addWidget( topWidget )
        #
        ## middle widget, reStructuredText output
        myLayout.addWidget( self.textOutput )
        #
        ## bottom widget
        botWidget = QWidget( )
        botLayout = QHBoxLayout( )
        botWidget.setLayout( botLayout )
        botLayout.addWidget( self.rowColLabel )
        botLayout.addWidget( self.statusLabel )
        myLayout.addWidget( botWidget )
        #
        self.fromButton.clicked.connect( self.fromDialog.show )
        self.toButton.clicked.connect( self.toEmailListDialog.show )
        self.sendButton.clicked.connect( self.sendEmail )
        self.convertButton.clicked.connect( self.printHTML )
        #
        self.fromDialog.emailAndNameChangedSignal.connect(
            self.fromLabel.setText )
        #
        ## save reStructuredText file
        saveAction = QAction( self )
        saveAction.setShortcut( 'Ctrl+S' )
        saveAction.triggered.connect( self.saveFileName )
        self.addAction( saveAction )
        #
        ## load reStructuredText file
        openAction = QAction( self )
        openAction.setShortcut( 'Ctrl+O' )
        openAction.triggered.connect( self.loadFileName )
        self.addAction( openAction )
        #
        ## interactivity -- show row and column of text cursor in editor, and once press enter strip subject string
        self.textOutput.cursorPositionChanged.connect( self.showRowCol )
        self.subjLineEdit.returnPressed.connect( self.fixSubject )
        #
        ## change to/cc/bcc/attachments data
        self.toEmailListDialog.emailListTableModel.changedEmailSignal.connect( self.changeEmailData )
        self.ccEmailListDialog.emailListTableModel.changedEmailSignal.connect( self.changeEmailData )
        self.bccEmailListDialog.emailListTableModel.changedEmailSignal.connect( self.changeEmailData )
        self.attachmentListDialog.attachmentListTableModel.attachmentsSignal.connect( self.changeAttachmentsData )
        #
        ## make popup menu
        self.popupMenu = self._makePopupMenu( )
        #
        ## geometry stuff and final initialization
        logging.debug( 'WAS ABLE TO INITIALIZE EVERYTHING IN %0.3f SECONDS.' % (
            time.time( ) - time0 ) )
        self.setFixedHeight( 700 )
        self.setFixedWidth( 600 )
        self.show( )

    def _makePopupMenu( self ):
        menu = QMenu( self )
        #
        menu.addSection( 'SENDING ACTIONS' )
        ccAction = QAction( 'CC', menu )
        ccAction.triggered.connect( self.ccEmailListDialog.show )
        menu.addAction( ccAction )
        bccAction= QAction( 'BCC', menu )
        bccAction.triggered.connect( self.bccEmailListDialog.show )
        menu.addAction(bccAction )
        attachAction = QAction( 'ATTACH', menu )
        attachAction.triggered.connect( self.attachmentListDialog.show )
        menu.addAction( attachAction )
        #
        menu.addSection( 'EMAIL ACTIONS' )
        pngAction = QAction( 'SHOW PNGS', menu )
        pngAction.triggered.connect( self.pngWidget.show )
        menu.addAction( pngAction )
        loadAction = QAction( 'LOAD RST', menu )
        loadAction.triggered.connect( self.loadFileName )
        menu.addAction( loadAction )
        saveAction = QAction( 'SAVE RST', menu )
        saveAction.triggered.connect( self.saveFileName )
        menu.addAction( saveAction )
        #
        return menu

    def contextMenuEvent( self, evt ):
        self.popupMenu.popup( QCursor.pos( ) )

    def changeEmailData( self, mydict ):
        assert('key' in mydict and 'names and emails' in mydict )
        assert(mydict[ 'key' ] in ( 'to', 'cc', 'bcc' ) )
        self.allData[ mydict[ 'key' ] ] = mydict[ 'names and emails' ]

    def changeAttachmentsData( self, mydict ):
        assert( 'attachments' in mydict )
        self.allData[ 'attachments' ] = mydict[ 'attachments' ]

    def sendEmail( self ):
        myString = self.getTextOutput( )
        htmlString = convert_string_RST( myString )
        if len( htmlString.strip( ) ) == 0:
            self.statusLabel.setText( 'OBVIOUSLY NO HTML. PLEASE FIX.' )
            return
        subject = self.subjLineEdit.text( ).strip( )
        if len( subject ) == 0:
            self.statusLabel.setText( 'NO SUBJECT. PLEASE FIX.' )
            return
        fullEmailString = formataddr( (
            self.allData[ 'from name' ], self.allData[ 'from email' ] ) )
        if fullEmailString == '':
            self.statusLabel.setText( 'NO FROM EMAIL ADDRESS. PLEASE FIX.' )
            return
        to_emails = set( self.allData[ 'to' ] )
        cc_emails = set( self.allData[ 'cc' ] )
        bcc_emails= set( self.allData[ 'bcc' ] ) | set([ fullEmailString ])
        attachments = self.allData[ 'attachments' ]
        logging.info( 'to_emails: %s.' % to_emails )
        logging.info( 'cc_emails: %s.' % cc_emails )
        logging.info( 'bcc_emails: %s.' % bcc_emails )
        logging.info( 'htmlString: %s.' % htmlString )
        if len( to_emails | cc_emails ) == 0:
            self.statusLabel.setText( 'NO TO OR CC EMAIL ADDRESSES. PLEASE FIX.' )
            return
        #
        ## now send the email out
        time0 = time.time( )
        num_emails = len( to_emails | cc_emails | bcc_emails )
        nprstuff_email.send_collective_email_full(
            htmlString, subject, fullEmailString,
            to_emails, cc_emails, bcc_emails, email_service = self.email_service,
            attachments = attachments )
        logging.info( 'sent out %d TO/CC/BCC emails in %0.3f seconds.' % (
            num_emails, time.time( ) - time0 ) )
        self.statusLabel.setText( 'SUCCESSFULLY SENT OUT %d EMAILS.' % num_emails )

    def fixSubject( self ):
        """
        strips out the empty characters within the subject line.
        """
        self.subjLineEdit.setText( self.subjLineEdit.text( ).strip( ) )

    def showRowCol( self ):
        """
        shows the row number and column number of the text cursor in the ``textOutput`` object's canvas.
        """
        cursor = self.textOutput.textCursor( )
        lineno = cursor.blockNumber( ) + 1
        colno  = cursor.columnNumber( ) + 1
        self.rowColLabel.setText( '(%d, %d)' % ( lineno, colno ) )

    #
    def saveFileName( self ):
        """
        This saves the reStructuredText_ that is currently within the ``textOutput`` object's canvas.

        .. seealso::
        
           * :py:meth:`loadFileName <howdy.core.core_texts_gui.ConvertWidget.loadFileName>`.
           * :py:meth:`getTextOutput <howdy.core.core_texts_gui.CovertWidget.getTextOutput>`.

        .. _reStructuredText: https://en.wikipedia.org/wiki/ReStructuredText
        """
        fname, _ = QFileDialog.getSaveFileName(
            self, 'Save ReStructuredText File', os.getcwd( ),
            filter = '*.rst' )
        if not fname.lower().endswith('.rst' ): return
        if len( os.path.basename( fname ) ) == 0: return
        with open( fname, 'w' ) as openfile:
            openfile.write( '%s\n' % self.getTextOutput( ) )

    def loadFileName( self ):
        """
        This loads a reStructuredText_ file (ends with ``.rst``) into the ``textOutput`` object's canvas.

        .. seealso::
        
           * :py:meth:`saveFileName <howdy.core.core_texts_gui.ConvertWidget.saveFileName>`.
           * :py:meth:`getTextOutput <howdy.core.core_texts_gui.CovertWidget.getTextOutput>`.
        """
        fname, _ = QFileDialog.getOpenFileName(
            self, 'Open ReStructuredText File', os.getcwd( ),
            filter = '*.rst' )
        if not fname.lower().endswith('.rst' ): return
        if len( os.path.basename( fname ) ) == 0: return
        myString = open( fname, 'r' ).read( )
        self.textOutput.setPlainText( myString )
        
    def getTextOutput( self ):
        """
        :returns: the ``textOutput`` object's canvas as a :py:class:`string <str>`.
        :rtype: str
        """
        return r"%s" % self.textOutput.toPlainText( ).strip( )

    def printHTML( self ):
        """
        launches a new :py:class:`HtmlView <howdy.core.core_text_gui.HtmlView>` that contains the rich HTML view of the reStructuredText_ that lives within the ``textOutput`` object's canvas.
        """
        self.statusLabel.setText( '' )
        myString = self.getTextOutput( )
        if not check_valid_RST( myString, use_mathjax = self.use_mathjax ):
            self.statusLabel.setText(
                'COULD NOT CONVERT FROM RST TO HTML' )
            return
        #
        qdl = QDialogWithPrinting( self, doQuit = False, isIsolated = True )
        #
        qdl.setModal( True )
        backButton = QPushButton( 'BACK' )
        forwardButton = QPushButton( 'FORWARD' )
        resetButton = QPushButton( 'RESET' )
        #
        ##
        qte = HtmlView( qdl, convert_string_RST( myString, use_mathjax = self.use_mathjax ) )
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
        #qte.setWidth( 85 * qfm.width( 'A' ) )
        #qte.setHeight( 550 )
        #qdl.width( 85 * qfm.width( 'A' ) )
        #qdl.height( 550 )
        qte.setMinimumSize( 85 * qfm.width( 'A' ), 550 )
        qdl.setMinimumSize( 85 * qfm.width( 'A' ), 550 )
        #
        resetButton.clicked.connect( qte.reset )
        backButton.clicked.connect( qte.back )
        forwardButton.clicked.connect( qte.forward )
        qte.setHtml( convert_string_RST( myString ) )
        #
        qte.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        qdl.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        self.statusLabel.setText( 'SUCCESS' )
        qdl.show( )
        qdl.exec_( )
