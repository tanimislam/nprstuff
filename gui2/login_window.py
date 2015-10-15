#!/usr/bin/env python

import os, sys, requests
from urlparse import urljoin
from gui_common import push_database_data, get_database_data, QLineEditCustom, QPushButtonCustom
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class LoginWindow(QWidget):
    def __init__(self, statusdict, parent = None):
        super(LoginWindow, self).__init__()
        self.myParent = parent
        self.setWindowTitle("LOGIN SCREEN")
        #
        self.dbEmailLineEdit = QLineEditCustom("", self)
        self.dbPasswdLineEdit = QLineEditCustom("", self)
        self.rdEmailLineEdit = QLineEditCustom("", self)
        self.rdPasswdLineEdit = QLineEditCustom("", self)
        self.dbPasswdLineEdit.setEchoMode( QLineEdit.Password )
        self.rdPasswdLineEdit.setEchoMode( QLineEdit.Password )
        #
        self.actionButton = QPushButtonCustom("Action!")
        self.actionButton.clicked.connect( self.pushAction )
        #
        self.chooseCreate = QRadioButton("Create Accounts", self)
        self.chooseJustRead = QRadioButton("Just Login", self)
        button_group = QButtonGroup(self)
        button_group.addButton( self.chooseCreate )
        button_group.addButton( self.chooseJustRead )
        self.chooseCreate.toggled.connect( self.chooseStateCreate )
        self.chooseJustRead.toggled.connect( self.chooseStateJustRead )
        self.chooseJustRead.toggle()
        #
        self.statusLabel = QLabel("COULD NOT FIND DB USERNAME AND PASSWORD")
        #
        ## layout
        mainLayout = QVBoxLayout()
        dialogWidget = QWidget()
        buttonWidget = QWidget()
        statusWidget = QWidget()
        self.setLayout( mainLayout )
        mainLayout.addWidget( dialogWidget )
        mainLayout.addWidget( buttonWidget )
        mainLayout.addWidget( statusWidget )
        #
        dialogLayout = QGridLayout()        
        dialogWidget.setLayout( dialogLayout )
        dialogWidget.setStyleSheet("""
        QWidget {
        background-color: #E5EDE9;
        }
        """)
        dialogLayout.addWidget( QLabel("DB email"), 0, 0, 1, 1)
        dialogLayout.addWidget( self.dbEmailLineEdit, 0, 1, 1, 3)
        dialogLayout.addWidget( QLabel("DB passwd"), 1, 0, 1, 1)
        dialogLayout.addWidget( self.dbPasswdLineEdit, 1, 1, 1, 3)
        dialogLayout.addWidget( QLabel("RD email"), 2, 0, 1, 1)
        dialogLayout.addWidget( self.rdEmailLineEdit, 2, 1, 1, 3)
        dialogLayout.addWidget( QLabel("RD passwd"), 3, 0, 1, 1)
        dialogLayout.addWidget( self.rdPasswdLineEdit, 3, 1, 1, 3)
        #
        buttonLayout = QGridLayout( )
        buttonWidget.setLayout( buttonLayout )
        buttonWidget.setStyleSheet("""
        QWidget {
        background-color: #EDE6CE;
        }
        """)
        buttonLayout.addWidget( self.chooseCreate, 0, 0, 1, 1)
        buttonLayout.addWidget( self.chooseJustRead, 0, 1, 1, 1)
        buttonLayout.addWidget( self.actionButton, 0, 2, 1, 1)        
        #
        statusLayout = QHBoxLayout()
        statusWidget.setLayout( statusLayout )
        statusWidget.setStyleSheet("""
        QWidget {
        background-color: #EDDFEB;
        font-size: 12px;
        font-weight: bold;
        }
        """)
        statusLayout.addWidget( self.statusLabel )
        #
        exitAction = QAction(self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect( qApp.quit )
        self.addAction( exitAction )
        mySize = self.sizeHint()            
        self.resize( mySize.width(), mySize.height() )
        self.setFixedWidth( mySize.width() )
        self.setFixedHeight( mySize.height() )
        #
        ## now check to see if we have non-null emails and passwords
        # assert(statusdict['message'] != 'SUCCESS' )        
        self.statusLabel.setText( statusdict['message'] )
        if statusdict['message'] == 'SUCCESS':
            return
        if statusdict['email'] != '':
            self.dbEmailLineEdit.setEnabled( False )
            self.dbPasswdLineEdit.setEnabled( False )
            self.dbEmailLineEdit.setText( statusdict['email'] )
            self.dbPasswdLineEdit.setText( statusdict['password'] )
            self.chooseJustRead.setEnabled( False )
            self.chooseCreate.toggle()
        self.show()
        
    def pushAction(self):
        #
        ## sanitize inputs
        dbEmail = str(self.dbEmailLineEdit.text()).strip()
        self.dbEmailLineEdit.setText( dbEmail )
        dbPasswd = str(self.dbPasswdLineEdit.text()).strip()
        self.dbPasswdLineEdit.setText( dbPasswd )

        if self.dbEmailLineEdit.isEnabled():
            #
            ## check if valid password
            url = urljoin('https://tanimislam.ddns.net',
                          '/flask/accounts/checkpassword')
            try:
                response = requests.post( url, json = { 'username' : dbEmail,
                                                        'password' : dbPasswd } )
            except Exception:
                self.statusLabel.setText( "ERROR, COULD NOT CHECK DB UNAME/PASSWD")
                return
            if response.status_code != 200:
                self.statusLabel.setText( "ERROR, COULD NOT CHECK DB UNAME/PASSWD")
                return
            status = response.json()['data']
            if status == 'NO':
                self.statusLabel.setText( "ERROR, BAD DB UNAME/PASSWD" )
                self.dbEmailLineEdit.setText( "" )
                self.dbPasswdLineEdit.setText( "" )
                return
            #
            ## now put in the DB username and password
            push_database_data( dbEmail, dbPasswd )
            
        # first check that we have created the account
        #
        ## sanitize inputs
        rdEmail = str(self.rdEmailLineEdit.text()).strip()
        self.rdEmailLineEdit.setText( rdEmail )
        rdPasswd = str(self.rdPasswdLineEdit.text()).strip()
        self.rdPasswdLineEdit.setText( rdPasswd )
        if self.chooseCreate.isChecked():
            #
            ## check that this is a good email/password combo
            url = urljoin( 'https://tanimislam.ddns.net',
                           '/flask/api/nprstuff/readability/checkuser' )
            try:
                response = requests.post( url, json = { 'readability_email' : rdEmail,
                                                        'readability_password' : rdPasswd })
            except Exception:
                self.statusLabel.setText("ERROR, COULD NOT CHECK READABILITY UNAME/PASSWD")
                return
            if response.status_code != 200:
                self.statusLabel.setText("ERROR, COULD NOT CHECK READABILITY UNAME/PASSWD")
                return
            status = response.json()['status']
            if status == 'FAILURE':
                self.statusLabel.setText("ERROR, BAD READABILITY UNAME/PASSWD COMBO")
                self.rdEmailLineEdit.setText( "" )
                self.rdPasswdLineEdit.setText( "" )
                return
            #
            ## now create the user
            url = urljoin( 'https://tanimislam.ddns.net',
                           '/flask/api/nprstuff/readability/createuser' )
            response = requests.post( url, json = { 'readability_email' : rdEmail,
                                                    'readability_password' : rdPasswd,
                                                    'no_check_user' : 1 },
                                      auth = ( dbEmail, dbPasswd ) )
            if response.status_code != 200:
                self.statusLabel.setText("ERROR, COULD NOT CREATE READABILITY ACCOUNT")
                return
            self.statusLabel.setText("SUCCESS, CREATED USER")
            self.hide()
            return
        else:  # implies that we have username and password already defined
            #
            ## check that we already have a readability account
            url = urljoin( 'https://tanimislam.ddns.net',
                           '/flask/api/nprstuff/readability/checkaccount' )
            try:
                response = requests.get( url, auth = ( dbEmail, dbPasswd ) )
            except Exception:
                self.statusLabel.setText("ERROR, COULD NOT CHECK READABILITY ACCOUNT")
                return
            if response.status_code != 200:
                self.statusLabel.setText("ERROR, COULD NOT CHECK READABILITY ACCOUNT")
                return
            status = response.json()['status']
            if status == 'FAILURE':
                self.statusLabel.setText("ERROR, NEED TO CREATE READABILITY ACCOUNT")
                self.chooseCreate.toggle()
                return
            self.statusLabel.setText("SUCCESS, FOUND USER")
            self.hide()
            return
            
    def chooseStateCreate( self, enabled ):
        if enabled:
            self.rdEmailLineEdit.setEnabled( True )
            self.rdPasswdLineEdit.setEnabled( True )

    def chooseStateJustRead( self, enabled ):
        if enabled:
            self.rdEmailLineEdit.setEnabled( False )
            self.rdPasswdLineEdit.setEnabled( False )

if __name__=='__main__':
    statusdict = get_database_data( )
    print 'message = %s' % statusdict['message']
    qApp = QApplication( sys.argv )
    lw = LoginWindow( statusdict )
    sys.exit( qApp.exec_() )
