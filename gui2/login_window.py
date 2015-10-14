#!/usr/bin/env python

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class LoginWindow(QWidget):
    def __init__(self, parent):
        super(LoginWindow, self).__init__()
        self.myParent = parent
        #
        self.dbEmailLineEdit = QLineEdit()
        self.dbPasswdLineEdit = QLineEdit()
        self.rdEmailLineEdit = QLineEdit()
        self.rdPasswdLineEdit = QLineEdit()
        #
        self.actionButton = QPushButton("Action!")
        #
        self.chooseCreate = QRadioButton("Create Accounts", self)
        self.chooseJustRead = QRadioButton("Just Login", self)
        button_group = QButtonGroup(self)
        button_group.add( self.chooseCreate )
        button_group.add( self.chooseJustRead )
        self.chooseCreate.toggled.connect( self.chooseStateCreate )
        self.chooseJustRead.toggled.connect( self.chooseStateJustRead )
        self.chooseJustRead.setChecked(True)
        #
        ## layout
        layout = QVBoxLayout()

    def chooseStateCreate( self, enabled ):
        if enabled:
            self.rdEmailLineEdit.enable()
            self.rdPasswdLineEdit.enable()

    def chooseStateJustRead( self, enabled ):
        if enabled:
            self.rdEmailLineEdit.disable()
            self.rdPasswdLineEdit.disable()
