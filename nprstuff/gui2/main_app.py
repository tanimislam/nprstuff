import copy, os, sys, titlecase, datetime, time, requests, glob
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
#
from nprstuff import resourceDir
from nprstuff.gui2.gui_common import get_database_data, get_article_data
from nprstuff.gui2.login_window import LoginWindow
from nprstuff.gui2.main_gui import ArticleWidget, ArticlesListWidget, _demo_get_articles

class MainApp(QApplication):
    def __init__(self, args):
        super(MainApp, self).__init__(args)
        self.cookies = None
        mainPath = os.path.join( resourceDir, 'fonts' )
        for fontFile in glob.glob(
            os.path.join( mainPath, '*.ttf' ) ):
            QFontDatabase.addApplicationFont( fontFile )
        #
        ##
        self.aw = ArticleWidget( self )
        self.alw = ArticlesListWidget( self )
        self.lw = LoginWindow( self )
        self.aw.hide()
        self.alw.hide()
        self.lw.hide()
        self.aboutToQuit.connect( self.cleanUp )

    def doLogon(self):
        time0 = time.time()
        print( 'STARTING TO LOGIN' )
        statusdict = get_database_data( )
        print( 'FINISHED LOGIN STUFF IN %0.3f SECONDS: %s' % (
            time.time() - time0, statusdict['message'] ) )
        if statusdict['message'] != 'SUCCESS':
            self.lw.setFromStatus( statusdict )
            self.lw.show()
        else:
            self.cookies = statusdict['cookies']
            email = statusdict['email']
            password = statusdict['password']
            data = get_article_data( email, password, self.cookies )
            self.pushData( data['articles'], data['ids_ordered'] )
            
    def pushDataFromCreds(self, email, password, cookies ):
        self.cookies = cookies
        data = get_article_data( email, password, cookies )
        self.pushData( data['articles'], data['ids_ordered'] )        
            
    def pushData(self, articles, ordered_ids ):
        self.articles = copy.deepcopy( articles )
        self.alw.pushTableData( articles, ordered_ids )
        self.lw.hide()
        self.lw.wipeAllData()
        self.alw.show()
        self.aw.show()

    def cleanUp(self):
        url = urljoin( 'https://tanimislam.ddns.net',
                       '/flask/api/nprstuff/readability/logout' )
        resp = requests.get( url, cookies = self.cookies )        

    def pushContent(self, articleId ):
        assert(articleId in self.articles )
        self.aw.articlePanel.setHtml( BeautifulSoup(
            self.articles[ articleId ]['content'], 'html.parser' ).prettify() )
        self.aw.titleLabel.setText(
            titlecase.titlecase( self.articles[ articleId ]['title' ] ) )
        s_dt = self.articles[ articleId ]['date_published' ]
        wc = self.articles[ articleId ]['word_count']
        if s_dt is None:
            dtime = _badDate
            date_string = 'NODATE'
            time_string = 'NOTIME'
        else:
            dtime = datetime.datetime.strptime( s_dt, '%Y-%m-%d %H:%M:%S' )
            date_string = dtime.strftime('%m/%d/%Y')
            time_string = dtime.strftime('%H:%M:%S')
        self.aw.dateLabel.setText( date_string )
        self.aw.timeLabel.setText( time_string )
        self.aw.wcLabel.setText( '%d words' % wc )
