#!/usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os, sys, numpy, requests, json
import xdg.BaseDirectory, ConfigParser

colorwheel = [ QColor( QString( name ) ) for name in
               [ '#E5EDE9', '#EDE6CE', '#EDDFEB', '#F1EDFE', '#CCD9FD', '#F9EBFD' ] ]

class QPushButtonCustom( QPushButton ):
    def __init__(self, parent = None):
        super(QPushButton, self).__init__( parent = parent )
        self.setStyleSheet("""
        QPushButtonCustom {
        border-width: 3px;
        border-color: red;
        border-style: solid;
        border-radius: 7px;
        padding: 3px;
        font-size: 12px;
        font-weight: bold;
        padding-left: 5px;
        padding-right: 5px;
        min-width: 50px;
        max-width: 50px;
        min-height: 13px;
        max-height: 13px;
        }
        """)
    
    def __init__(self, text, parent = None):
        super(QPushButton, self).__init__( text, parent = parent )
        self.setStyleSheet("""
        QPushButtonCustom {
        border-width: 3px;
        border-color: red;
        border-style: solid;
        border-radius: 7px;
        padding: 3px;
        font-size: 12px;
        font-weight: bold;
        padding-left: 5px;
        padding-right: 5px;
        min-width: 50px;
        max-width: 50px;
        min-height: 13px;
        max-height: 13px;
        }
        """)

    def __init__(self, icon, text, parent = None):
        super(QPushButton, self).__init__( icon, text, parent = parent )
        self.setStyleSheet("""
        QPushButtonCustom {
        border-width: 3px;
        border-color: red;
        border-style: solid;
        border-radius: 7px;
        padding: 3px;
        font-size: 12px;
        font-weight: bold;
        padding-left: 5px;
        padding-right: 5px;
        min-width: 50px;
        max-width: 50px;
        min-height: 13px;
        max-height: 13px;
        }
        """)

class QLineEditCustom( QLineEdit ):
    def __init__(self, contents, parent = None ):
        super(QLineEditCustom, self).__init__( contents, parent = parent )
        self.setStyleSheet("""
        QLineEditCustom {
        background-color: white;
        }
        """)

    def setEnabled(self, val ):
        super(QLineEditCustom, self).setEnabled( val )
        if val:
            self.setStyleSheet("""
            QLineEditCustom {
            background-color: white;
            }
            """)
        else:
            self.setStyleSheet("""
            QLineEditCustom {
            background-color: #DAE9F0;
            }
            """)

def nuke_database_data( ):
    esource = 'nprstuff'
    filename = '%s.conf' % resource
    baseConfDir = xdg.BaseDirectory.save_config_path( resource )
    absPath = os.path.join( baseConfDir, filename )
    if os.path.isfile( absPath ):
        cparser = ConfigParser.ConfigParser()
        cparser.read( absPath )
        if cparser.has_section( 'DATABASE_DATA' ):
            cparser.remove_section( 'DATABASE_DATA' )
            with open( absPath, 'wb' ) as openfile:
                cparser.write( openfile )
            os.chmod( absPath, 0600 )

def push_database_data( email, password ):
    resource = 'nprstuff'
    filename = '%s.conf' % resource
    baseConfDir = xdg.BaseDirectory.save_config_path( resource )
    absPath = os.path.join( baseConfDir, filename )
    if not os.path.isfile( absPath ):
        cparser = ConfigParser.RawConfigParser()
        cparser.set('DATABASE_DATA', 'email', dbEmail )
        cparser.set('DATABASE_DATA', 'password', dbPasswd )
    else:
        cparser = ConfigParser.ConfigParser()
        cparser.read( absPath )
        if cparser.has_section( 'DATABASE_DATA' ):
            cparser.remove_section( 'DATABASE_DATA' )
        cparser.add_section( 'DATABASE_DATA' )
        cparser.set( 'DATABASE_DATA', 'email', email )
        cparser.set( 'DATABASE_DATA', 'password', password )
    with open( absPath, 'wb' ) as openfile:
        cparser.write( openfile )
    os.chmod( absPath, 0600 )

def get_database_data( ):
    resource = 'nprstuff'
    filename = '%s.conf' % resource
    baseConfDir = xdg.BaseDirectory.save_config_path( resource )
    absPath = os.path.join( baseConfDir, filename )
    if not os.path.isfile( absPath ):
        return { 'email' : '', 'password' : '',
                 'message' : "Error, config file does not exist." }

    cparser = ConfigParser.ConfigParser()
    cparser.read( absPath )
    if not cparser.has_section( 'DATABASE_DATA' ):
        return { 'email' : '', 'password' : '',
                 'message' : "Error, config file does not contain DATABASE DATA" }
    email = cparser.get( "DATABASE_DATA", 'email' )
    password = cparser.get( "DATABASE_DATA", "password" )
    url = urljoin('https://tanimislam.ddns.net',
                  '/flask/accounts/checkpassword')
    try:
        response = requests.post( url, json = { 'username' : email,
                                                'password' : password } )
    except Exception as e:
        return { 'email' : '', 'password' : '',
                 'message' : str(e) }
    if response.status_code != 200:
        return { 'email' : '', 'password' : '',
                 'message' : "Error, could not login to database" }
    status = response.json()['data']
    if status == 'NO':
        cparser.remove_section( 'DATABASE_DATA' )
        with open( absPath, 'wb' ) as openfile:
            cparser.write( openfile )
        os.chmod( absPath, 0600 )
        return { 'email' : '', 'password' : '',
                 'message' : "Error, invalid username or password" }
    #
    ## now check that we have actual readability data here
    url = urljoin( 'https://tanimislam.ddns.net',
                   '/flask/api/nprstuff/readability/checkaccount' )
    try:
        response = requests.get( url, auth = ( email, password ) )
    except Exception as e:
        return { 'email' : email, 'password' : password,
                 'message' : str(e) }
    if response.status_code != 200:
        return { 'email' : email, 'password' : password,
                 'message' : "Error, could not login to database" }
    status = response.json()['status']
    if status == 'FAILURE':
        return { 'email' : email, 'password' : password,
                 'message' : "Error, no readability data exists" }
    else:
        return { 'email' : email, 'password' : password,
                 'message' : 'SUCCESS' }


class CustomScrollArea(QScrollArea):
    def __init__(self):
        super(CustomScrollArea, self).__init__()
        #
        toEndAction = QAction(self)
        toEndAction.setShortcut('End')
        toEndAction.triggered.connect( self.scrollToBottom )
        self.addAction( toEndAction )
        #
        toStartAction = QAction(self)
        toStartAction.setShortcut('Home')
        toStartAction.triggered.connect( self.scrollToTop )
        self.addAction( toStartAction )

    def scrollToBottom(self):
        sb = self.verticalScrollBar()
        sb.setValue( sb.maximum() )

    def scrollTopTop(self):
        sb = self.verticalScrollBar()
        sb.setValue( sb.minimum() )
