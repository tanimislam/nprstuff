import os, sys, datetime, requests, copy, titlecase, datetime
import pickle, gzip, binascii, json, numpy, random
from urlparse import urljoin
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from gui_common import get_database_data, colorwheel
from gui_common import QPushButtonCustom

_badDate = datetime.datetime.strptime("January 1, 1000", "%B %d, %Y")

def demo_get_articles(email, password):
    if not os.path.isfile( 'articledata.pkl.gz' ):
        url = urljoin( 'https://tanimislam.ddns.net',
                       '/flask/api/nprstuff/readability/login')
        response = requests.get( url, auth = ( email, password ) )
        cookie = response.cookies
        url = urljoin( 'https://tanimislam.ddns.net',
                       '/flask/api/nprstuff/readability/getarticles' )
        response = requests.get( url, auth = ( email, password ), cookies = cookie )
        data = json.loads( binascii.a2b_hex( response.json()['data'] ).decode('bz2' ) )
        pickle.dump(data, gzip.open( 'articledata.pkl.gz', 'w') )
        return data
    else:
        return pickle.load( gzip.open( 'articledata.pkl.gz', 'r' ) )

class ArticleWidget(QGroupBox):
    def __init__(self, parent):
        super(ArticleWidget, self).__init__()
        self.setWindowTitle("ARTICLE TEXT")
        self.parent = parent
        #
        layout = QVBoxLayout()
        self.setLayout( layout )
        self.titleLabel = QLabel("")
        self.titleLabel.setWordWrap(True)
        self.wcLabel = QLabel("")
        self.dateLabel = QLabel("")
        self.timeLabel = QLabel("")
        self.articlePanel = QTextEdit("")
        self.articlePanel.setReadOnly(True)
        self.fontButton = QPushButtonCustom("FONT")
        self.printButton = QPushButtonCustom("PRINT")
        self.ebookButton = QPushButtonCustom("EBOOK")
        topPanel = QWidget()
        midPanel = QWidget()
        botPanel = QWidget()
        layout.addWidget( topPanel )
        layout.addWidget( midPanel )
        layout.addWidget( botPanel )
        newcolors = copy.deepcopy( colorwheel )
        random.shuffle( newcolors )
        for idx, qw in enumerate([ topPanel, midPanel, botPanel ]):
            qw.setStyleSheet("""
            QWidget {
            background-color: %s;
            }
            """ % newcolors[idx % 6].name() )
        #
        topPanelLayout = QGridLayout()
        topPanel.setLayout( topPanelLayout )
        q1 = QLabel("TITLE:")
        q2 = QLabel("DATE:")
        q3 = QLabel("TIME:")
        for ql in (q1, q2, q3, self.wcLabel):
            ql.setStyleSheet("""
            QLabel {
            font-weight: bold;
            font-size: 12;
            }
            """)
        topPanelLayout.addWidget( q1, 0, 0, 1, 1)
        topPanelLayout.addWidget( self.titleLabel, 0, 1, 1, 2)
        topPanelLayout.addWidget( self.wcLabel, 0, 3, 1, 1)
        topPanelLayout.addWidget( q2, 1, 0, 1, 1)
        topPanelLayout.addWidget( self.dateLabel, 1, 1, 1, 1)
        topPanelLayout.addWidget( q3, 1, 2, 1, 1)
        topPanelLayout.addWidget( self.timeLabel, 1, 3, 1, 1)
        #
        midPanelLayout = QVBoxLayout()
        midPanel.setLayout( midPanelLayout )
        midPanelLayout.addWidget( self.articlePanel )
        #
        botPanelLayout = QGridLayout()
        botPanel.setLayout( botPanelLayout )
        botPanelLayout.addWidget( self.fontButton, 0, 0, 1, 1)
        botPanelLayout.addWidget( self.printButton, 0, 1, 1, 1)
        botPanelLayout.addWidget( self.ebookButton, 0, 2, 1, 1)
        #
        self.resize( 500, 800 )
        self.setFixedWidth( 500 )
        self.setFixedHeight( 800 )
        #
        self.fontButton.clicked.connect( self.chooseFont )
        self.printButton.clicked.connect( self.printArticle )
        self.ebookButton.clicked.connect( self.makeEbook )

    def chooseFont(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.articlePanel.setFont( font )


    def printArticle(self):
        dialog = QPrintPreviewDialog()
        #self._disableMainDialog()
        qtd = QTextDocument()
        qtd.setHtml( self.articlePanel.toHtml() )
        dialog.paintRequested.connect( qtd.print_ )
        dialog.exec_()
        #self._enableMainDialog()

    def makeEbook(self):
        print 'MAKING EBOOK'
        

class ArticlesListWidget(QWidget):
    def __init__(self, parent):
        super(ArticlesListWidget, self).__init__()
        self.setWindowTitle("ARTICLE TITLES")
        layout = QVBoxLayout()
        self.setLayout( layout )
        self.create_table_and_model( )
        layout.addWidget( self.table )
        self.table.clicked.connect( self.doClickedTable )
        self.parent = parent
    
    # fix this part here
    # self.table.clicked.connect( self.doClickedTable )
    def doClickedTable(self, clickedIndex):
        row = clickedIndex.row()
        model = clickedIndex.model()
        act_index = model.index( row, 4 )
        articleId = str( model.data( act_index, Qt.DisplayRole ).toString() )
        self.parent.pushContent( articleId )
                
    def scrollUpOnePage( self ):
        self.table.scrollContentsBy( 0, -450 )

    def scrollDownOnePage( self ):
        self.table.scrollContentsBy( 0, 450 )
    
    def pushTableData( self, articles, ordered_ids ):
        tabledata = []
        lengths = []
        lengths_ds = []
        lengths_ts = []
        qfm = QFontMetrics( self.table.font() )
        for articleId in ordered_ids:
            artsub = articles[articleId]
            title = titlecase.titlecase( artsub['title'] )
            s_dt = artsub['date_published']
            lengths.append( qfm.boundingRect( title ).width( ) )
            if s_dt is None:
                dtime = _badDate
                date_string = 'NODATE'
                time_string = 'NOTIME'
            else:
                dtime = datetime.datetime.strptime( s_dt, '%Y-%m-%d %H:%M:%S' )
                date_string = dtime.strftime('%m/%d/%Y')
                time_string = dtime.strftime('%H:%M:%S')
            lengths_ds.append( qfm.boundingRect( date_string ).width( ) )
            lengths_ts.append( qfm.boundingRect( time_string ).width( ) )
            tabledata.append( [ title, date_string, time_string, dtime, articleId ])
        self.tm.pushData( tabledata )
        for column in (1, 2):
            self.table.resizeColumnToContents( column )        
        #
        ## 75% bar set length for title column
        lengths = numpy.sort( lengths )
        tot_length = len( lengths )
        length_to_set = lengths[ int( 0.85 * tot_length ) ]
        self.table.setColumnWidth(0, length_to_set )
        self.table.setColumnWidth(1, 1.5 * max( lengths_ds ) )
        self.table.setColumnWidth(2, 1.5 * max( lengths_ts ) )
        #
        ## set length
        setTotalLength = sum([ self.table.columnWidth( idx ) for
                               idx in (0, 1, 2) ])
        self.resize( setTotalLength * 1.1, 450 )
        self.setFixedWidth( setTotalLength * 1.1 )
        self.setFixedHeight( 450 )
            
    def create_table_and_model( self ):
        self.table = QTableView( self )
        self.tm = MyTableModel( self )
        self.table.setModel( self.tm )
        self.table.setColumnHidden(3, True)
        self.table.setColumnHidden(4, True)
        self.table.setItemDelegateForColumn(0, TitleDelegate( self ) )
        self.table.setItemDelegateForColumn(1, DateDelegate( self ) )
        self.table.setItemDelegateForColumn(2, TimeDelegate( self ) )

        # set the minimum size
        self.table.setMinimumSize( 500, 400 )
        
        # show grid
        self.table.setShowGrid( True )
        
        # set fixed vertical headers
        self.table.verticalHeader().setResizeMode( QHeaderView.Fixed )
        hheader = self.table.horizontalHeader()
        hheader.setResizeMode( QHeaderView.Fixed )
        qf = hheader.font()
        qf.setBold( True )
        qf.setPointSize( 12)
        hheader.setFont( qf )
        
        # hide vertical header
        self.table.verticalHeader().setVisible( False )
        
        # set sorting enabled
        self.table.setSortingEnabled( False )
        
        # other stuff
        self.table.setSelectionBehavior( QTableView.SelectRows )
        
        # slots
        self.tm.layoutChanged.connect( self.table.resizeColumnsToContents )

        # end button scroll to bottom
        toBotAction = QAction( self.table )
        toBotAction.setShortcut( 'End' )
        toBotAction.triggered.connect( self.table.scrollToBottom )
        self.table.addAction( toBotAction )

        # home button scroll to top
        toTopAction = QAction( self.table )
        toTopAction.setShortcut( 'Home' )
        toTopAction.triggered.connect( self.table.scrollToTop )
        self.table.addAction( toTopAction )

        # up one page
        upOnePageAction = QAction( self.table )
        upOnePageAction.setShortcut( 'PgUp' )
        upOnePageAction.triggered.connect( self.scrollUpOnePage )
        self.table.addAction( upOnePageAction )

        # down one page
        downOnePageAction = QAction( self.table )
        downOnePageAction.setShortcut( 'PgDown' )
        downOnePageAction.triggered.connect( self.scrollDownOnePage )
        self.table.addAction( downOnePageAction )        
        
class TitleDelegate(QItemDelegate):
    def __init__(self, owner):
        super(TitleDelegate, self).__init__(owner)

    def createEditor(self, parent, option, index):
        rowNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 0 )
        title = str( model.data( act_index, Qt.DisplayRole ).toString() ).strip()
        editor = QLabel( title, parent = parent )
        return editor

    def setEditor(self, editor, index ):
        rowNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 0 )
        title = str( model.data( act_index, Qt.DisplayRole ).toString() ).strip()
        editor.setText( title )

class DateDelegate(QItemDelegate):
    def __init__(self, owner):
        super(DateDelegate, self).__init__(owner)

    def createEditor(self, parent, option, index):
        rowNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 3 )
        dtime = model.data( act_index, Qt.DisplayRole).toDateTime().toPyDateTime()
        if dtime == _badDate:
            editor = QLabel("NODATE", parent = parent)
        else:
            editor = QLabel( dtime.strftime( '%m/%d/%Y' ), parent = parent )
        return editor

    def setEditorData(self, editor, index):
        rowNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 3 )
        dtime = model.data( act_index, Qt.DisplayRole).toDateTime().toPyDateTime()
        if dtime == _badDate:
            editor.setText( "NODATE" )
        else:
            editor.setText( dtime.strftime( "%m/%d/%Y" ) )

class TimeDelegate(QItemDelegate):
    def __init__(self, owner):
        super(TimeDelegate, self).__init__(owner)

    def createEditor(self, parent, option, index):
        rowNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 3 )
        dtime = model.data( act_index, Qt.DisplayRole).toDateTime().toPyDateTime()
        if dtime == _badDate:
            editor = QLabel("NOTIME", parent = parent)
        else:
            editor = QLabel( dtime.strftime( '%H:%M:%S' ), parent = parent )
        return editor

    def setEditorData(self, editor, index):
        owNumber = index.row()
        model = index.model()
        act_index = model.index( rowNumber, 3 )
        dtime = model.data( act_index, Qt.DisplayRole).toDateTime().toPyDateTime()
        if dtime == _badDate:
            editor.setText( "NOTIME" )
        else:
            editor.setText( dtime.strftime( '%H:%M:%S' ) )

class MyTableModel(QAbstractTableModel):
    def __init__(self, parent = None):
        super(MyTableModel, self).__init__(parent)
        self.arrayData = []
        self.headerData = [ "title", "date" , "time", "datetime", "articleId" ]

    def pushData(self, tabledata):
        #
        ## first remove all rows that exist
        initRowCount = self.rowCount(None)
        self.beginRemoveRows( QModelIndex(), 0, initRowCount - 1 )
        self.arrayData = []
        self.endRemoveRows( )
        #
        ## now add the rows from tabledata
        self.beginInsertRows( QModelIndex(), 0, len( tabledata ) - 1 )
        self.arrayData = tabledata
        self.endInsertRows( )
        self.sort(0, Qt.DescendingOrder )

    def rowCount(self, parent):
        return len( self.arrayData )

    def columnCount( self, parent ):
        return len( self.headerData )

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role == Qt.BackgroundRole:
            return QBrush( colorwheel[ index.row() % 6 ] )
        elif role != Qt.DisplayRole:
            return QVariant()
        else:
            return QVariant( self.arrayData[ index.row() ][ index.column() ] )

    def setData( self, index, value, role ):
        if not index.isValid():
            return
        if index.column() in (0, 1, 2, 4):
            self.arrayData[ index.row() ][ index.column() ] = str( value.toString() )
        elif index.column() == 3:
            self.arrayData[ index.row() ][ 3 ] = value.toDateTime().toPyDateTime() 

    def flags( self, index ):
        return Qt.ItemFlags( Qt.ItemIsSelectable | Qt.ItemIsEnabled )

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant( self.headerData[ col ] )
        return QVariant( )

    def sort(self, ncol, order):
        self.layoutAboutToBeChanged.emit()
        if order == Qt.AscendingOrder:
            self.arrayData = sorted(self.arrayData, key = lambda tup: tup[3] )
        else:
            self.arrayData = sorted(self.arrayData, key = lambda tup: tup[3] )[::-1]
        self.layoutChanged.emit()
