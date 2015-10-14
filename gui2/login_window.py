#!/usr/bin/env python

import os, sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class LoginWindow(QWidget):
    def __init__(self, parent = None, showFrame = True):
        super(LoginWindow, self).__init__()
        self.myParent = parent
        self.setWindowTitle("LOGIN SCREEN")
        #
        self.dbEmailLineEdit = QLineEdit("")
        self.dbPasswdLineEdit = QLineEdit("")
        self.rdEmailLineEdit = QLineEdit("")
        self.rdPasswdLineEdit = QLineEdit("")
        self.dbPasswdLineEdit.setEchoMode( QLineEdit.Password )
        self.rdPasswdLineEdit.setEchoMode( QLineEdit.Password )
        for qle in ( self.dbEmailLineEdit, self.dbPasswdLineEdit,
                     self.rdEmailLineEdit, self.rdPasswdLineEdit):
            qle.setStyleSheet("""
            QLineEdit {
            background-color: white;
            }
            """)
        #
        self.actionButton = QPushButton("Action!")
        self.actionButton.setStyleSheet("""
        QPushButton {
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
        #
        if showFrame:
            mySize = self.sizeHint()            
            self.addAction( exitAction )
            self.resize( mySize.width(), mySize.height() )
            self.setFixedWidth( mySize.width() )
            self.setFixedHeight( mySize.height() )
            self.show()
        
    def pushAction(self):
        text = "CLICKED!"
        if self.chooseCreate.isChecked():
            text = "%s CREATE ACCOUNT!" % text
        else:
            text = "%s ONLY LOGIN!" % text
        self.statusLabel.setText(text)
        

            
    def chooseStateCreate( self, enabled ):
        if enabled:
            self.rdEmailLineEdit.setEnabled( True )
            self.rdPasswdLineEdit.setEnabled( True )
            self.rdEmailLineEdit.setStyleSheet( """
            QLineEdit { 
            background-color: white;            
            }
            """)
            self.rdPasswdLineEdit.setStyleSheet("""
            QLineEdit { 
            background-color: white;           
            }
            """)

    def chooseStateJustRead( self, enabled ):
        if enabled:
            self.rdEmailLineEdit.setEnabled( False )
            self.rdPasswdLineEdit.setEnabled( False )
            self.rdEmailLineEdit.setStyleSheet( """
            QLineEdit { 
            background-color: #DAE9F0;       
            }
            """)
            self.rdPasswdLineEdit.setStyleSheet("""
            QLineEdit { 
            background-color: #DAE9F0;           
            }
            """)

if __name__=='__main__':
    qApp = QApplication( sys.argv )
    lw = LoginWindow()
    sys.exit( qApp.exec_() )
