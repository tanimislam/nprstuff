#!/usr/bin/env python

from PyQt4.QtGui import *
import copy, os, sys, titlecase, datetime, time, requests
from gui_common import get_database_data, get_article_data
from login_window import LoginWindow
from main_gui import ArticleWidget, ArticlesListWidget
from main_gui import demo_get_articles
from bs4 import BeautifulSoup
from urlparse import urljoin

class MainApp(QApplication):
    def __init__(self, args):
        super(MainApp, self).__init__(args)
        self.cookies = None
        self.aw = ArticleWidget( self )
        self.alw = ArticlesListWidget( self )
        self.lw = LoginWindow( self )
        self.aw.hide()
        self.alw.hide()
        self.lw.hide()
        self.aboutToQuit.connect( self.cleanUp )

    def doLogon(self):
        time0 = time.time()
        print 'STARTING TO LOGIN'
        statusdict = get_database_data( )
        print 'FINISHED LOGIN STUFF IN %0.3f SECONDS: %s' % (
            time.time() - time0, statusdict['message'] )
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
            self.articles[ articleId ]['content'] ).prettify() )
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
        

if __name__=='__main__':
    #data = demo_get_articles('', '')
    ma = MainApp(sys.argv)
    ma.doLogon( )
    # ma.pushData( data['articles'], data['ids_ordered'] )
    sys.exit( ma.exec_() )
