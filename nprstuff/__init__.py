__author__ = 'Tanim Islam'
__email__ = 'tanim.islam@gmail.com'

import sys, os, logging, numpy, requests, urllib3

#
## PyQt5 stuff
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

#
## SQLAlchemy stuff
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, JSON, Date, Boolean

#
## disable insecure request warnings
requests.packages.urllib3.disable_warnings( )
urllib3.disable_warnings( )

_mainDir = os.path.dirname( os.path.abspath( __file__ ) )
resourceDir = os.path.join( _mainDir, 'resources' )
assert( os.path.isdir( resourceDir ) )

baseConfDir = os.path.abspath( os.path.expanduser( '~/.config/nprstuff' ) )
"""
the directory where NPRStuff user data is stored -- ``~/.config/nprstuff``.
"""

logging_dict = {
    "NONE" : 100,
    "INFO" : logging.INFO,
    "DEBUG": logging.DEBUG,
    "ERROR": logging.ERROR }

def _get_nprstuff_logger( ):
    logging.basicConfig(format = '%(levelname)s %(module)s.%(funcName)s (%(lineno)d): %(message)s' )
    return logging.getLogger( )
    # h = logging.StreamHandler( sys.stdout )
    #formatter = logging.Formatter(
    # #    '%{levelno}s %{module}s.%{filename}s.%{funcName}s: %{message}s' )
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(message)s', style='{' )
    # h.setFormatter( formatter )
    # logger.addHandler( h )
    # return logger

# code to handle Ctrl+C, convenience method for command line tools
def signal_handler( signal, frame ):
    print( "You pressed Ctrl+C. Exiting...")
    sys.exit( 0 )

nprstuff_logger = _get_nprstuff_logger( )
# nprstuff_logger = logging.getLogger()


#
## follow directions in http://pythoncentral.io/introductory-tutorial-python-sqlalchemy/
_engine = create_engine( 'sqlite:///%s' % os.path.join( baseConfDir, 'app.db') )
Base = declarative_base( )
if not os.environ.get( 'READTHEDOCS' ):
    if not os.path.isdir( baseConfDir ):
        os.mkdir( baseConfDir )
    Base.metadata.bind = _engine
    session = sessionmaker( bind = _engine )( )
else: session = sessionmaker( )

#
## this will be used to replace all the existing credentials stored in separate tables
class NPRStuffConfig( Base ):
    """
    This SQLAlchemy_ ORM class contains the configuration data used for running all the NPRStuff tools. Stored into the ``nprconfig`` table in the SQLite3_ configuration database.

    :var service: the name of the configuration service we store. Index on this unique key. This is a :py:class:`Column <sqlalchemy.schema.Column>` containing a :py:class:`String <sqlalchemy.types.String>` of size 65536.
    :var data: the JSON formatted information on the data stored here. For instance, username and password can be stored in the following way
    
      .. code-block:: python

         { 'username' : USERNAME,
           'password' : PASSWORD }

      This is a :py:class:`Column <sqlalchemy.schema.Column>` containing a :py:class:`JSON <sqlalchemy.types.JSON>` object.

    .. _SQLAlchemy: https://www.sqlalchemy.org
    """    
    #
    ## create the table using Base.metadata.create_all( _engine )
    __tablename__ = 'nprconfig'
    __table_args__ = { 'extend_existing' : True }
    service = Column( String( 65536 ), index = True, unique = True, primary_key = True )
    data = Column( JSON )


def create_all( ):
    """
    creates the necessary SQLite3_ tables into the database file ``~/.config/nprstuff/app.db`` if they don't already exist, but only if not building documentation in `Read the docs`_.

    .. _SQLite3: https://en.wikipedia.org/wiki/SQLite
    .. _`Read the docs`: https://www.readthedocs.io
    """
    if os.environ.get( 'READTHEDOCS' ): return # do nothing if in READTHEDOCS
    Base.metadata.create_all( _engine )
    session.commit( )

create_all( ) # OK, now create the missing tables


#
## a QLabel with save option of the pixmap
class QLabelWithSave( QLabel ):
    """
    A convenient PyQt5_ widget that inherits from :py:class:`QLabel <PyQt5.QtWidgets.QLabel>`, but allows screen shots.

    .. _PyQt5: https://www.riverbankcomputing.com/static/Docs/PyQt5
    """
    
    def screenGrab( self ):
        """
        take a screen shot of itself and save to a PNG file through a :py:class:`QFileDialog <PyQt5.QtWidgets.QFileDialog>` widget.

        .. seealso:: :py:meth:`QDialogWithPrinting.screenGrab <nprstuff.QDialogWithPrinting.screenGrab>`.
        """
        fname, _ = QFileDialog.getSaveFileName(
            self, 'Save Pixmap', os.path.expanduser( '~' ),
            filter = '*.png' )
        if len( os.path.basename( fname.strip( ) ) ) == 0: return
        if not fname.lower( ).endswith( '.png' ):
            fname = '%s.png' % fname
        qpm = self.grab( )
        qpm.save( fname )

    def __init__( self, parent = None ):
        super( QLabel, self ).__init__( parent )

    def contextMenuEvent( self, event ):
        """Constructs a `context menu`_ with a single action, *Save Pixmap*, that takes a screen shot of this widget, using :py:meth:`screenGrab <nprstuff.QLabelWithSave.screenGrab>`.

        :param QEvent event: default :py:class:`QEvent <PyQt5.QtCore.QEvent>` argument needed to create a context menu. Is not used in this reimplementation.

        .. _`context menu`: https://en.wikipedia.org/wiki/Context_menu

        """
        menu = QMenu( self )
        savePixmapAction = QAction( 'Save Pixmap', menu )
        savePixmapAction.triggered.connect( self.screenGrab )
        menu.addAction( savePixmapAction )
        menu.popup( QCursor.pos( ) )

class QDialogWithPrinting( QDialog ):
    """
    A convenient PyQt5_ widget, inheriting from :py:class:`QDialog <PyQt5.QtWidgets.QDialog>`, that allows for screen grabs and keyboard shortcuts to either hide this dialog window or quit the underlying program. This PyQt5_ widget is also resizable, in relative increments of 5% larger or smaller, to a maximum of :math:`1.05^5` times the initial size, and to a minimum of :math:`1.05^{-5}` times the initial size.
    
    Args:
        parent (:py:class:`QWidget <PyQt5.QtWidgets.QWidget>`): the parent :py:class:`QWidget <PyQt5.QtWidgets.QWidget>` to this dialog widget.
        isIsolated (bool): If ``True``, then this widget is detached from its parent. If ``False``, then this widget is embedded into a layout in the parent widget.
        doQuit (bool): if ``True``, then using the quit shortcuts (``Esc`` or ``Ctrl+Shift+Q``) will cause the underlying program to exit. Otherwise, hide the progress dialog.

     
    :var indexScalingSignal: a :py:class:`pyqtSignal <PyQt5.QtCore.pyqtSignal>` that can be connected to other PyQt5_ events or methods, if resize events want to be recorded.
    :type indexScalingSignal: :py:class:`pyqtSignal <PyQt5.QtCore.pyqtSignal>` that can be connected to other PyQt5_ events or methods.
    :var int initWidth: the initial width of the GUI in pixels.
    :var int initHeight: the initial heigth of the GUI in pixels.    
    """
    
    indexScalingSignal = pyqtSignal( int )
    
    def screenGrab( self ):
        """
        take a screen shot of itself and saver to a PNG file through a :py:class:`QFileDialog <PyQt5.QtGui.QFileDialog>` widget.
        
        .. seealso:: :py:meth:`QLabelWithSave.screenGrab <nprstuff.QLabelWithSave.screenGrab>`.
        """
        fname, _ = QFileDialog.getSaveFileName(
            self, 'Save Screenshot', os.path.expanduser( '~' ),
            filter = '*.png' )
        if len( os.path.basename( fname.strip( ) ) ) == 0: return
        if not fname.lower( ).endswith( '.png' ):
            fname = '%s.png' % fname
        qpm = self.grab( )
        qpm.save( fname )

    def reset_sizes( self ):
        """
        Sets the default widget size to the current size.
        """
        
        self.initWidth = self.width( )
        self.initHeight = self.height( )
        self.resetSize( )

    def makeBigger( self ):
        """
        makes the widget incrementally 5% larger, for a maximum of :math:`1.05^5`, or approximately 28% larger than, the initial size.
        """
        
        newSizeRatio = min( self.currentSizeRatio + 1,
                            len( self.sizeRatios ) - 1 )
        if newSizeRatio != self.currentSizeRatio:
            self.setFixedWidth( self.initWidth * 1.05**( newSizeRatio - 5 ) )
            self.setFixedHeight( self.initHeight * 1.05**( newSizeRatio - 5 ) )
            self.currentSizeRatio = newSizeRatio
            self.indexScalingSignal.emit( self.currentSizeRatio - 5 )
            
    def makeSmaller( self ):
        """
        makes the widget incrementally 5% smaller, for a minimum of :math:`1.05^{-5}`, or approximately 28% smaller than, the initial size.
        """
        newSizeRatio = max( self.currentSizeRatio - 1, 0 )
        if newSizeRatio != self.currentSizeRatio:
            self.setFixedWidth( self.initWidth * 1.05**( newSizeRatio - 5 ) )
            self.setFixedHeight( self.initHeight * 1.05**( newSizeRatio - 5 ) )
            self.currentSizeRatio = newSizeRatio
            self.indexScalingSignal.emit( self.currentSizeRatio - 5 )

    def resetSize( self ):
        """
        reset the widget size to the initial size.
        """
        
        if self.currentSizeRatio != 5:
            self.setFixedWidth( self.initWidth )
            self.setFixedHeight( self.initHeight )
            self.currentSizeRatio = 5
            self.indexScalingSignal.emit( 0 )
    #
    ## these commands are run after I am in the event loop. Get lists of sizes
    def on_start( self ):
        if not self.isIsolated: return
        self.reset_sizes( )
        #
        ## set up actions

        #
        ## make bigger
        makeBiggerAction = QAction( self )
        makeBiggerAction.setShortcut( 'Ctrl+|' )
        makeBiggerAction.triggered.connect( self.makeBigger )
        self.addAction( makeBiggerAction )
        #
        ## make smaller
        makeSmallerAction = QAction( self )
        makeSmallerAction.setShortcut( 'Ctrl+_' )
        makeSmallerAction.triggered.connect( self.makeSmaller )
        self.addAction( makeSmallerAction )
        #
        ## reset to original size
        resetSizeAction = QAction( self )
        resetSizeAction.setShortcut( 'Shift+Ctrl+R' )
        resetSizeAction.triggered.connect( self.resetSize )
        self.addAction( resetSizeAction )        

    def __init__( self, parent, isIsolated = True, doQuit = True ):
        super( QDialogWithPrinting, self ).__init__( parent )
        self.setModal( True )
        self.isIsolated = isIsolated
        self.initWidth = self.width( )
        self.initHeight = self.height( )
        self.sizeRatios = numpy.array(
            [ 1.05**(-idx) for idx in range(1, 6 ) ][::-1] + [ 1.0, ] +
            [ 1.05**idx for idx in range(1, 6 ) ] )
        self.currentSizeRatio = 5
        #
        ## timer to trigger on_start function on start of app
        QTimer.singleShot( 0, self.on_start )
        #
        if isIsolated:
            printAction = QAction( self )
            printAction.setShortcuts( [ 'Shift+Ctrl+P' ] )
            printAction.triggered.connect( self.screenGrab )
            self.addAction( printAction )
            #
            quitAction = QAction( self )
            quitAction.setShortcuts( [ 'Ctrl+Q', 'Esc' ] )
            if not doQuit:
                quitAction.triggered.connect( self.hide )
            else:
                quitAction.triggered.connect( sys.exit )
            self.addAction( quitAction )

class ProgressDialogThread( QThread ):
    """
    This subclassing of :py:class:`QThread <PyQt5.QtCore.QThread>` provides a convenient scaffolding to run, in a non-blocking fashion, some long-running processes with an asssociated :py:class:`ProgressDialog <nprstuff.ProgressDialog>` widget.

    Subclasses of this object need to have a particular structure for their ``__init__`` method. The first three arguments MUST be ``self``, ``parent``, ``self`` is a reference to this object. ``parent`` is the parent :py:class:`QWidget <PyQt5.QtWidgets.QWidget>` to which the :py:class:`ProgressDialog <nprstuff.ProgressDialog>` attribute, named ``progress_dialog``, is the child. ``title`` is the title of ``progress_dialog``. Here is an example, where an example class named ``ProgressDialogThreadChildClass`` inherits from  :py:class:`ProgressDialogThread <nprstuff.ProgressDialogThread>`.

    .. code-block:: python

       def __init__( self, parent, *args, **kwargs ):
           super( ProgressDialogThreadChildClass, self ).__init__( parent, title )

           # own code to initialize based on *args and **kwargs

    This thing has an associated :py:meth:`run <ProgressDialogThread.run>` method that is expected to be partially implemented in the following manner for subclasses of :py:class:`ProgressDialogThread <howdy.ProgressDialogThread>`.

    * It must start with ``self.progress_dialog.show( )`` to show the progress dialog widget.

    * It must end with this command, ``self.stopDialog.emit( )`` to hide the progress dialog widget.

    Here is an example.

    .. code-block:: python

       def run( self ):
           self.progress_dialog.show( )
           # run its own way
           self.stopDialog.emit( )

    In the :py:meth:`run <howdy.ProgressDialogThread.run>` method, if one wants to print out something into ``progess_dialog``, then there should be these types of commands in ``run``: ``self.emitString.emit( mystr )``, where ``mystr`` is a :py:class:`str` message to show in ``progress_dialog``, and ``emitString`` is a :py:class:`pyqtsignal <PyQt5.QtCore.pyqtSignal>` connected to the ``progress_dialog`` object's :py:meth:`addText( ) <nprstuff.ProgressDialog.addText>`.
    
    :param parent: the parent widget for which this long-lasting process will pop up a progress dialog.
    :param str title: the title for the ``progress_dialog`` widget.
    :type parent: :py:class:`QWidget <PyQt5.QtWidgets.QWidget>`

    :var emitString: the signal, with :py:class:`str` signature, that is triggered to send progress messages into ``progress_dialog``.
    :var stopDialog: the signal that is triggered to stop the ``progress_dialog``, calling :py:meth:`stopDialog <nprstuff.ProgressDialog.stopDialog>`.
    :var startDialog: the signal, with :py:class:`str` signature, that is triggered to restart the ``progress_dialog`` widget, calling :py:class:`startDialog <nprstuff.ProgressDialog.startDialog>`.
    :var progress_dialog: the GUI that shows, in a non-blocking fashion, the progress on some longer-running method.
    :var int time0: a convenience attribute, the UTC time at which the ``progress_dialog`` object was first instantiated. Can be used to determine the time each submethod takes (for example, ``time.time( ) - self.time0``).
    :type emitString: :py:class:`pyqtSignal <PyQt5.QtCore.pyqtSignal>`
    :type stopDialog: :py:class:`pyqtSignal <PyQt5.QtCore.pyqtSignal>`
    :type startDialog: :py:class:`pyqtSignal <PyQt5.QtCore.pyqtSignal>`
    :type progress_dialog: :py:class:`ProgressDialog <nprstuff.ProgressDialog>`
    
    .. seealso:: :py:class:`ProgressDialog <nprstuff.ProgressDialog>`.
    """
    emitString = pyqtSignal( str )
    stopDialog = pyqtSignal( ) 
    startDialog= pyqtSignal( str )
    
    def __init__( self, parent, title ):
        super( ProgressDialogThread, self ).__init__( )
        self.progress_dialog = ProgressDialog( parent, title )
        #
        ## must do these things because unsafe to manipulate this thing from separate thread
        self.emitString.connect( self.progress_dialog.addText )
        self.stopDialog.connect( self.progress_dialog.stopDialog )
        self.startDialog.connect( self.progress_dialog.startDialog )
        self.progress_dialog.hide( )
        self.time0 = self.progress_dialog.t0
            
class ProgressDialog( QDialogWithPrinting ):
    """
    A convenient PyQt5_ widget, inheriting from :py:class:`QDialogWithPrinting <nprstuff.QDialogWithPrinting>`, that acts as a GUI blocking progress window for longer lasting operations. Like its parent class, this dialog widget is also resizable. This shows the passage of the underlying slow process in 5 second increments.

    This progress dialog exposes three methods -- :py:meth:`addText <nprstuff.ProgressDialog.addText>`, :py:meth:`stopDialog <nprstuff.ProgressDialog.stopDialog>`, and :py:meth:`startDialog <nprstuff.ProgressDialog.startDialog>` -- to which a custom :py:class:`QThread <PyQt5.QtCore.QThread>` object can connect.
    
    * :py:meth:`startDialog <nprstuff.ProgressDialog.startDialog>` is triggered on long operation start, sometimes with an initial message.
    
    * :py:meth:`addText <nprstuff.ProgressDialog.addText>` is triggered when some intermediate progress text must be returned.
    
    * :py:meth:`stopDialog <nprstuff.ProgressDialog.stopDialog>` is triggered on process end.

    :param parent: the parent :py:class:`QWidget <PyQt5.QtWidgets.QWidget>` on which this dialog widget blocks.
    :param str windowTitle: the label to put on this progress dialog in an internal :py:class:`QLabel <PyQt5.QtWidgets.QLabel>`.
    :param bool doQuit: if ``True``, then using the quit shortcuts (``Esc`` or ``Ctrl+Shift+Q``) will cause the underlying program to exit. Otherwise, hide the progress dialog.
    :type parent: :py:class:`QWidget <PyQt5.QtWidgets.QWidget>`

    :var mainDialog: the main dialog widget in this GUI.
    :var parsedHTML: the :py:class:`BeautifulSoup <bs4.BeautifulSoup>` structure that contains the indexable tree of progress dialogs.
    :var elapsedTime: the bottom :py:class:`QLabel <PyQt5.QtWidgets.QLabel>` widget that displays how much time (in seconds) has passed.
    :var timer: the :py:class:`QTimer <PyQt5.QtCore.QTimer>` sub-thread that listens every 5 seconds before emitting a signal.
    :var float t0: the UNIX time, in seconds with resolution of microseconds.
    
    :vartype mainDialog: :py:class:`QTextEdit <PyQt5.QtWidgets.QTextEdit>`
    :vartype parsedHTML: :py:class:`BeautifulSoup <bs4.BeautifulSoup>`
    :vartype elapsedTime: :py:class:`QLabel <PyQt5.QtWidgets.QLabel>`
    :vartype timer: :py:class:`QTimer <PyQt5.QtCore.QTimer>`
    """
    def __init__( self, parent, windowTitle = "", doQuit = True ):
        super( ProgressDialog, self ).__init__(
            parent, doQuit = doQuit )
        self.setModal( True )
        self.setWindowTitle( 'PROGRESS' )
        myLayout = QVBoxLayout( )
        self.setLayout( myLayout )
        self.setFixedWidth( 300 )
        self.setFixedHeight( 400 )
        myLayout.addWidget( QLabel( windowTitle ) )
        self.mainDialog = QTextEdit( )
        self.parsedHTML = BeautifulSoup("""
        <html>
        <body>
        </body>
        </html>""", 'lxml' )
        self.mainDialog.setHtml( self.parsedHTML.prettify( ) )
        self.mainDialog.setReadOnly( True )
        self.mainDialog.setStyleSheet("""
        QTextEdit {
        background-color: #373949;
        }""" )
        myLayout.addWidget( self.mainDialog )
        #
        self.elapsedTime = QLabel( )
        self.elapsedTime.setStyleSheet("""
        QLabel {
        background-color: #373949;
        }""" )
        myLayout.addWidget( self.elapsedTime )
        self.timer = QTimer( )
        self.timer.timeout.connect( self.showTime )
        self.t0 = time.time( )
        self.timer.start( 5000 ) # every 5 seconds
        self.show( )

    def showTime( self ):
        """
        method connected to the internal :py:attr:`timer` that prints out how many seconds have passed, on the underlying :py:attr:`elapsedTime` :py:class:`QLabel <PyQt5.QtWidgets.QLabel>`.
        """
        dt = time.time( ) - self.t0
        self.elapsedTime.setText(
            '%0.1f seconds passed' % dt )
        if dt >= 50.0:
            logging.basicConfig( level = logging.DEBUG )

    def addText( self, text ):
        """adds some text to this progress dialog window.

        :param str text: the text to add.
        
        """
        body_elem = self.parsedHTML.find_all('body')[0]
        txt_tag = self.parsedHTML.new_tag("p")
        txt_tag.string = text
        body_elem.append( txt_tag )
        self.mainDialog.setHtml( self.parsedHTML.prettify( ) )

    def stopDialog( self ):
        """
        stops running, and hides, this progress dialog.
        """
        self.timer.stop( )
        self.hide( )

    def startDialog( self, initString = '' ):
        """starts running the progress dialog, with an optional labeling string, and starts the timer.

        :param str initString: optional internal labeling string.
        """
        self.t0 = time.time( )
        self.timer.start( )
        #
        ## now reset the text
        self.parsedHTML = BeautifulSoup("""
        <html>
        <body>
        </body>
        </html>""", 'lxml' )
        self.mainDialog.setHtml( self.parsedHTML.prettify( ) )
        if len( initString ) != 0:
            self.addText( initString )
        self.timer.stop( ) # if not already stopped
        self.t0 = time.time( )
        self.timer.start( 5000 )
        self.show( )
