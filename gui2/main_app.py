#!/usr/bin/env python

from PyQt4.QtGui import *
import copy, os, sys, titlecase, datetime
from gui_common import get_database_data, get_article_data
from login_window import LoginWindow
from main_gui import ArticleWidget, ArticlesListWidget
from main_gui import demo_get_articles
from bs4 import BeautifulSoup

class MainApp(QApplication):
    def __init__(self, args):
        super(MainApp, self).__init__(args)
        self.aw = ArticleWidget( self )
        self.alw = ArticlesListWidget( self )
        self.lw = LoginWindow( self )
        self.aw.hide()
        self.alw.hide()
        self.lw.hide()
        #
        statusdict = get_database_data( )
        if statusdict['message'] != 'SUCCESS':
            self.lw.setFromStatus( statusdict )
            self.lw.show()
        else:
            cookies = statusdict['cookies']
            email = statusdict['email']
            password = statusdict['password']
            data = get_article_data( email, password, cookies )
            self.pushData( data['articles'], data['ids_ordered'] )
            
    def pushData(self, articles, ordered_ids ):
        self.articles = copy.deepcopy( articles )
        self.alw.pushTableData( articles, ordered_ids )
        self.alw.show()
        self.aw.show()
        self.lw.hide()
        self.lw.wipeAllData()

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
    #ma.pushData( data['articles'], data['ids_ordered'] )
    sys.exit( ma.exec_() )



    
